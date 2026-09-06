# 3D Printer Dataset Documentation

This dataset contains telemetry data from a Prusa MK3S 3D printer.

## Data Format

The data is provided in CSV format (`datapoint_named_example.csv`). Each row represents a snapshot of the printer's state at a given timestamp.

- Fan PWM: Value between 0 and 255 controlling the fan speed
- Fan Speed: Fan rotation speed in RPM (rotations per minute)

## Columns

The dataset includes the following columns:

- `timestamp`: The date and time of the data point.
- `T_Ambient_Actual`: Ambient temperature in °C.
- `T_Pinda_Actual`: Pinda probe temperature in °C.
- `T_Bed_Setpoint`: Target temperature for the heated bed in °C (parsed from GCode).
- `Power_Bed`: Power consumption of the heated bed in Watts (calculated by measuring DC voltage and current).
- `T_Bed_Actual`: Actual temperature of the heated bed in °C.
- `Speed_Fan_Hotend`: Hotend fan speed.
- `Speed_Fan_Part`: Part cooling fan speed.
- `PWM_Fan_Hotend`: PWM value for the hotend fan.
- `PWM_Fan_Part`: PWM value for the part cooling fan.
- `T_Hotend_Setpoint`: Target temperature for the hotend in °C (parsed from GCode).
- `Power_Hotend`: Power consumption of the hotend and electronics in Watts. This includes power for all logic, fans, control PCB, hotend heater, stepper motors, and drivers (calculated by measuring DC voltage and current).
- `T_Hotend_Actual`: Actual temperature of the hotend in °C.
- `T_Tool_Actual`: Actual temperature of the tool (synonymous with `T_Hotend_Actual`) in °C.
- `T_Tool_Setpoint`: Target temperature for the tool (synonymous with `T_Hotend_Setpoint`) in °C (parsed from GCode).
- `StepperOnOff`: Indicates if the stepper motors are powered on (1) or off (0).
- `X_Setpoint`: Target X-axis position (parsed from GCode).
- `Y_Setpoint`: Target Y-axis position (parsed from GCode).
- `Z_Setpoint`: Target Z-axis position (parsed from GCode).
- `E_Setpoint`: Target extruder position (parsed from GCode).
- `F_Setpoint`: Target feedrate (speed) (parsed from GCode).

## Notes

- All temperatures are in degrees Celsius (°C).
- Power values (`Power_Bed`, `Power_Hotend`) are in Watts (W).
- `Power_Bed` and `Power_Hotend` were calculated by measuring DC voltage and current and then multiplying these values.
- The total power consumption of the printer is the sum of `Power_Bed` and `Power_Hotend`.
- `Power_Hotend` includes the power consumption for all the logic including fans, control PCB, hotend heater, stepper motors and drivers.
- Setpoint values for temperatures and positions are parsed directly from the GCode commands sent to the printer.
- `StepperOnOff` is either 0 or 1 and indicates if steppers are powered on.
- The dataset contains the DC power consumption of the printer.

## Data Information

- PWM fan values range between 0 and 255
- Fan speed is measured in RPM (Revolutions Per Minute)
- The data is not gapfilled (i.e., there may be missing values or time periods in the dataset)

## Data Characteristics

The dataset contains raw sensor measurements without any gap-filling. Missing data points are not interpolated or estimated.

## Data Processing

The data provided in this repository is raw and has not been gapfilled. Any missing values or gaps in the data collection remain as is in the datasets.
