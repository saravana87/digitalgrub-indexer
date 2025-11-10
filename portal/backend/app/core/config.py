"""
Configuration settings for the DigitalGrub Portal API
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )
    
    # Database Configuration
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="booksgrub_index_sources", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="", alias="DB_PASSWORD")
    
    # Azure OpenAI Configuration
    azure_openai_api_key: str = Field(default="", alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_embedding_deployment: str = Field(default="text-embedding-3-large", alias="AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    azure_openai_llm_deployment: str = Field(default="model-router", alias="AZURE_OPENAI_LLM_DEPLOYMENT")
    azure_openai_llm_model: str = Field(default="gpt-4o", alias="AZURE_OPENAI_LLM_MODEL")
    azure_openai_api_version: str = Field(default="2024-02-15-preview", alias="AZURE_OPENAI_API_VERSION")
    
    # Vector Configuration
    vector_dimension: int = Field(default=3072, alias="VECTOR_DIMENSION")
    vector_table_prefix: str = Field(default="llamaindex_embedding", alias="VECTOR_TABLE_PREFIX")
    
    # API Configuration
    api_title: str = Field(default="DigitalGrub Portal API", alias="API_TITLE")
    api_version: str = Field(default="1.0.0", alias="API_VERSION")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    
    # CORS
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")
    
    # Indexer Path
    indexer_path: str = Field(default="../digitalgrub-indexer", alias="INDEXER_PATH")
    
    @property
    def database_url(self) -> str:
        """Get database URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Create settings instance
settings = Settings()
