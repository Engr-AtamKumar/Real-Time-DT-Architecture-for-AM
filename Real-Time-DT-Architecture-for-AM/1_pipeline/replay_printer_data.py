"""Original replay script (2025): streams the cleaned telemetry row by row to MQTT and TimescaleDB.
Credentials are read from environment variables (see .env.example)."""
import pandas as pd
import time
import paho.mqtt.client as mqtt
import psycopg2
import json
import math
import os

# 🔧 Utility: Replace NaN/inf with None for JSON compatibility
def sanitize(data):
    for key in data:
        if isinstance(data[key], float) and (math.isnan(data[key]) or math.isinf(data[key])):
            data[key] = 0.0
    return data

# 📂 Load cleaned dataset
df = pd.read_csv(os.path.join(os.environ.get("DT_DATA_DIR", "data"), "cleaned_printer_data.csv"), parse_dates=["timestamp"])

# 🌐 Setup MQTT
mqtt_client = mqtt.Client()
mqtt_client.connect(os.environ.get("MQTT_HOST", "localhost"), int(os.environ.get("MQTT_PORT", "1883")), 60)

# 🛢️ Connect to TimescaleDB
conn = psycopg2.connect(
    host=os.environ.get("PGHOST", "localhost"),
    dbname=os.environ.get("PGDATABASE", "printer"),
    user=os.environ.get("PGUSER", "postgres"),
    password=os.environ["PGPASSWORD"],  # set in your environment, never in code
    port=int(os.environ.get("PGPORT", "5432")),
)
cursor = conn.cursor()

# 🔁 Stream data row by row
for _, row in df.iterrows():
    data = row.to_dict()
    data["timestamp"] = row["timestamp"].isoformat()

    # ✅ Clean invalid floats
    clean_data = sanitize(data)

    # 📤 Send to MQTT
    mqtt_client.publish("printer/data", json.dumps(clean_data))

    # 📝 Insert into TimescaleDB
    cursor.execute("""
        INSERT INTO printer_data (
            timestamp,
            T_Ambient_Actual, T_Pinda_Actual, T_Bed_Setpoint, Power_Bed, T_Bed_Actual,
            Speed_Fan_Hotend, Speed_Fan_Part, PWM_Fan_Hotend, PWM_Fan_Part,
            T_Hotend_Setpoint, Power_Hotend, T_Hotend_Actual,
            T_Tool_Actual, T_Tool_Setpoint, StepperOnOff,
            X_Setpoint, Y_Setpoint, Z_Setpoint, E_Setpoint, F_Setpoint
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (timestamp) DO NOTHING;
    """, (
        row["timestamp"],
        row["T_Ambient_Actual"],
        row["T_Pinda_Actual"],
        row["T_Bed_Setpoint"],
        row["Power_Bed"],
        row["T_Bed_Actual"],
        row["Speed_Fan_Hotend"],
        row["Speed_Fan_Part"],
        row["PWM_Fan_Hotend"],
        row["PWM_Fan_Part"],
        row["T_Hotend_Setpoint"],
        row["Power_Hotend"],
        row["T_Hotend_Actual"],
        row["T_Tool_Actual"],
        row["T_Tool_Setpoint"],
        row["StepperOnOff"],
        row["X_Setpoint"],
        row["Y_Setpoint"],
        row["Z_Setpoint"],
        row["E_Setpoint"],
        row["F_Setpoint"]
    ))
    conn.commit()
    time.sleep(float(os.environ.get("REPLAY_INTERVAL_S", "2")))  # fixed-interval replay (the timing-faithful benchmark is in 5_replay_benchmark)

# 🧹 Clean up
cursor.close()
conn.close()
mqtt_client.disconnect()
