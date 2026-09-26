from app.tools.data_info import get_dataset_info
from app.tools.statistics import calculate_statistics
from app.tools.grouping import group_by_analysis
from app.tools.correlation import calculate_correlation
from app.tools.filtering import filter_data
from app.tools.visualization import prepare_bar_chart_data


TOOLS = {
    "dataset_info": get_dataset_info,
    "statistics": calculate_statistics,
    "group_by": group_by_analysis,
    "correlation": calculate_correlation,
    "filter": filter_data,
    "visualization": prepare_bar_chart_data,
}