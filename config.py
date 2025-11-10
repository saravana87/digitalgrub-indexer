"""
Configuration management for DigitalGrub Indexer
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="digitalgrub", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="", alias="DB_PASSWORD")
    
    # Azure OpenAI Configuration
    azure_openai_api_key: str = Field(default="", alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_embedding_deployment: str = Field(
        default="text-embedding-ada-002",
        alias="AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview",
        alias="AZURE_OPENAI_API_VERSION"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    
    # Embedding Configuration
    embedding_provider: Literal["azure", "openai", "local"] = Field(
        default="azure", 
        alias="EMBEDDING_PROVIDER"
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL"
    )
    local_embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        alias="LOCAL_EMBEDDING_MODEL"
    )
    
    # LlamaIndex Configuration
    chunk_size: int = Field(default=1024, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")
    
    # PgVector Configuration
    vector_dimension: int = Field(default=384, alias="VECTOR_DIMENSION")
    vector_table_prefix: str = Field(
        default="llamaindex_embedding",
        alias="VECTOR_TABLE_PREFIX"
    )
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="", alias="LOG_FILE")
    
    # Application Settings
    app_name: str = Field(default="DigitalGrub Indexer", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    
    # LlamaIndex Advanced Configuration
    context_window: int = Field(default=3900, alias="CONTEXT_WINDOW")
    similarity_top_k: int = Field(default=10, alias="SIMILARITY_TOP_K")
    
    # PgVector Advanced
    vector_distance_metric: str = Field(default="cosine", alias="VECTOR_DISTANCE_METRIC")
    
    # Indexing Advanced
    index_batch_size: int = Field(default=100, alias="INDEX_BATCH_SIZE")
    enable_incremental_indexing: bool = Field(default=True, alias="ENABLE_INCREMENTAL_INDEXING")
    auto_run_migrations: bool = Field(default=False, alias="AUTO_RUN_MIGRATIONS")
    
    # LLM Configuration
    llm_provider: str = Field(default="azure", alias="LLM_PROVIDER")
    azure_openai_llm_deployment: str = Field(default="gpt-4o-mini", alias="AZURE_OPENAI_LLM_DEPLOYMENT")
    azure_openai_llm_model: str = Field(default="gpt-4o", alias="AZURE_OPENAI_LLM_MODEL")  # Actual model name
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, alias="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=2000, alias="OPENAI_MAX_TOKENS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env
    
    @property
    def database_url(self) -> str:
        """Get SQLAlchemy database URL"""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    @property
    def async_database_url(self) -> str:
        """Get async SQLAlchemy database URL"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


# Global settings instance
settings = Settings()
