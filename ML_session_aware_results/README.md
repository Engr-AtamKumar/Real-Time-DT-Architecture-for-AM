# Experiment A: Predictive Model Results

This directory contains the result files, evaluation metrics, and session-level information associated with **Experiment A** of the predictive analytics pipeline.

Experiment A evaluates machine-learning models using **observation-level telemetry data** and a **session-aware chronological evaluation procedure**.

> **Important:** The predictive target used in this experiment is a synthetic session-progress proxy. It is not a physical Remaining Useful Life (RUL) measurement, degradation indicator, or failure prediction target.

---

## Experiment Overview

The experiment uses telemetry observations collected from multiple operating sessions.

The evaluation procedure separates complete sessions into training and testing groups:

- **Training sessions:** 17
- **Testing sessions:** 5
- **Total usable sessions:** 22

The session assignments used for the experiment are provided in:

```text
train_test_session_assignment.csv
```

The repository also includes a session summary file containing information about the identified telemetry sessions.

---

## Evaluated Models

The following predictive models and reference baselines were evaluated:

### Baselines

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

Baseline models are included to determine whether the machine-learning models provide predictive information beyond simple constant predictions.

---

# Files

## `model_results_all_metrics.csv`

This file contains the complete overall evaluation metrics for all evaluated models.

The file includes:

- model name;
- number of training observations;
- number of testing observations;
- number of training sessions;
- number of testing sessions;
- Pearson correlation coefficient (`R`);
- coefficient of determination (`R²`);
- Mean Absolute Error (`MAE`);
- Mean Squared Error (`MSE`);
- Root Mean Squared Error (`RMSE`);
- Explained Variance;
- Median Absolute Error;
- Maximum Absolute Error;
- prediction-error statistics;
- prediction distribution statistics;
- actual-target distribution statistics.

This file provides the most complete model-level evaluation output.

---

## `paper_ready_model_metrics.csv`

This file contains the formatted model-performance results prepared for reporting and comparison.

It contains the same main model-level metrics as the complete results file, with values formatted for presentation.

Key metrics include:

- `R`
- `R2`
- `MAE`
- `MSE`
- `RMSE`
- `Explained_Variance`

This file can be used to reproduce summary tables and reported model-comparison results.

---

## `session_averaged_model_performance.csv`

This file provides model performance averaged across the individual test sessions.

For each model, it reports:

- mean session-level correlation (`Session_Mean_R`);
- standard deviation of session-level correlation (`Session_SD_R`);
- mean session-level coefficient of determination (`Session_Mean_R2`);
- standard deviation of session-level coefficient of determination (`Session_SD_R2`);
- mean session-level MAE;
- standard deviation of session-level MAE;
- mean session-level RMSE;
- standard deviation of session-level RMSE.

This file supports evaluation of model behavior across different operating sessions rather than relying only on aggregated test-set performance.

---

## `session_level_test_metrics.csv`

This file contains detailed predictive performance metrics calculated separately for each test session.

Each record represents the performance of one model on one test session.

The file includes:

- model;
- session identifier;
- number of observations;
- correlation coefficient (`R`);
- coefficient of determination (`R²`);
- MAE;
- MSE;
- RMSE;
- Explained Variance;
- Median Absolute Error;
- Maximum Absolute Error;
- prediction-error statistics;
- prediction statistics;
- actual-target statistics.

Because five test sessions and ten models are evaluated, this file contains session-specific performance information for all model-session combinations.

---

## `session_summary_used_for_ML.csv`

This file contains the summary information for the telemetry sessions used during the machine-learning analysis.

The included variables are:

| Column | Description |
|---|---|
| `session_id` | Unique identifier for each telemetry session |
| `start` | Session start timestamp |
| `end` | Session end timestamp |
| `records` | Number of telemetry observations in the session |
| `duration_hours` | Duration of the session in hours |
| `session_order` | Chronological order of the session |
| `short_session` | Indicator identifying short sessions |

This file documents the operating-session structure used in the predictive evaluation.

---

## `train_test_session_assignment.csv`

This file records the assignment of usable operating sessions to the training and testing datasets.

The columns are:

| Column | Description |
|---|---|
| `session_id` | Unique session identifier |
| `split` | Dataset assignment (`train` or `test`) |

The file documents the session-level separation used during the experiment.

This information is important for reproducibility because observations belonging to the same session should not be arbitrarily mixed between training and testing groups.

---

# Evaluation Metrics

The predictive models were evaluated using multiple complementary metrics.

### Pearson Correlation Coefficient (`R`)

Measures the linear association between predicted and actual target values.

### Coefficient of Determination (`R²`)

Measures the proportion of target variance explained by the predictions.

### Mean Absolute Error (`MAE`)

Measures the average absolute difference between predictions and actual values.

### Mean Squared Error (`MSE`)

Measures the average squared prediction error.

### Root Mean Squared Error (`RMSE`)

Provides the square root of the mean squared prediction error.

### Explained Variance

Measures how much variation in the target is explained by the predictions.

Additional error and prediction-distribution statistics are provided in the detailed result files.

---

# Interpretation of Results

The results should be interpreted within the scope of the proof-of-concept predictive analytics pipeline.

The experiment evaluates whether relationships between machine telemetry features and the synthetic session-progress target can be learned under the specified evaluation procedure.

The results do **not** demonstrate:

- validated Remaining Useful Life prediction;
- physical component degradation prediction;
- machine failure prediction;
- validated predictive-maintenance capability.

The experiment is intended to evaluate the integration and analytical behavior of the machine-learning component within the broader Digital Twin architecture.

---

# Reproducibility

The result files in this directory should be used together with the corresponding scripts located in the source-code directories.

The general workflow is:

```text
Telemetry Data
      |
      v
Session Identification
      |
      v
Feature Engineering
      |
      v
Training/Test Session Assignment
      |
      v
Model Training
      |
      v
Model Prediction
      |
      v
Overall and Session-Level Evaluation
      |
      v
CSV Result Files
```

The scripts responsible for reproducing the experiment and generating these result files are provided elsewhere in the repository.

---

## Related Repository Components

Relevant repository directories include:

```text
src/
├── preprocessing/
│   ├── 01_feature_engineering.py
│   └── 02_session_summary.py
│
└── experiment_a/
    └── experiment_a.py

data/
├── raw/
└── processed/

results/
└── experiment_a/
```

---

## Important Limitation

The predictive target used in this experiment is a **synthetic session-progress proxy**.

It should not be interpreted as an experimentally validated measure of:

- remaining useful life;
- component health;
- degradation;
- failure probability.

Future work requires physically meaningful degradation indicators, component-health measurements, and run-to-failure data to support validated prognostic modeling.
