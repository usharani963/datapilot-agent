import pandas as pd


def dataset_info(
    df: pd.DataFrame
) -> dict:

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "data_types": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "missing_values": {
            column: int(value)
            for column, value
            in df.isnull().sum().items()
        }
    }


def statistics(
    df: pd.DataFrame,
    column: str
) -> dict:

    if column not in df.columns:

        return {
            "error": f"Column '{column}' not found."
        }

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):

        return {
            "error": (
                f"Column '{column}' is not numeric."
            )
        }

    series = df[column].dropna()

    if series.empty:

        return {
            "error": (
                f"No valid values in '{column}'."
            )
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


def group_by(
    df: pd.DataFrame,
    group_column: str,
    value_column: str,
    operation: str = "mean"
) -> dict:

    if group_column not in df.columns:

        return {
            "error": (
                f"Column '{group_column}' not found."
            )
        }

    if value_column not in df.columns:

        return {
            "error": (
                f"Column '{value_column}' not found."
            )
        }

    data = df.copy()

    data[value_column] = pd.to_numeric(
        data[value_column],
        errors="coerce"
    )

    data = data.dropna(
        subset=[
            group_column,
            value_column
        ]
    )

    if data.empty:

        return {
            "error": "No valid data available."
        }

    grouped = (
        data
        .groupby(group_column)[value_column]
    )

    if operation == "mean":

        result = grouped.mean()

    elif operation == "sum":

        result = grouped.sum()

    elif operation == "max":

        result = grouped.max()

    elif operation == "min":

        result = grouped.min()

    else:

        return {
            "error": (
                f"Unsupported operation: {operation}"
            )
        }

    # -----------------------------------------------------
    # Sort descending
    # -----------------------------------------------------

    result = result.sort_values(
        ascending=False
    )

    # -----------------------------------------------------
    # JSON-safe result
    # -----------------------------------------------------

    grouped_results = {

        str(index): round(
            float(value),
            4
        )

        for index, value
        in result.items()

    }

    # -----------------------------------------------------
    # Highest
    # -----------------------------------------------------

    highest_category = None
    highest_value = None

    if len(result) > 0:

        highest_category = str(
            result.index[0]
        )

        highest_value = round(
            float(result.iloc[0]),
            4
        )

    # -----------------------------------------------------
    # Lowest
    # -----------------------------------------------------

    lowest_category = None
    lowest_value = None

    if len(result) > 0:

        lowest_category = str(
            result.index[-1]
        )

        lowest_value = round(
            float(result.iloc[-1]),
            4
        )

    return {

        "group_column": group_column,

        "value_column": value_column,

        "operation": operation,

        "grouped_results": grouped_results,

        "highest_category": highest_category,

        "highest_value": highest_value,

        "lowest_category": lowest_category,

        "lowest_value": lowest_value

    }


def correlation(
    df: pd.DataFrame,
    column1: str,
    column2: str
) -> dict:

    if column1 not in df.columns:

        return {
            "error": (
                f"Column '{column1}' not found."
            )
        }

    if column2 not in df.columns:

        return {
            "error": (
                f"Column '{column2}' not found."
            )
        }

    data = df[
        [column1, column2]
    ].copy()

    data[column1] = pd.to_numeric(
        data[column1],
        errors="coerce"
    )

    data[column2] = pd.to_numeric(
        data[column2],
        errors="coerce"
    )

    data = data.dropna()

    if len(data) < 2:

        return {
            "error": (
                "Not enough valid data points "
                "for correlation."
            )
        }

    value = data[
        column1
    ].corr(
        data[column2]
    )

    return {

        "column1": column1,

        "column2": column2,

        "correlation": round(
            float(value),
            4
        )

    }


def filter_data(
    df: pd.DataFrame,
    column: str,
    value
) -> dict:

    if column not in df.columns:

        return {
            "error": (
                f"Column '{column}' not found."
            )
        }

    filtered = df[
        df[column].astype(str)
        == str(value)
    ]

    return {

        "column": column,

        "value": str(value),

        "rows": int(
            len(filtered)
        ),

        "data": filtered.to_dict(
            orient="records"
        )

    }