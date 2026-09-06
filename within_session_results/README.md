# Experiment A: Within-Session Chronological Evaluation

This directory contains the results and data-splitting information associated with **Experiment A**, which evaluates the proof-of-concept predictive analytics pipeline using a **within-session chronological train-test split**.

> **Important:** The predictive target used in this experiment is a synthetic session-progress proxy. It is not a physical Remaining Useful Life (RUL) measurement, degradation indicator, component-health measurement, or failure prediction target.

---

## Experiment Overview

Experiment A evaluates whether relationships learned from earlier observations within an operating session can be used to predict the synthetic session-progress proxy for later observations from the same session.

The telemetry data are processed chronologically within each operating session.

For every usable session:

```text
Earlier observations
        |
        v
Training subset
        |
        |
        | chronological boundary
        |
        v
Later observations
        |
        v
Testing subset
```

Observations are not randomly shuffled.

The evaluation therefore preserves the temporal ordering of telemetry observations within each operating session.

---

# Dataset Split

## `within_session_split_summary.csv`

This file documents the chronological training and testing split applied to each operating session.

The file contains **22 operating sessions** and provides the following information for each session:

| Column | Description |
|---|---|
| `session_id` | Unique identifier of the operating session |
| `total_rows` | Total number of telemetry observations in the session |
| `train_rows` | Number of observations used for model training |
| `test_rows` | Number of observations used for testing |
| `train_progress_min` | Minimum synthetic session-progress value in the training subset |
| `train_progress_max` | Maximum synthetic session-progress value in the training subset |
| `test_progress_min` | Minimum synthetic session-progress value in the testing subset |
| `test_progress_max` | Maximum synthetic session-progress value in the testing subset |

The dataset contains:

- **22 operating sessions**
- **9,679,157 total telemetry observations**
- **6,775,401 training observations**
- **2,903,756 testing observations**

Each session is split chronologically, meaning that earlier observations are assigned to training and later observations are assigned to testing.

Because the duration and number of observations vary across operating sessions, the exact progress boundary differs between sessions.

---

# Model Results

## `within_session_model_results.csv`

This file contains the overall predictive performance results for the evaluated models and reference baselines.

The following approaches were evaluated.

### Reference Baselines

- Training Mean Baseline
- Midpoint Baseline

### Machine-Learning Models

- Linear Regression
- Ridge Regression
- Decision Tree
- Random Forest
- Extra Trees
- Gradient Boosting
- Histogram Gradient Boosting
- XGBoost

The inclusion of baseline models is important for determining whether the machine-learning models provide predictive performance beyond simple constant-reference predictions.

---

# Evaluation Metrics

The model results include the following metrics.

| Metric | Description |
|---|---|
| `R` | Pearson correlation coefficient between predictions and actual target values |
| `R2` | Coefficient of determination |
| `MAE` | Mean Absolute Error |
| `MSE` | Mean Squared Error |
| `RMSE` | Root Mean Squared Error |
| `EVS` | Explained Variance Score |
| `Error_Variance` | Variance of the prediction errors |
| `Prediction_Value` | Constant prediction value used by the reference baseline, where applicable |

---

## Pearson Correlation Coefficient (`R`)

Measures the linear association between the predicted values and the actual target values.

Values closer to:

```text
+1  -> strong positive association
 0  -> little or no linear association
-1  -> strong negative association
```

---

## Coefficient of Determination (`R²`)

Measures how well the predictions explain variation in the target.

Negative values indicate that the predictive model performs worse than an appropriate constant-reference prediction.

---

## Mean Absolute Error (`MAE`)

Measures the average absolute difference between predicted and actual values.

Lower values indicate smaller average prediction errors.

---

## Mean Squared Error (`MSE`)

Measures the average squared difference between predicted and actual values.

Larger prediction errors receive greater weight because the errors are squared.

---

## Root Mean Squared Error (`RMSE`)

The square root of the Mean Squared Error.

