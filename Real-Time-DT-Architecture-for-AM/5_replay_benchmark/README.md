# Replay benchmark

Measures end-to-end latency, per-stage latency, throughput, message loss and duplicates, synchronization error, and Grafana query time of the DT pipeline for 1, 5, 10, 20, and 40 virtual printers. Each virtual printer replays a 120-s window of a recorded 10-minute printing segment (76 events/s) at its original timing through MQTT → Node-RED → TimescaleDB → Grafana. A full run takes about 20–30 minutes.

## Requirements

* Docker Desktop (or Docker Engine with Compose).
* The replay segment `replay_segment_session17.csv` in `data/` (available on request, see `../data/README.md`).
* Free host ports 11883 (MQTT), 15432 (TimescaleDB), 11880 (Node-RED), and 13000 (Grafana).

## Run

```bash
docker compose up -d --build      # build and start the stack
docker compose ps                 # all four services should be running
docker compose run --rm bench     # run all scenarios; prints DONE at the end
docker compose down -v            # stop and remove the stack
```

To run only some scenarios: `docker compose run --rm -e SCENARIOS=1,5,10,20 bench`.

During the run, the dashboard "Prusa i3 MK3S Digital Twin (replay benchmark)" is available at http://localhost:13000 and the Node-RED flow at http://localhost:11880. The default credentials in `docker-compose.yml` are for local use only.

## Outputs (`results/`)

* `benchmark_summary.csv` – one row per scenario (offered rate, throughput, loss, latency percentiles, stage latencies, synchronization error, Grafana query time).
* `latency_samples_XX_printers.csv` – per-message timestamps of each scenario.
* `grafana_probe.csv` – dashboard query latency, sampled every 5 s.
* `fig_benchmark.*`, `grafana_dashboard.png`, `nodered_flow.png` – figures; `figbench.py` recreates the benchmark figure.

## Troubleshooting

* No rows reach TimescaleDB: check `docker compose logs nodered`.
* A port is already in use: stop the container or service that occupies it, or change the host port in `docker-compose.yml`.
