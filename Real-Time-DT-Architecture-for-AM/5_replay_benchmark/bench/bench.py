"""
Replay benchmark for the real-time Digital Twin pipeline
MQTT (Mosquitto) -> Node-RED -> TimescaleDB -> Grafana

Replays a recorded 10-minute event segment of the Prusa i3 MK3S (session 17,
76 events/s, printing phase) at its ORIGINAL timing for N virtual printers in
parallel and measures, per scenario:
  * end-to-end latency (MQTT publish -> row committed in TimescaleDB)
  * stage latencies (publish -> Node-RED, Node-RED -> DB)
  * message loss and duplicates (sequence numbers)
  * sustained database insert throughput
  * temporal fidelity ("synchronization error"): deviation between the
    inter-event timing stored in the twin and the original recorded timing
  * Grafana query latency and data age at display (via the Grafana HTTP API)
All containers share the Docker host clock, so timestamps are comparable.
"""
import json, os, sys, time, threading, statistics, csv, math, random
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import psycopg2
import requests
import paho.mqtt.client as mqtt

SEGMENT = os.environ.get("SEGMENT", "/data/replay_segment_session17.csv")
OUT = "/results"
SCENARIOS = [int(x) for x in os.environ.get("SCENARIOS", "1,5,10,20,40").split(",")]
DURATION = float(os.environ.get("DURATION", "120"))      # seconds of replay per scenario
BROKER, BPORT = "mosquitto", 1883
PG = dict(host="timescaledb", user="dt", password="dtbench", dbname="printer")
GRAFANA = "http://grafana:3000"
FIELDS = ["T_Ambient_Actual", "T_Pinda_Actual", "T_Bed_Setpoint", "Power_Bed", "T_Bed_Actual",
          "Speed_Fan_Hotend", "Speed_Fan_Part", "PWM_Fan_Hotend", "PWM_Fan_Part",
          "T_Hotend_Setpoint", "Power_Hotend", "T_Hotend_Actual", "T_Tool_Actual",
          "T_Tool_Setpoint", "StepperOnOff", "X_Setpoint", "Y_Setpoint", "Z_Setpoint",
          "E_Setpoint", "F_Setpoint"]

os.makedirs(OUT, exist_ok=True)


def log(*a):
    print(datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def pg():
    return psycopg2.connect(**PG)


# ---------------------------------------------------------------- data
def load_segment():
    d = pd.read_csv(SEGMENT)
    t = pd.to_datetime(d["timestamp"], utc=True, format="ISO8601")
    t_orig = (t - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds().to_numpy()
    off = t_orig - t_orig[0]
    recs = []
    vals = d[FIELDS].to_numpy()
    for i in range(len(d)):
        row = {FIELDS[k]: float(vals[i, k]) for k in range(len(FIELDS)) if not math.isnan(vals[i, k])}
        recs.append((off[i], t_orig[i], row))
    return recs


# ---------------------------------------------------------------- readiness
def wait_ready():
    log("Waiting for pipeline (MQTT -> Node-RED -> TimescaleDB) ...")
    for _ in range(60):
        try:
            c = pg(); c.close(); break
        except Exception:
            time.sleep(2)
    cl = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="bench-probe")
    cl.connect(BROKER, BPORT); cl.loop_start()
    deadline = time.time() + 120
    while time.time() < deadline:
        now = time.time()
        cl.publish("printer/0/telemetry", json.dumps({"run_id": "probe", "printer_id": 0, "seq": int(now * 1000),
                                                     "t_orig": now, "t_pub": now, "T_Hotend_Actual": 1.0}), qos=1)
        time.sleep(3)
        c = pg(); cur = c.cursor()
        cur.execute("SELECT count(*) FROM telemetry WHERE run_id='probe'")
        n = cur.fetchone()[0]; c.close()
        if n > 0:
            log("Pipeline is ready (probe rows arrived:", n, ")")
            cl.loop_stop(); cl.disconnect()
            return True
    cl.loop_stop()
    log("ERROR: no rows reached TimescaleDB within 120 s.")
    log("Open http://localhost:1880 (Node-RED) and check the 'error log' in the debug sidebar,")
    log("then send a screenshot. Also run: docker compose logs nodered")
    return False


# ---------------------------------------------------------------- publisher
class Printer(threading.Thread):
    def __init__(self, pid, run_id, recs, start_wall, start_off, stats):
        super().__init__(daemon=True)
        self.pid, self.run_id, self.recs, self.t0, self.stats = pid, run_id, recs, start_wall, stats
        # each virtual printer replays a different 2-minute window of the segment
        offs = np.array([r[0] for r in recs])
        self.i0 = int(np.searchsorted(offs, start_off))
        self.off0 = offs[self.i0]

    def run(self):
        cl = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"printer-{self.run_id}-{self.pid}")
        cl.max_inflight_messages_set(1000)
        cl.max_queued_messages_set(0)
        cl.connect(BROKER, BPORT, keepalive=60)
        cl.loop_start()
        seq, pace_err = 0, []
        i = self.i0
        while i < len(self.recs):
            off, t_orig, row = self.recs[i]
            rel = off - self.off0
            if rel > DURATION:
                break
            sched = self.t0 + rel
            dt = sched - time.time()
            if dt > 0:
                time.sleep(dt)
            t_pub = time.time()
            msg = dict(row)
            msg.update(run_id=self.run_id, printer_id=self.pid, seq=seq, t_orig=t_orig, t_pub=t_pub)
            cl.publish(f"printer/{self.pid}/telemetry", json.dumps(msg), qos=1)
            pace_err.append(t_pub - sched)
            seq += 1
            i += 1
        time.sleep(2)
        cl.loop_stop(); cl.disconnect()
        self.stats[self.pid] = dict(published=seq, pace_err=pace_err)


