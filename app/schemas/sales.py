from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class AnalyzeParams(BaseModel):
	date_column: Optional[str] = Field(default=None, description="日期列名")
	amount_column: Optional[str] = Field(default=None, description="销售金额列名")
	drop_duplicates: bool = Field(default=True)
	fill_missing: Optional[str] = Field(default="median", description="缺失值填充策略: none|zero|median|mean")
	group_by: Optional[List[str]] = Field(default=None, description="分组列列表，如['region','product']")
	date_granularity: Optional[str] = Field(default=None, description="日期粒度: D|W|M|Q|Y")
	metrics: Optional[List[str]] = Field(default=None, description="聚合指标：sum|mean|median|max|min|count，默认仅返回 sum 与 count")
	# 新增预处理参数
	normalize_columns: bool = Field(default=True, description="标准化列名：去空格并转小写")
	treat_blank_as_na: bool = Field(default=True, description="将空白字符串视为缺失值")
	outlier_strategy: str = Field(default="none", description="异常值处理策略：none|iqr（仅对金额列）")


class SummaryStats(BaseModel):
	rows: int
	columns: int
	amount_sum: Optional[float] = None
	amount_mean: Optional[float] = None
	amount_median: Optional[float] = None


class GroupedStat(BaseModel):
	keys: Dict[str, Any]
	# 指标输出（可选出现）
	total_amount: Optional[float] = None  # sum
	amount_mean: Optional[float] = None
	amount_median: Optional[float] = None
	amount_max: Optional[float] = None
	amount_min: Optional[float] = None
	count: Optional[int] = None


class AnalyzeResult(BaseModel):
	summary: SummaryStats
	groups: Optional[List[GroupedStat]] = None


class PreviewParams(AnalyzeParams):
	limit: int = Field(default=20, ge=1, le=1000, description="预览返回的行数")


class PreviewResult(BaseModel):
	columns: List[str]
	rows: List[Dict[str, Any]]
