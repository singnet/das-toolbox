from pydantic import BaseModel
from shared.enums.metric_scope import MetricScope

class GetMetricsDto(BaseModel):
    targetIp : str
    metricScope : MetricScope