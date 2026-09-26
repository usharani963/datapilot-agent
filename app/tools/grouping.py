import pandas as pd


def group_by_analysis(
    df: pd.DataFrame,
    group_column: str,
    value_column: str,
    operation: str = "mean"
) -> dict:

    if group_column not in df.columns:

        return {
            "error": (
                f"Column '{group_column}' does not exist."
            )
        }

    if value_column not in df.columns:

        return {
            "error": (
                f"Column '{value_column}' does not exist."
            )
        }

    if not pd.api.types.is_numeric_dtype(
        df[value_column]
    ):

        return {
            "error": (
                f"Column '{value_column}' must be numeric."
            )
        }

    allowed_operations = {
        "mean",
        "sum",
        "max",
        "min"
    }

    if operation not in allowed_operations:

        return {
            "error": (
                f"Unsupported operation '{operation}'. "
                f"Use mean, sum, max or min."
            )
        }

    grouped = (
        df.groupby(group_column)[value_column]
        .agg(operation)
        .sort_values(ascending=False)
    )

    results = {
        str(index): round(float(value), 4)
        for index, value in grouped.items()
    }

    return {
        "group_column": group_column,
        "value_column": value_column,
        "operation": operation,
        "results": results
    }