This metric provides prediction error in the same scale as the target variable.

---

## Explained Variance Score (`EVS`)

Measures the proportion of variation in the target that is explained by the predictions.

---

# Interpretation of Experiment A

Experiment A is a **within-session evaluation**.

This means that observations from the same operating sessions contribute to both the training and testing datasets, although the temporal ordering is preserved.

The experiment therefore evaluates whether predictive relationships learned from earlier portions of sessions extend to later portions of those same sessions.

This evaluation is useful as a diagnostic analysis, but it does not provide the same level of generalization testing as evaluation on completely unseen operating sessions.

For this reason, the results should be interpreted together with **Experiment B**, which uses complete session-level separation between training and testing data.

---

# Important Limitation

The target used in this experiment is a:

```text
synthetic session-progress proxy
```

The target represents the relative temporal position of an observation within an operating session.

Conceptually:

```text
Session Start                              Session End
     |-------------------------------------------|
     0                                           1
```

This target is not equivalent to:

- Remaining Useful Life (RUL);
- physical degradation;
- component health;
- machine failure probability;
- predictive-maintenance effectiveness.

Therefore, the predictive results should not be interpreted as validated prognostic or RUL prediction results.

---

# Why Experiment A Was Performed

Experiment A was designed to provide a diagnostic evaluation of the predictive analytics pipeline under a chronological within-session split.

The experiment helps investigate:

- whether temporal ordering is preserved during evaluation;
- whether relationships learned from earlier telemetry observations extend to later observations;
- how machine-learning models behave within operating sessions;
- how model performance compares with simple reference baselines.

The experiment also provides a comparison point for the stricter **cross-session evaluation performed in Experiment B**.

---

# Relationship to Experiment B

The two experiments use different evaluation strategies.

## Experiment A

```text
Session 1
[ Training observations | Testing observations ]

Session 2
[ Training observations | Testing observations ]

Session 3
[ Training observations | Testing observations ]
```

Observations from the same session can appear in both training and testing subsets.

---

## Experiment B

```text
Training Sessions
Session 1
Session 2
Session 3
Session ...
        |
        v
Model Training
        |
        v
Previously Unseen Test Sessions
Session ...
Session ...
Session ...
```

Complete operating sessions are separated between training and testing.

Experiment B therefore provides the primary evaluation of cross-session generalization.

---

# Files in This Directory

```text
experiment_a/
├── README.md
├── within_session_split_summary.csv
└── within_session_model_results.csv
```

---

# Reproducibility

The general workflow for Experiment A is:

```text
Processed Telemetry Data
        |
        v
Session Identification
        |
        v
Synthetic Session-Progress Target
        |
        v
Chronological Split Within Each Session
        |
        +-----------------------+
        |                       |
        v                       v
Earlier Observations       Later Observations
Training Data               Testing Data
        |
        v
Machine-Learning Models
        |
        v
Model Predictions
        |
        v
Performance Evaluation
        |
        v
Experiment A Results
```

The corresponding preprocessing and Experiment A scripts are provided in the source-code section of the repository.

---

# Related Repository Components

```text
src/
├── preprocessing/
│   ├── 01_feature_engineering.py
│   └── 02_session_summary.py
│
└── experiment_a/
    └── experiment_a.py

results/
├── experiment_a/
│   ├── README.md
│   ├── within_session_split_summary.csv
│   └── within_session_model_results.csv
│
└── experiment_b/
    └── ...
```

---

# Important Research Context

Experiment A should be interpreted as a **proof-of-concept evaluation of the predictive analytics component** within the broader Real-Time Digital Twin Architecture.

The experiment does not establish validated:

- Remaining Useful Life prediction;
- prognostic capability;
- degradation prediction;
- failure prediction;
- predictive-maintenance effectiveness.

Future research requires physically meaningful degradation indicators, component-health measurements, and run-to-failure data to develop and validate a genuine prognostic capability.