# ---------------------------------------------------------------- grafana probe
PANEL_SQL = ("SELECT time_bucket('1 second', time) AS time, avg(t_hotend) AS actual, avg(t_hotend_sp) AS setpoint "
             "FROM telemetry WHERE $__timeFilter(time) AND printer_id = 1 AND t_hotend IS NOT NULL GROUP BY 1 ORDER BY 1")
AGE_SQL = "SELECT extract(epoch from (now() - max(t_db))) AS age FROM telemetry"


def grafana_query(sql, fmt="time_series"):
    body = {"from": "now-5m", "to": "now",
            "queries": [{"refId": "A", "datasource": {"uid": "tsdb"}, "rawSql": sql, "format": fmt, "rawQuery": True}]}
    t = time.time()
    r = requests.post(f"{GRAFANA}/api/ds/query", json=body, auth=("admin", "admin"), timeout=30)
    return (time.time() - t) * 1000, r


class GrafanaProbe(threading.Thread):
    def __init__(self, run_id, n, rows):
        super().__init__(daemon=True); self.run_id, self.n, self.rows = run_id, n, rows; self.stop = False

    def run(self):
        while not self.stop:
            try:
                ms, r = grafana_query(PANEL_SQL)
                ms2, r2 = grafana_query(AGE_SQL, "table")
                age = None
                try:
                    age = r2.json()["results"]["A"]["frames"][0]["data"]["values"][0][0]
                except Exception:
                    pass
                self.rows.append(dict(run_id=self.run_id, printers=self.n, t=time.time(), panel_query_ms=ms,
                                      status=r.status_code, age_query_ms=ms2, data_age_s=age))
            except Exception as e:
                self.rows.append(dict(run_id=self.run_id, printers=self.n, t=time.time(), panel_query_ms=None,
                                      status=str(e)[:60], age_query_ms=None, data_age_s=None))
            time.sleep(5)  # = dashboard refresh interval


# ---------------------------------------------------------------- analysis
def pct(a, p):
    return float(np.percentile(a, p)) if len(a) else float("nan")


