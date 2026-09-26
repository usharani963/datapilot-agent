import os

import pandas as pd
import matplotlib.pyplot as plt


def prepare_bar_chart_data(
    df: pd.DataFrame,
    category_column: str,
    value_column: str
) -> dict:

    # --------------------------------------------------
    # Validate columns
    # --------------------------------------------------

    if category_column not in df.columns:
        return {
            "error": f"Column '{category_column}' not found."
        }

    if value_column not in df.columns:
        return {
            "error": f"Column '{value_column}' not found."
        }

    # --------------------------------------------------
    # Select required columns
    # --------------------------------------------------

    data = df[
        [category_column, value_column]
    ].copy()

    # Convert numeric column
    data[value_column] = pd.to_numeric(
        data[value_column],
        errors="coerce"
    )

    # Remove invalid rows
    data = data.dropna(
        subset=[
            category_column,
            value_column
        ]
    )

    if data.empty:
        return {
            "error": "No valid data available for visualization."
        }

    # --------------------------------------------------
    # Group data
    # --------------------------------------------------

    grouped = (
        data
        .groupby(category_column)[value_column]
        .mean()
        .sort_values(ascending=False)
    )

    # --------------------------------------------------
    # Create output directory
    # --------------------------------------------------

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    # --------------------------------------------------
    # Create chart
    # --------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    grouped.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        f"Average {value_column} by {category_column}"
    )

    ax.set_xlabel(
        category_column
    )

    ax.set_ylabel(
        f"Average {value_column}"
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.tight_layout()

    # --------------------------------------------------
    # Save chart
    # --------------------------------------------------

    filename = (
        f"{category_column}_"
        f"{value_column}_bar_chart.png"
    )

    filepath = os.path.join(
        "outputs",
        filename
    )

    plt.savefig(
        filepath,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close(fig)

    # --------------------------------------------------
    # Return result
    # --------------------------------------------------

    return {
        "chart_type": "bar",

        "category_column":
            category_column,

        "value_column":
            value_column,

        "chart_path":
            filepath,

        "grouped_results": {
            str(index): round(
                float(value),
                4
            )
            for index, value
            in grouped.items()
        }
    }