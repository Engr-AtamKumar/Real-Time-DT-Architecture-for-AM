# ============================================================
# REVISED FEATURE ENGINEERING PIPELINE
# Digital Twin / Additive Manufacturing
# ============================================================

import pandas as pd
import numpy as np
from scipy.stats import zscore

# ============================================================
# 1. FILE PATHS
# ============================================================

INPUT_FILE = (
    r"C:\My Personal Documents\Masters Thesis\Thesis Papers"
    r"\Paper 1\Results\cleaned_printer_data.csv"
)

OUTPUT_FILE = (
    r"C:\My Personal Documents\Masters Thesis\Thesis Papers"
    r"\Paper 1\Results\features_engineered_revised.csv"
)

# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 80)
print("REVISED FEATURE ENGINEERING")
print("=" * 80)

print("\nLoading source dataset...")

df = pd.read_csv(INPUT_FILE)

print(
    f"Rows loaded: {len(df):,}"
)

# ============================================================
# 3. TIMESTAMP PROCESSING
# ============================================================

print("\nProcessing timestamps...")

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce",
    utc=True
)

# Remove invalid timestamps
before = len(df)

df = df.dropna(
    subset=["timestamp"]
).copy()

print(
    f"Rows removed due to invalid timestamps: "
    f"{before - len(df):,}"
)

# Sort chronologically
df = (
    df.sort_values("timestamp")
      .reset_index(drop=True)
)

print(
    "Timestamp range:"
)

print(
    df["timestamp"].min()
)

print(
    df["timestamp"].max()
)

# ============================================================
# 4. SESSION DETECTION
# ============================================================
#
# A gap > 10 minutes defines a new telemetry session.
#
# This is a data-organization step, NOT a physical failure
# assumption.
# ============================================================

print("\nDetecting telemetry sessions...")

time_diff = (
    df["timestamp"]
    .diff()
    .dt.total_seconds()
)

SESSION_GAP_SECONDS = 600

df["session_id"] = (
    time_diff > SESSION_GAP_SECONDS
).cumsum()

number_sessions = df["session_id"].nunique()

print(
    f"Detected sessions: {number_sessions}"
)

# ============================================================
# 5. MISSING VALUES
# ============================================================

print("\nHandling missing values...")

# Variables for forward filling
ffill_columns = [
    "T_Ambient_Actual",
    "T_Pinda_Actual",
    "T_Bed_Actual",
    "T_Hotend_Actual",
    "T_Tool_Actual",
    "T_Tool_Setpoint"
]

for col in ffill_columns:

    if col in df.columns:

        df[col] = (
            df.groupby("session_id")[col]
              .ffill()
        )

# Process-related missing values
if "E_Setpoint" in df.columns:

    df["E_Setpoint"] = (
        df.groupby("session_id")["E_Setpoint"]
          .ffill()
          .fillna(0)
    )

# Position/feed-rate variables
fill_zero_columns = [
    "X_Setpoint",
    "Y_Setpoint",
    "Z_Setpoint",
    "F_Setpoint"
]

for col in fill_zero_columns:

    if col in df.columns:

        df[col] = (
            df.groupby("session_id")[col]
              .ffill()
        )

# ============================================================
# 6. TIME FEATURES
# ============================================================

print("\nCreating time features...")

df["hour"] = df["timestamp"].dt.hour

df["dayofweek"] = df["timestamp"].dt.dayofweek

df["minute"] = df["timestamp"].dt.minute

# ============================================================
# 7. MACHINE ACTIVITY
# ============================================================

print("\nCreating machine activity features...")

df["is_active"] = (
    df["E_Setpoint"] > 0
).astype(int)

# Session-level utilization
df["utilization"] = (
    df.groupby("session_id")["is_active"]
      .transform(
          lambda x: x.rolling(
              window=60,
              min_periods=1
          ).mean()
      )
)

# ============================================================
# 8. SMOOTHING
# ============================================================

print("\nCreating smoothed sensor features...")

df["T_Hotend_Actual_Smooth"] = (
    df.groupby("session_id")["T_Hotend_Actual"]
      .transform(
          lambda x: x.rolling(
              window=5,
              min_periods=1
          ).mean()
      )
)

df["Power_Hotend_Smooth"] = (
    df.groupby("session_id")["Power_Hotend"]
      .transform(
          lambda x: x.rolling(
              window=5,
              min_periods=1
          ).mean()
      )
)

# ============================================================
# 9. Z-SCORE FEATURES
# ============================================================
#
# Calculate anomaly scores within each session rather than
# across the entire multi-month dataset.
# ============================================================

print("\nCreating session-level anomaly features...")

def session_zscore(series):

    std = series.std()

    if pd.isna(std) or std == 0:

        return pd.Series(
            0.0,
            index=series.index
        )

    return (
        (series - series.mean()) / std
    )


df["hotend_zscore"] = (
    df.groupby("session_id")["T_Hotend_Actual"]
      .transform(session_zscore)
)

df["power_zscore"] = (
    df.groupby("session_id")["Power_Hotend"]
      .transform(session_zscore)
)

# ============================================================
# 10. ELAPSED TIME WITHIN SESSION
# ============================================================

print("\nCreating session elapsed time...")

df["session_elapsed_seconds"] = (
    df["timestamp"]
    -
    df.groupby("session_id")["timestamp"]
      .transform("min")
).dt.total_seconds()

df["session_elapsed_hours"] = (
    df["session_elapsed_seconds"] / 3600.0
)

# ============================================================
# 11. SESSION SUMMARY
# ============================================================

print("\nSession summary:")

session_summary = (
    df.groupby("session_id")
      .agg(
          start=("timestamp", "min"),
          end=("timestamp", "max"),
          records=("timestamp", "size"),
          duration_hours=(
              "session_elapsed_hours",
              "max"
          )
      )
)

print(
    session_summary.to_string()
)

# ============================================================
# 12. DATA QUALITY CHECK
# ============================================================

print("\nData quality check...")

print(
    "Rows:",
    f"{len(df):,}"
)

print(
    "Columns:",
    len(df.columns)
)

print(
    "Duplicate rows:",
    df.duplicated().sum()
)

print(
    "Duplicate timestamps:",
    df["timestamp"].duplicated().sum()
)

print(
    "Missing values:",
    df.isna().sum().sum()
)

# ============================================================
# 13. SAVE
# ============================================================

print("\nSaving revised feature dataset...")

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"Saved to:\n{OUTPUT_FILE}"
)

# ============================================================
# 14. FINAL
# ============================================================

print("\n" + "=" * 80)
print("FEATURE ENGINEERING COMPLETE")
print("=" * 80)

print(
    "\nIMPORTANT:"
)

print(
    "No RUL_simulated target was created."
)

print(
    "The synthetic prognostics target will be defined "
    "after reviewing the session structure."
)

print("=" * 80)