def analyse(run_id, n, stats, probe_rows):
    c = pg(); cur = c.cursor()
    cur.execute("""SELECT printer_id, seq, t_orig, t_pub, t_nr, extract(epoch from t_db)
                   FROM telemetry WHERE run_id=%s""", (run_id,))
    d = pd.DataFrame(cur.fetchall(), columns=["pid", "seq", "t_orig", "t_pub", "t_nr", "t_db"]).astype(float)
    cur.execute("SELECT hypertable_size('telemetry')"); size = cur.fetchone()[0]
    c.close()
    published = sum(s["published"] for s in stats.values())
    uniq = d.drop_duplicates(["pid", "seq"])
    dup = len(d) - len(uniq)
    lost = published - len(uniq)
    e2e = (uniq.t_db - uniq.t_pub).to_numpy() * 1000
    s1 = (uniq.t_nr - uniq.t_pub).to_numpy() * 1000
    s2 = (uniq.t_db - uniq.t_nr).to_numpy() * 1000
    span = uniq.t_db.max() - uniq.t_db.min() if len(uniq) else float("nan")
    fid = []
    for pid, g in uniq.sort_values(["pid", "seq"]).groupby("pid"):
        dev = (g.t_db - g.t_db.iloc[0]) - (g.t_orig - g.t_orig.iloc[0])
        fid.append(dev.abs().to_numpy() * 1000)
    fid = np.concatenate(fid) if fid else np.array([])
    pace = np.concatenate([np.array(s["pace_err"]) for s in stats.values()]) * 1000
    pr = pd.DataFrame([r for r in probe_rows if r["run_id"] == run_id])
    pq = pr.panel_query_ms.dropna().to_numpy() if len(pr) else np.array([])
    ages = pr.data_age_s.dropna().astype(float).to_numpy() if len(pr) else np.array([])
    row = dict(printers=n, run_id=run_id, duration_s=DURATION, offered_msgs=published,
               offered_rate_msg_s=published / DURATION, stored_unique=len(uniq), duplicates=dup,
               lost=lost, loss_pct=100 * lost / published if published else float("nan"),
               throughput_rows_s=len(uniq) / span if span and span > 0 else float("nan"),
               e2e_p50_ms=pct(e2e, 50), e2e_p95_ms=pct(e2e, 95), e2e_p99_ms=pct(e2e, 99), e2e_max_ms=float(e2e.max()) if len(e2e) else float("nan"),
               mqtt_to_nodered_p50_ms=pct(s1, 50), mqtt_to_nodered_p95_ms=pct(s1, 95),
               nodered_to_db_p50_ms=pct(s2, 50), nodered_to_db_p95_ms=pct(s2, 95),
               sync_err_p50_ms=pct(fid, 50), sync_err_p95_ms=pct(fid, 95), sync_err_p99_ms=pct(fid, 99),
               publisher_pacing_p95_ms=pct(pace, 95),
               grafana_query_p50_ms=pct(pq, 50), grafana_query_p95_ms=pct(pq, 95),
               data_age_at_display_p50_s=pct(ages, 50), data_age_at_display_p95_s=pct(ages, 95),
               db_size_mb=size / 1e6)
    smp = pd.DataFrame({"printers": n, "e2e_ms": e2e, "mqtt_to_nodered_ms": s1, "nodered_to_db_ms": s2})
    if len(smp) > 20000:
        smp = smp.sample(20000, random_state=0)
    smp.to_csv(f"{OUT}/latency_samples_{n:02d}_printers.csv", index=False)
    return row


# ---------------------------------------------------------------- main
def main():
    recs = load_segment()
    seg_len = recs[-1][0]
    log(f"Loaded segment: {len(recs)} events, {seg_len:.0f} s, {len(recs) / seg_len:.1f} events/s")
    if not wait_ready():
        sys.exit(1)
    results, probe_rows = [], []
    for n in SCENARIOS:
        run_id = f"N{n:02d}_{int(time.time())}"
        log(f"=== Scenario: {n} virtual printer(s), {DURATION:.0f} s, offered ~{n * len(recs) / seg_len:.0f} msg/s ===")
        stats = {}
        start = time.time() + 3
        rnd = random.Random(n)
        ths = [Printer(p, run_id, recs, start + rnd.random(), (p * 37.0) % max(1.0, seg_len - DURATION - 1), stats)
               for p in range(1, n + 1)]
        probe = GrafanaProbe(run_id, n, probe_rows)
        probe.start()
        for t in ths:
            t.start()
        for t in ths:
            t.join()
        # drain: wait until row count stops growing
        last, stable = -1, 0
        for _ in range(90):
            c = pg(); cur = c.cursor()
            cur.execute("SELECT count(*) FROM telemetry WHERE run_id=%s", (run_id,))
            cnt = cur.fetchone()[0]; c.close()
            stable = stable + 1 if cnt == last else 0
            last = cnt
            if stable >= 5:
                break
            time.sleep(1)
        probe.stop = True; probe.join(timeout=10)
        r = analyse(run_id, n, stats, probe_rows)
        results.append(r)
        log(f"   offered {r['offered_rate_msg_s']:.0f} msg/s | stored {r['stored_unique']}/{r['offered_msgs']} "
            f"(loss {r['loss_pct']:.3f}%) | e2e p50 {r['e2e_p50_ms']:.1f} ms p95 {r['e2e_p95_ms']:.1f} ms | "
            f"sync err p95 {r['sync_err_p95_ms']:.1f} ms | Grafana p95 {r['grafana_query_p95_ms']:.0f} ms")
        pd.DataFrame(results).to_csv(f"{OUT}/benchmark_summary.csv", index=False)
        pd.DataFrame(probe_rows).to_csv(f"{OUT}/grafana_probe.csv", index=False)
        time.sleep(10)
    with open(f"{OUT}/environment.txt", "w") as f:
        f.write(f"finished {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"segment {SEGMENT}: {len(recs)} events over {seg_len:.1f} s\n")
        f.write(f"scenarios {SCENARIOS}, duration {DURATION} s each, MQTT QoS 1, Node-RED per-message INSERT\n")
        f.write(f"cpu_count_in_bench_container {os.cpu_count()}\n")
    log("DONE. Results in ./results  -> benchmark_summary.csv, grafana_probe.csv, latency_samples_*.csv")


if __name__ == "__main__":
    main()
