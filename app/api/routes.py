from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from app.schemas.sales import AnalyzeParams, AnalyzeResult, PreviewParams, PreviewResult
from app.services.preprocess import preprocess_dataframe
from app.services.analyze import basic_analysis
from app.utils.csv_io import read_csv_to_dataframe
from app.db.session import engine
import pandas as pd

api_router = APIRouter()


@api_router.post("/analyze", response_model=AnalyzeResult)
async def analyze_csv(
	file: UploadFile = File(...),
	params_json: Optional[str] = Form(default=None, description="AnalyzeParams 的 JSON 字符串"),
):
	if file.content_type not in ("text/csv", "application/vnd.ms-excel", "application/csv"):
		raise HTTPException(status_code=400, detail="Only CSV files are supported")

	# Parse params from JSON string if provided
	params: Optional[AnalyzeParams] = None
	if params_json:
		try:
			params = AnalyzeParams.model_validate_json(params_json)
		except Exception as exc:
			raise HTTPException(status_code=400, detail=f"Invalid params JSON: {exc}")

	content = await file.read()
	df: pd.DataFrame = read_csv_to_dataframe(content)

	df_clean = preprocess_dataframe(
		df,
		date_column=params.date_column if params else None,
		amount_column=params.amount_column if params else None,
		drop_duplicates=params.drop_duplicates if params else True,
		fill_missing=params.fill_missing if params else "median",
		normalize_columns=params.normalize_columns if params is not None else True,
		treat_blank_as_na=params.treat_blank_as_na if params is not None else True,
		outlier_strategy=params.outlier_strategy if params is not None else "none",
	)

	result = basic_analysis(
		df_clean,
		group_by=params.group_by if params else None,
		amount_column=params.amount_column if params else None,
		date_granularity=params.date_granularity if params else None,
		date_column=params.date_column if params else None,
		metrics=params.metrics if params else None,
	)
	return result


@api_router.post("/preview", response_model=PreviewResult)
async def preview_csv(
	file: UploadFile = File(...),
	params_json: Optional[str] = Form(default=None, description="PreviewParams 的 JSON 字符串"),
):
	if file.content_type not in ("text/csv", "application/vnd.ms-excel", "application/csv"):
		raise HTTPException(status_code=400, detail="Only CSV files are supported")

	# Parse params from JSON string if provided
	params: Optional[PreviewParams] = None
	if params_json:
		try:
			params = PreviewParams.model_validate_json(params_json)
		except Exception as exc:
			raise HTTPException(status_code=400, detail=f"Invalid params JSON: {exc}")

	content = await file.read()
	df: pd.DataFrame = read_csv_to_dataframe(content)

	df_clean = preprocess_dataframe(
		df,
		date_column=params.date_column if params else None,
		amount_column=params.amount_column if params else None,
		drop_duplicates=params.drop_duplicates if params else True,
		fill_missing=params.fill_missing if params else "median",
		normalize_columns=params.normalize_columns if params is not None else True,
		treat_blank_as_na=params.treat_blank_as_na if params is not None else True,
		outlier_strategy=params.outlier_strategy if params is not None else "none",
	)

	limit = params.limit if params else 20
	preview_df = df_clean.head(limit)
	rows = preview_df.to_dict(orient="records")
	columns = list(preview_df.columns)
	return PreviewResult(columns=columns, rows=rows)


@api_router.get("/health")
async def health():
	try:
		with engine.connect() as conn:
			_ = conn.execute("SELECT 1")
		return {"status": "ok"}
	except Exception:
		return {"status": "degraded"}


@api_router.get("/version")
async def version():
	from app.main import app
	return {"name": app.title, "version": app.version}
