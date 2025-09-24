from __future__ import annotations
import pandas as pd
from typing import Optional, List, Dict, Any
from app.schemas.sales import AnalyzeResult, SummaryStats, GroupedStat


_GRANULARITY = {
	"D": "D",
	"W": "W",
	"M": "MS",
	"Q": "QS",
	"Y": "YS",
}


def _maybe_resample_by_date(df: pd.DataFrame, date_column: Optional[str], granularity: Optional[str], amount_column: Optional[str]) -> pd.DataFrame:
	if not date_column or date_column not in df.columns or not granularity:
		return df
	rule = _GRANULARITY.get(granularity)
	if not rule:
		return df
	if amount_column and amount_column in df.columns:
		resampled = (
			df.set_index(pd.DatetimeIndex(df[date_column]))[[amount_column]]
			.resample(rule)
			.sum()
			.reset_index(drop=False)
		)
		resampled.rename(columns={"index": date_column}, inplace=True)
		return resampled
	return df


def _prepare_metrics(metrics: Optional[List[str]]) -> List[str]:
	default = ["sum", "count"]
	if not metrics:
		return default
	allowed = {"sum", "mean", "median", "max", "min", "count"}
	filtered = [m for m in metrics if m in allowed]
	return filtered or default


def basic_analysis(
	df: pd.DataFrame,
	group_by: Optional[List[str]] = None,
	amount_column: Optional[str] = None,
	date_granularity: Optional[str] = None,
	date_column: Optional[str] = None,
	metrics: Optional[List[str]] = None,
) -> AnalyzeResult:
	if df is None or df.empty:
		return AnalyzeResult(
			summary=SummaryStats(rows=0, columns=0),
			groups=[],
		)

	# Optional date resampling - if requested and columns exist
	if date_granularity and date_column:
		try:
			df = _maybe_resample_by_date(df, date_column, date_granularity, amount_column)
		except Exception:
			pass

	# Summary
	if amount_column and amount_column in df.columns:
		amount_sum = float(df[amount_column].sum())
		amount_mean = float(df[amount_column].mean()) if df[amount_column].notna().any() else None
		amount_median = float(df[amount_column].median()) if df[amount_column].notna().any() else None
	else:
		amount_sum = None
		amount_mean = None
		amount_median = None

	summary = SummaryStats(
		rows=int(df.shape[0]),
		columns=int(df.shape[1]),
		amount_sum=amount_sum,
		amount_mean=amount_mean,
		amount_median=amount_median,
	)

	# Grouped metrics
	groups_out: List[GroupedStat] | None = None
	if group_by:
		missing = [g for g in group_by if g not in df.columns]
		if not missing:
			computed_metrics = _prepare_metrics(metrics)
			if amount_column and amount_column in df.columns:
				agg_dict = {}
				for m in computed_metrics:
					if m == "count":
						agg_dict["count"] = (amount_column, "count")
					else:
						agg_dict[m] = (amount_column, m)
				grouped = df.groupby(group_by, dropna=False).agg(**agg_dict).reset_index()
			else:
				# no amount column: only count per group
				grouped = df.groupby(group_by, dropna=False).size().reset_index(name="count")
				computed_metrics = ["count"]

			groups_out = []
			for _, row in grouped.iterrows():
				keys: Dict[str, Any] = {col: row[col] for col in group_by}
				gs = GroupedStat(keys=keys)
				for m in computed_metrics:
					val = row[m] if m in grouped.columns else None
					if pd.isna(val):
						val = None
					if m == "sum":
						gs.total_amount = float(val) if val is not None else None
					elif m == "mean":
						gs.amount_mean = float(val) if val is not None else None
					elif m == "median":
						gs.amount_median = float(val) if val is not None else None
					elif m == "max":
						gs.amount_max = float(val) if val is not None else None
					elif m == "min":
						gs.amount_min = float(val) if val is not None else None
					elif m == "count":
						gs.count = int(val) if val is not None else 0
				groups_out.append(gs)

	return AnalyzeResult(summary=summary, groups=groups_out)
