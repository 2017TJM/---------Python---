from __future__ import annotations
import pandas as pd
from typing import Optional


def preprocess_dataframe(
	df: pd.DataFrame,
	date_column: Optional[str] = None,
	amount_column: Optional[str] = None,
	drop_duplicates: bool = True,
	fill_missing: Optional[str] = "median",
	normalize_columns: bool = True,
	treat_blank_as_na: bool = True,
	outlier_strategy: str = "none",
) -> pd.DataFrame:
	clean = df.copy()

	# Normalize columns: strip and lower
	if normalize_columns:
		clean.columns = [str(c).strip().lower() for c in clean.columns]
		# also normalize provided column names to match
		if date_column:
			date_column = date_column.strip().lower()
		if amount_column:
			amount_column = amount_column.strip().lower()

	# Treat blank as NA
	if treat_blank_as_na:
		clean = clean.apply(lambda s: s.mask(s.astype(str).str.strip().eq("")))

	# Parse dates
	if date_column and date_column in clean.columns:
		clean[date_column] = pd.to_datetime(clean[date_column], errors="coerce")

	# Drop duplicates
	if drop_duplicates:
		clean = clean.drop_duplicates()

	# Fill missing values for amount
	if fill_missing and amount_column and amount_column in clean.columns:
		if fill_missing == "zero":
			clean[amount_column] = clean[amount_column].fillna(0)
		elif fill_missing == "mean":
			clean[amount_column] = clean[amount_column].fillna(clean[amount_column].mean())
		elif fill_missing == "median":
			clean[amount_column] = clean[amount_column].fillna(clean[amount_column].median())
		# if 'none', do nothing

	# Outlier handling for amount via IQR clipping
	if outlier_strategy == "iqr" and amount_column and amount_column in clean.columns:
		col = pd.to_numeric(clean[amount_column], errors="coerce")
		q1 = col.quantile(0.25)
		q3 = col.quantile(0.75)
		iqr = q3 - q1
		if pd.notna(iqr) and iqr > 0:
			lower = q1 - 1.5 * iqr
			upper = q3 + 1.5 * iqr
			clean[amount_column] = col.clip(lower=lower, upper=upper)
		else:
			clean[amount_column] = col

	return clean
