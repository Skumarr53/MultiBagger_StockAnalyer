from pydantic import BaseModel, Field

class ProjectConfig(BaseModel):
    name: str = Field(..., description="Project name")
    data_dir: str = Field(default="./data")
    log_dir: str = Field(default="./logs")

class ForumConfig(BaseModel):
    base_url: str
    update_frequency: str = "weekly"

class FinancialAPIConfig(BaseModel):
    provider: str
    api_key: str
    update_frequency: str = "weekly"
