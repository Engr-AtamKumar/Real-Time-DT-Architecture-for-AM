"""Threshold-based monitoring of model outputs stored in TimescaleDB (Layer 3).

Reads the most recent predictions, logs threshold crossings to the table `alerts`,
and optionally sends an e-mail notification. In the paper this mechanism is a
demonstration only: the targets used are not validated health indicators.
All credentials come from environment variables (see .env.example).
"""
import os
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText

import pandas as pd
from sqlalchemy import create_engine

DB_URL = os.environ["DT_DB_URL"]
TABLE = os.environ.get("PRED_TABLE", "predictions")
COLUMN = os.environ.get("PRED_COLUMN", "prediction")
THRESHOLD = float(os.environ.get("ALERT_THRESHOLD", "0.9"))
DIRECTION = os.environ.get("ALERT_DIRECTION", "above")      # "above" or "below"
LIMIT = int(os.environ.get("ALERT_LOOKBACK_ROWS", "100"))

engine = create_engine(DB_URL)
df = pd.read_sql(f'SELECT timestamp, "{COLUMN}" FROM {TABLE} ORDER BY timestamp DESC LIMIT {LIMIT}', engine)
hit = df[df[COLUMN] > THRESHOLD] if DIRECTION == "above" else df[df[COLUMN] < THRESHOLD]

if hit.empty:
    print("No threshold crossings.")
else:
    hit = hit.copy()
    hit["alert_time"] = datetime.now(timezone.utc)
    hit.to_sql("alerts", engine, if_exists="append", index=False)
    print(f"{len(hit)} threshold crossings logged to table 'alerts'.")
    sender, pwd, receiver = (os.environ.get(k) for k in ("SMTP_USER", "SMTP_PASSWORD", "ALERT_RECEIVER"))
    if sender and pwd and receiver:
        body = "\n".join(f"{r[COLUMN]:.3f} at {r['timestamp']}" for _, r in hit.head(20).iterrows())
        msg = MIMEText("Threshold crossings:\n" + body)
        msg["Subject"], msg["From"], msg["To"] = "DT threshold alert", sender, receiver
        with smtplib.SMTP_SSL(os.environ.get("SMTP_HOST", "smtp.gmail.com"), 465) as s:
            s.login(sender, pwd)
            s.sendmail(sender, receiver, msg.as_string())
        print("E-mail notification sent.")
