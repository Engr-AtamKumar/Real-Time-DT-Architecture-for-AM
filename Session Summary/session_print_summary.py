import pandas as pd
import numpy as np

FILE = (
    r"C:\My Personal Documents\Masters Thesis\Thesis Papers"
    r"\Paper 1\Results\features_engineered_revised.csv"
)

df = pd.read_csv(FILE)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce",
    utc=True
)

df = (
    df.sort_values("timestamp")
      .reset_index(drop=True)
)

# ------------------------------------------------------------
# SESSION SUMMARY
# ------------------------------------------------------------

summary = (
    df.groupby("session_id")
      .agg(
          start=("timestamp", "min"),
          end=("timestamp", "max"),
          records=("timestamp", "size"),
          duration_hours=("session_elapsed_hours", "max"),

          hotend_mean=("T_Hotend_Actual", "mean"),
          hotend_std=("T_Hotend_Actual", "std"),

          bed_mean=("T_Bed_Actual", "mean"),
          bed_std=("T_Bed_Actual", "std"),

          hotend_power_mean=("Power_Hotend", "mean"),
          hotend_power_std=("Power_Hotend", "std"),

          bed_power_mean=("Power_Bed", "mean"),
          bed_power_std=("Power_Bed", "std"),

          extrusion_start=("E_Setpoint", "first"),
          extrusion_end=("E_Setpoint", "last"),

          feedrate_mean=("F_Setpoint", "mean"),

          stepper_on_fraction=("StepperOnOff", "mean"),

          active_fraction=("is_active", "mean")
      )
      .reset_index()
)

# ------------------------------------------------------------
# CUMULATIVE OPERATING HISTORY
# ------------------------------------------------------------

summary["extrusion_increment"] = (
    summary["extrusion_end"]
    -
    summary["extrusion_start"]
)

summary["cumulative_extrusion_end"] = (
    summary["extrusion_end"]
)

summary["cumulative_operating_hours"] = (
    summary["duration_hours"].cumsum()
)

# ------------------------------------------------------------
# SESSION ORDER
# ------------------------------------------------------------

summary["session_order"] = (
    np.arange(len(summary))
)

# ------------------------------------------------------------
# EXCLUDE VERY SHORT SESSION FLAG
# ------------------------------------------------------------

summary["short_session"] = (
    summary["duration_hours"] < 1.0
)

# ------------------------------------------------------------
# PRINT CLEAN TABLE
# ------------------------------------------------------------

columns = [
    "session_id",
    "session_order",
    "start",
    "end",
    "records",
    "duration_hours",
    "hotend_mean",
    "hotend_std",
    "bed_mean",
    "bed_std",
    "hotend_power_mean",
    "bed_power_mean",
    "extrusion_start",
    "extrusion_end",
    "extrusion_increment",
    "cumulative_operating_hours",
    "feedrate_mean",
    "stepper_on_fraction",
    "active_fraction",
    "short_session"
]

print("=" * 120)
print("FINAL SESSION HISTORY TABLE")
print("=" * 120)

print(
    summary[columns].to_string(index=False)
)

# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

OUTPUT = (
    r"C:\My Personal Documents\Masters Thesis\Thesis Papers"
    r"\Paper 1\Results\session_summary_revised.csv"
)

summary[columns].to_csv(
    OUTPUT,
    index=False
)

print("\nSaved:")
print(OUTPUT)

print("\n" + "=" * 120)
print("COMPLETE")
print("=" * 120)