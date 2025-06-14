import hydra
from typing import Optional
from omegaconf import DictConfig, OmegaConf
from .models import ProjectConfig, ForumConfig, FinancialAPIConfig

_config: Optional[DictConfig] = None

# def get_config() -> DictConfig:
#     global _config
#     # If the configuration is not already loaded, initialize and compose it
#     if _config is None:
#         try:
#             with hydra.initialize(config_path="."):
#                 _config = hydra.compose(config_name="config.yaml")
#         except Exception as e:
#             logging.error(f"Error loading configuration: {e}")
#             raise
#     return _config

# config = get_config()

# cfg = Optional[DictConfig] = None

# @hydra.main(config_path=".", config_name="config")
# @hydra.main(config_path="config", config_name="config")
def get_config():
    # Convert relevant config sections to Pydantic models
    with hydra.initialize(config_path="."):
        cfg = hydra.compose(config_name="config.yaml")
    project = ProjectConfig(**cfg.project)
    forum = ForumConfig(**cfg.forum)
    api = FinancialAPIConfig(**cfg.financial_api)
    companies_suffix = cfg.get("company_suffixes", None)
    return project, forum, api, companies_suffix

# Usage example (from any script):
# from config import get_config
project_cfg, forum_cfg, api_cfg, companies_suffix = get_config()
