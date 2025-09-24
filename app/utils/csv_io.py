from __future__ import annotations
import io
import pandas as pd


def read_csv_to_dataframe(content: bytes) -> pd.DataFrame:
	# Try utf-8, fallback to gbk commonly used in CN locales
	for enc in ("utf-8", "utf-8-sig", "gbk"):
		try:
			return pd.read_csv(io.BytesIO(content), encoding=enc)
		except UnicodeDecodeError:
			continue
	# As a last resort, let pandas guess
	return pd.read_csv(io.BytesIO(content), encoding_errors="ignore")
