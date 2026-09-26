import pandas as pd


def calculate_statistics(
    df: pd.DataFrame,
    column: str
) -> dict:

    if column not in df.columns:

        return {
            "error": f"Column '{column}' does not exist."
        }

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):

        return {
            "error": f"Column '{column}' is not numeric."
        }

    series = df[column].dropna()

    if len(series) == 0:

        return {
            "error": f"Column '{column}' contains no usable values."
        }

    return {
        "column": column,
        "count": int(series.count()),
        "mean": round(float(series.mean()), 4),
        "median": round(float(series.median()), 4),
        "minimum": round(float(series.min()), 4),
        "maximum": round(float(series.max()), 4),
        "standard_deviation": round(
            float(series.std()),
            4
        )
    }