# Session Summary and Operating History

This directory contains the script and output dataset used to generate a session-level summary of the processed telemetry data collected from the additive-manufacturing system.

The session summary provides a compact representation of individual printer operating sessions and their associated operational characteristics.

---

## Overview

The high-frequency telemetry dataset contains millions of timestamped observations collected from the additive-manufacturing system.

To support data exploration, session-aware analysis, and predictive experiments, the telemetry observations are grouped according to their assigned:

```text
session_id
```

The session-level summary aggregates the telemetry data and provides information about:

- session timing;
- number of observations;
- operating duration;
- temperature characteristics;
- power characteristics;
- extrusion history;
- cumulative operating time;
- feed-rate behavior;
- stepper activity;
- machine activity;
- short-session identification.

The summary is generated from the feature-engineered telemetry dataset.

---

# Files

## `session_print_summary.py`

This Python script generates a session-level summary from the feature-engineered telemetry dataset.

The script performs the following main steps:

```text
Feature-Engineered Telemetry Data
        |
        v
Timestamp Processing
        |
        v
Chronological Sorting
        |
        v
Grouping by Session ID
        |
        v
Session-Level Aggregation
        |
        v
Cumulative Operating History
        |
        v
Short-Session Identification
        |
        v
Session Summary CSV
```

The script reads:

```text
features_engineered_revised.csv
```

and generates:

```text
session_summary_revised.csv
```

The script groups the processed telemetry data by `session_id` and calculates operational statistics for each session. :contentReference[oaicite:0]{index=0}

---

## `session_summary_revised.csv`

This file contains the final session-level summary generated from the feature-engineered telemetry dataset.

The dataset contains:

- **23 identified telemetry sessions**
- **9,679,191 telemetry observations**
- approximately **114.31 cumulative operating hours**
- **1 session identified as a short session**

Each row represents one telemetry session.

---

# Session Summary Variables

## Session Identification and Timing

### `session_id`

Unique identifier assigned to each telemetry session.

---

### `session_order`

Chronological order of the session within the dataset.

The sessions are ordered according to their temporal sequence.

---

### `start`

Timestamp representing the beginning of the telemetry session.

---

### `end`

Timestamp representing the end of the telemetry session.

---

### `records`

Number of telemetry observations contained within the session.

---

### `duration_hours`

Total duration of the session in hours.

The duration is calculated using the elapsed time between the beginning of the session and its final recorded observation.

---

# Temperature Statistics

## `hotend_mean`

Mean actual hotend temperature during the session.

---

## `hotend_std`

Standard deviation of the actual hotend temperature during the session.

This variable describes the variation in hotend temperature during operation.

---

## `bed_mean`

Mean actual bed temperature during the session.

---

## `bed_std`

Standard deviation of the actual bed temperature during the session.

---

# Power Statistics

## `hotend_power_mean`

Mean hotend power measurement during the session.

---

## `bed_power_mean`

Mean bed power measurement during the session.

The session summary script also calculates the corresponding standard deviations during aggregation, although the final exported summary focuses on the selected reporting variables. :contentReference[oaicite:1]{index=1}

---

# Extrusion History

## `extrusion_start`

Extrusion setpoint value at the beginning of the session.

---

## `extrusion_end`

Extrusion setpoint value at the end of the session.

---

## `extrusion_increment`

The change in extrusion setpoint during the session.

It is calculated as:

```text
extrusion_increment =
extrusion_end − extrusion_start
```

---

## `cumulative_operating_hours`

Cumulative operating duration calculated across the chronologically ordered sessions.

This variable represents the accumulated duration of the identified operating sessions.

---

# Process and Activity Variables

## `feedrate_mean`

Mean feed-rate setpoint during the session.

---

## `stepper_on_fraction`

Fraction of observations during which the stepper-motor status indicates activity.

---

## `active_fraction`

Fraction of observations identified as active according to the activity variable generated during feature engineering.

---

# Short Session Flag

## `short_session`

Boolean indicator used to identify sessions with a duration of less than one hour.

The script defines:

```text
short_session = duration_hours < 1.0
```

This flag can be used to identify unusually short telemetry sessions for further inspection or exclusion during specific analytical procedures. :contentReference[oaicite:2]{index=2}

---

# Session-Level Aggregation

The session summary is generated by grouping the telemetry dataset according to:

```text
session_id
```

For each session, the script calculates variables including:

- minimum timestamp;
- maximum timestamp;
- number of records;
- session duration;
- mean and standard deviation of hotend temperature;
- mean and standard deviation of bed temperature;
- mean and standard deviation of hotend power;
- mean and standard deviation of bed power;
- initial extrusion value;
- final extrusion value;
- mean feed rate;
- fraction of stepper activity;
- fraction of machine activity. :contentReference[oaicite:3]{index=3}

---

# Cumulative Operating History

The script additionally derives operational-history variables.

These include:

```text
extrusion_increment
```

which represents the difference between the final and initial extrusion values within a session, and:

```text
cumulative_operating_hours
```

which accumulates session durations across the chronologically ordered dataset. :contentReference[oaicite:4]{index=4}

---

# Relationship to the Predictive Experiments

The session summary provides important information for the predictive analytics component of the repository.

The session-level information supports:

- identification of operating sessions;
- inspection of session durations;
- chronological ordering of sessions;
- identification of short sessions;
- session-aware data preparation;
- train-test assignment at the session level;
- within-session and cross-session evaluation.

The general relationship is:

```text
Raw / Cleaned Telemetry
        |
        v
Feature Engineering
        |
        v
Session Identification
        |
        v
Session Summary
        |
        +--------------------+
        |                    |
        v                    v
Experiment A          Experiment B
Within-Session         Cross-Session
Evaluation            Evaluation
```

---

# Reproducibility

The session-summary workflow can be reproduced using the following sequence:

```text
cleaned_printer_data.csv
        |
        v
01_feature_engineering.py
        |
        v
features_engineered_revised.csv
        |
        v
session_print_summary.py
        |
        v
session_summary_revised.csv
```

The script expects the feature-engineered dataset as its input and saves the final session-level summary as a CSV file. :contentReference[oaicite:5]{index=5} :contentReference[oaicite:6]{index=6}

---

# Repository Structure

```text
src/
└── preprocessing/
    ├── 01_feature_engineering.py
    └── session_print_summary.py

results/
└── session_summary/
    ├── README.md
    └── session_summary_revised.csv
```

> **Note:** In the final repository organization, the Python script may be placed under `src/preprocessing/`, while the generated CSV output is stored under `results/session_summary/`.

---

# Important Interpretation Note

The session summary is a data-organization and exploratory-analysis component.

A telemetry session represents a temporally grouped period of recorded machine operation.

The identification of sessions and the summary statistics should not automatically be interpreted as:

- machine degradation states;
- failure cycles;
- component-health trajectories;
- run-to-failure experiments.

The session structure is primarily used to organize the telemetry data and support session-aware analytical evaluation.

---

# Related Components

The following repository components are directly related to this session summary:

```text
data/
├── raw/
│   └── cleaned_printer_data.csv
│
└── processed/
    └── features_engineered_revised.csv

src/
└── preprocessing/
    ├── 01_feature_engineering.py
    └── session_print_summary.py

results/
└── session_summary/
    └── session_summary_revised.csv
```
