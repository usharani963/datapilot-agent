import pandas as pd

from app.tools.data_info import get_dataset_info
from app.tools.statistics import calculate_statistics
from app.tools.grouping import group_by_analysis
from app.tools.correlation import calculate_correlation


df = pd.read_csv("data/sample.csv")

print("\nDATASET INFO")
print(get_dataset_info(df))

print("\nSTATISTICS")
print(calculate_statistics(df, "yield"))

print("\nGROUP BY")
print(
    group_by_analysis(
        df,
        "state",
        "yield",
        "mean"
    )
)

print("\nCORRELATION")
print(
    calculate_correlation(
        df,
        "rainfall",
        "yield"
    )
)