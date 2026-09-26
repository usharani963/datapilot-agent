import pandas as pd


def filter_data(
    df: pd.DataFrame,
    column: str,
    value: str
) -> dict:

    if column not in df.columns:

        return {
            "error": (
                f"Column '{column}' does not exist."
            )
        }

    filtered = df[
        df[column]
        .astype(str)
        .str.lower()
        == str(value).lower()
    ]

    return {
        "column": column,
        "value": value,
        "rows_found": int(len(filtered)),
        "data": filtered.to_dict(
            orient="records"
        )
    }