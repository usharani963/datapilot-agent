import pandas as pd


def calculate_correlation(
    df: pd.DataFrame,
    column1: str,
    column2: str
) -> dict:

    if column1 not in df.columns:

        return {
            "error": (
                f"Column '{column1}' does not exist."
            )
        }

    if column2 not in df.columns:

        return {
            "error": (
                f"Column '{column2}' does not exist."
            )
        }

    if not pd.api.types.is_numeric_dtype(
        df[column1]
    ):

        return {
            "error": f"{column1} must be numeric."
        }

    if not pd.api.types.is_numeric_dtype(
        df[column2]
    ):

        return {
            "error": f"{column2} must be numeric."
        }

    correlation = (
        df[[column1, column2]]
        .corr()
        .iloc[0, 1]
    )

    if pd.isna(correlation):

        return {
            "error": "Correlation could not be calculated."
        }

    return {
        "column1": column1,
        "column2": column2,
        "pearson_correlation": round(
            float(correlation),
            4
        )
    }