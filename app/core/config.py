from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

	app_name: str = "Sales Analytics API"
	debug: bool = True
	# Use sqlite by default to allow running without MySQL driver; override via .env
	database_url: str = "sqlite:///./local.db"


settings = Settings()
