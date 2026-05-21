from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    huggingface_token: str = Field(..., description="HuggingFace API token (hf_...)")
    hf_model: str = Field(
        default="Qwen/Qwen2.5-7B-Instruct",
        description="HuggingFace Inference API model for generation",
    )
    chroma_persist_dir: str = Field(default="./chroma_db")
    collection_name: str = Field(default="rasaveda_recipes")
    top_k_results: int = Field(default=8)
    recipes_path: str = Field(default="./data/recipes.json")
    admin_password: str = Field(default="rasaveda-admin", description="Password to unlock the recipe editor")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
