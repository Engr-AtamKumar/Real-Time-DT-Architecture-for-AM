import os
# Paths: set DT_DATA_DIR to the folder holding the (on-request) dataset; outputs go to DT_RESULTS_DIR.
DATA_DIR = os.environ.get("DT_DATA_DIR", "data")
RESULTS_DIR = os.environ.get("DT_RESULTS_DIR", "results")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


# ============================================================
# LOAD CORRELATION RESULTS
# ============================================================

file_path = (
    os.path.join(RESULTS_DIR, "windowed_results/feature_target_correlations.csv")
)

corr_df = pd.read_csv(file_path)


# ============================================================
# SELECT TOP 15 FEATURES BY ABSOLUTE PEARSON CORRELATION
# ============================================================

top_n = 15

top_features = (
    corr_df
    .sort_values("Abs_Pearson_R", ascending=False)
    .head(top_n)
    .copy()
)


# ============================================================
# CREATE HUMAN-READABLE FEATURE LABELS
# ============================================================

feature_labels = {

    # --------------------------------------------------------
    # POSITION VARIABLES
    # --------------------------------------------------------
    "Z_Setpoint_min": "Z-axis setpoint (min)",
    "Z_Setpoint_mean": "Z-axis setpoint (mean)",
    "Z_Setpoint_max": "Z-axis setpoint (max)",

    "Y_Setpoint_std": "Y-axis setpoint (std)",
    "Y_Setpoint_min": "Y-axis setpoint (min)",

    "X_Setpoint_max": "X-axis setpoint (max)",
    "X_Setpoint_mean": "X-axis setpoint (mean)",

    # --------------------------------------------------------
    # HOTEND SETPOINT
    # --------------------------------------------------------
    "T_Hotend_Setpoint_max": "Hotend setpoint (max)",
    "T_Hotend_Setpoint_mean": "Hotend setpoint (mean)",
    "T_Hotend_Setpoint_min": "Hotend setpoint (min)",

    # --------------------------------------------------------
    # TOOL SETPOINT
    # --------------------------------------------------------
    "T_Tool_Setpoint_max": "Tool setpoint (max)",
    "T_Tool_Setpoint_mean": "Tool setpoint (mean)",
    "T_Tool_Setpoint_min": "Tool setpoint (min)",

    # --------------------------------------------------------
    # BED SETPOINT
    # --------------------------------------------------------
    "T_Bed_Setpoint_max": "Bed setpoint (max)",
    "T_Bed_Setpoint_mean": "Bed setpoint (mean)",
    "T_Bed_Setpoint_min": "Bed setpoint (min)",

    # --------------------------------------------------------
    # BED POWER
    # --------------------------------------------------------
    "Power_Bed_max": "Bed power (max)",
    "Power_Bed_mean": "Bed power (mean)",

    # --------------------------------------------------------
    # OTHER VARIABLES
    # --------------------------------------------------------
    "StepperOnOff_max": "Stepper status (max)",

    "T_Hotend_Actual_max": "Hotend temperature (max)"
}


top_features["Feature_Label"] = (
    top_features["Feature"]
    .map(feature_labels)
    .fillna(top_features["Feature"])
)


# ============================================================
# SORT BY ABSOLUTE CORRELATION
# ============================================================

top_features = (
    top_features
    .sort_values("Abs_Pearson_R", ascending=False)
    .reset_index(drop=True)
)


# ============================================================
# DEFINE SCIENTIFIC DIVERGING COLORS
#
# Positive correlations -> blue
# Negative correlations -> muted orange
#
# Colors are intentionally restrained and suitable for
# scientific publication.
# ============================================================

positive_color = "#2166AC"
negative_color = "#B35806"

bar_colors = np.where(
    top_features["Pearson_R"] >= 0,
    positive_color,
    negative_color
)


# ============================================================
# CREATE FIGURE
# ============================================================

fig, ax = plt.subplots(
    figsize=(10.5, 7.5)
)


# ============================================================
# HORIZONTAL BAR CHART
# ============================================================

bars = ax.barh(
    top_features["Feature_Label"],
    top_features["Pearson_R"],
    color=bar_colors,
    edgecolor="none",
    height=0.78
)


# ============================================================
# ZERO REFERENCE LINE
# ============================================================

ax.axvline(
    x=0,
    color="black",
    linewidth=0.9,
    zorder=0
)


# ============================================================
# OPTIONAL LIGHT GRID
#
# Only vertical grid lines are used because the x-axis represents
# the correlation coefficient.
# ============================================================

ax.xaxis.grid(
    True,
    linestyle="--",
    linewidth=0.5,
    alpha=0.35
)

ax.set_axisbelow(True)


# ============================================================
# SYMMETRIC AXIS LIMITS
# ============================================================

max_abs = top_features["Abs_Pearson_R"].max()

padding = 0.06

axis_limit = np.ceil(
    (max_abs + padding) * 10
) / 10

ax.set_xlim(
    -axis_limit,
    axis_limit
)


# ============================================================
# X-AXIS TICKS
# ============================================================

tick_step = 0.1

ticks = np.arange(
    -axis_limit,
    axis_limit + tick_step,
    tick_step
)

ax.set_xticks(ticks)


# ============================================================
# AXIS LABEL
# ============================================================

ax.set_xlabel(
    r"Pearson correlation coefficient ($r$) with session-progress proxy",
    fontsize=12.5
)

# Remove unnecessary y-axis label for a cleaner journal figure
ax.set_ylabel("")


# ============================================================
# ADD CORRELATION VALUES
# ============================================================

text_offset = 0.012

for bar, value in zip(
    bars,
    top_features["Pearson_R"]
):

    y_position = (
        bar.get_y()
        + bar.get_height() / 2
    )

    if value >= 0:

        ax.text(
            value + text_offset,
            y_position,
            f"{value:.3f}",
            va="center",
            ha="left",
            fontsize=10.5
        )

    else:

        ax.text(
            value - text_offset,
            y_position,
            f"{value:.3f}",
            va="center",
            ha="right",
            fontsize=10.5
        )


# ============================================================
# FEATURE ORDER
#
# Highest absolute correlation appears at the top.
# ============================================================

ax.invert_yaxis()


# ============================================================
# LEGEND
# ============================================================

legend_elements = [

    Patch(
        facecolor=positive_color,
        edgecolor="none",
        label="Positive correlation"
    ),

    Patch(
        facecolor=negative_color,
        edgecolor="none",
        label="Negative correlation"
    )
]


ax.legend(
    handles=legend_elements,
    loc="lower right",
    frameon=False,
    fontsize=10
)


# ============================================================
# IMPROVE TYPOGRAPHY
# ============================================================

ax.tick_params(
    axis="x",
    labelsize=11
)

ax.tick_params(
    axis="y",
    labelsize=11.5
)


# ============================================================
# CLEAN SPINES
# ============================================================

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)


# ============================================================
# ADJUST LAYOUT
# ============================================================

plt.tight_layout()


# ============================================================
# SAVE FIGURES
# ============================================================

output_png = (
    os.path.join(RESULTS_DIR, "windowed_results/top_feature_target_correlations.png")
)

output_pdf = (
    os.path.join(RESULTS_DIR, "windowed_results/top_feature_target_correlations.pdf")
)


plt.savefig(
    output_png,
    dpi=600,
    bbox_inches="tight"
)

plt.savefig(
    output_pdf,
    bbox_inches="tight"
)


# ============================================================
# DISPLAY FIGURE
# ============================================================

plt.show()