"""Uploads the engineered feature table to TimescaleDB (table: engineered_features).
Database connection is read from the environment (see .env.example)."""
import os
import pandas as pd
from sqlalchemy import create_engine

DATA_DIR = os.environ.get("DT_DATA_DIR", "data")
DB_URL = os.environ["DT_DB_URL"]  # e.g. postgresql+psycopg2://user:password@localhost:5432/printer

df = pd.read_csv(os.path.join(DATA_DIR, "features_engineered.csv"))
print(f"Loaded engineered dataset: {len(df)} rows")
engine = create_engine(DB_URL)
df.to_sql("engineered_features", engine, if_exists="replace", index=False, chunksize=100000)
print("Uploaded to TimescaleDB table: engineered_features")
