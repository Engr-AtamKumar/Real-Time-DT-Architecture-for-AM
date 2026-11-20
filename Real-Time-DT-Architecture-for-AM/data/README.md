# Data (available on request)

The telemetry dataset is **not** part of this repository. It was recorded on an instrumented Prusa i3 MK3S in a university laboratory and is available from the corresponding author on reasonable request, subject to the agreement of the data owner.

Contact: Atam Kumar Menghwar, mngtkm01m14z236b@studenti.unical.it

## Expected files (after a granted request)

| File | Used by | Description |
|---|---|---|
| `datapoint_named.csv` | `2_preprocessing/01_clean_event_log.py` | Raw event-based log (10.07 M records), one row per change event |
| `cleaned_printer_data.csv` | `02_feature_engineering.py`, `1_pipeline/replay_printer_data.py` | Cleaned table (9.68 M records) |
| `features_engineered.csv` | `3_experiments/*`, `03_session_summary.py` | Session-aware engineered features (output of step 02) |
| `replay_segment_session17.csv` | `5_replay_benchmark` (copy into `5_replay_benchmark/data/`) | 10-minute event segment used for the benchmark |

## Schema of the telemetry columns

`timestamp`, `T_Ambient_Actual`, `T_Pinda_Actual`, `T_Bed_Setpoint`, `Power_Bed`, `T_Bed_Actual`, `Speed_Fan_Hotend`, `Speed_Fan_Part`, `PWM_Fan_Hotend`, `PWM_Fan_Part`, `T_Hotend_Setpoint`, `Power_Hotend`, `T_Hotend_Actual`, `T_Tool_Actual`, `T_Tool_Setpoint`, `StepperOnOff`, `X_Setpoint`, `Y_Setpoint`, `Z_Setpoint`, `E_Setpoint`, `F_Setpoint`

Temperatures are in °C and power in W; X, Y and Z setpoints are in mm, E is the extruder position in mm, and F is the feed rate in mm/min. `T_Tool_*` duplicates `T_Hotend_*` on this single-extruder printer.
