"""
Centralized configuration management for RegulAIte.
"""
import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """Database configuration."""
    host: str = Field(default="localhost")
    port: int = Field(default=3306)
    database: str = Field(default="regulaite")
    user: str = Field(default="regulaite_user")
    password: str = Field(default="SecureP@ssw0rd!")
    
    @validator('password')
    def validate_password(cls, v):
        if v == "SecureP@ssw0rd!":
            logger.warning("Using default database password. Please change in production.")
        return v

class QdrantConfig(BaseModel):
    """Qdrant vector database configuration."""
    url: str = Field(default="http://localhost:6333")
    grpc_url: Optional[str] = Field(default="localhost:6334")
    collection_name: str = Field(default="regulaite_documents")

class RedisConfig(BaseModel):
    """Redis configuration."""
    url: str = Field(default="redis://localhost:6379/0")

class LLMConfig(BaseModel):
    """LLM configuration."""
    openai_api_key: Optional[str] = None
    default_model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=2048)
    
    @validator('openai_api_key')
    def validate_api_key(cls, v):
        if not v:
            logger.warning("OpenAI API key not configured. Some features may not work.")
        return v

class DocumentParserConfig(BaseModel):
    """Document parser configuration."""
    unstructured_api_url: str = Field(default="http://localhost:9900/general/v0/general")
    unstructured_cloud_api_url: str = Field(default="https://api.unstructured.io/general/v0/general")
    unstructured_cloud_api_key: Optional[str] = None
    llamaparse_api_url: str = Field(default="https://api.llamaindex.ai/v1/parsing")
    llamaparse_api_key: Optional[str] = None
    doctly_api_url: str = Field(default="https://api.doctly.dev/v1/parse")
    doctly_api_key: Optional[str] = None
    default_parser_type: str = Field(default="unstructured")
    extract_tables: bool = Field(default=True)
    extract_metadata: bool = Field(default=True)
    extract_images: bool = Field(default=False)
    chunk_size: int = Field(default=2048)
    chunk_overlap: int = Field(default=200)

class AppConfig(BaseModel):
    """Main application configuration."""
    debug: bool = Field(default=False)
    environment: str = Field(default="development")
    
    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    document_parser: DocumentParserConfig = Field(default_factory=DocumentParserConfig)
    
    class Config:
        env_nested_delimiter = '__'

def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    config_dict = {
        'debug': os.getenv('DEBUG', 'false').lower() == 'true',
        'environment': os.getenv('ENVIRONMENT', 'development'),
        
        # Database configuration
        'database': {
            'host': os.getenv('MARIADB_HOST', 'localhost'),
            'port': int(os.getenv('MARIADB_PORT', '3306')),
            'database': os.getenv('MARIADB_DATABASE', 'regulaite'),
            'user': os.getenv('MARIADB_USER', 'regulaite_user'),
            'password': os.getenv('MARIADB_PASSWORD', 'SecureP@ssw0rd!'),
        },
        
        # Qdrant configuration
        'qdrant': {
            'url': os.getenv('QDRANT_URL', 'http://localhost:6333'),
            'grpc_url': os.getenv('QDRANT_GRPC_URL', 'localhost:6334'),
            'collection_name': os.getenv('QDRANT_COLLECTION_NAME', 'regulaite_documents'),
        },
        
        # Redis configuration
        'redis': {
            'url': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        },
        
        # LLM configuration
        'llm': {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'default_model': os.getenv('DEFAULT_LLM_MODEL', 'gpt-4'),
            'temperature': float(os.getenv('LLM_TEMPERATURE', '0.2')),
            'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '2048')),
        },
        
        # Document parser configuration
        'document_parser': {
            'unstructured_api_url': os.getenv('UNSTRUCTURED_API_URL', 'http://localhost:9900/general/v0/general'),
            'unstructured_cloud_api_url': os.getenv('UNSTRUCTURED_CLOUD_API_URL', 'https://api.unstructured.io/general/v0/general'),
            'unstructured_cloud_api_key': os.getenv('UNSTRUCTURED_CLOUD_API_KEY'),
            'llamaparse_api_url': os.getenv('LLAMAPARSE_API_URL', 'https://api.llamaindex.ai/v1/parsing'),
            'llamaparse_api_key': os.getenv('LLAMAPARSE_API_KEY'),
            'doctly_api_url': os.getenv('DOCTLY_API_URL', 'https://api.doctly.dev/v1/parse'),
            'doctly_api_key': os.getenv('DOCTLY_API_KEY'),
            'default_parser_type': os.getenv('DEFAULT_PARSER_TYPE', 'unstructured'),
            'extract_tables': os.getenv('EXTRACT_TABLES', 'true').lower() == 'true',
            'extract_metadata': os.getenv('EXTRACT_METADATA', 'true').lower() == 'true',
            'extract_images': os.getenv('EXTRACT_IMAGES', 'false').lower() == 'true',
            'chunk_size': int(os.getenv('CHUNK_SIZE', '2048')),
            'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', '200')),
        }
    }
    
    return AppConfig(**config_dict)

# Global configuration instance
config = load_config()

def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config

def validate_config() -> Dict[str, Any]:
    """Validate the configuration and return validation results."""
    validation_results = {
        'valid': True,
        'warnings': [],
        'errors': []
    }
    
    # Check critical configurations
    if not config.llm.openai_api_key:
        validation_results['warnings'].append("OpenAI API key not configured")
    
    if config.database.password == "SecureP@ssw0rd!":
        validation_results['warnings'].append("Using default database password")
    
    # Check if running in production with debug mode
    if config.environment == "production" and config.debug:
        validation_results['warnings'].append("Debug mode enabled in production")
    
    # Validate URLs
    required_services = [
        ('Qdrant', config.qdrant.url),
        ('Redis', config.redis.url),
    ]
    
    for service_name, url in required_services:
        if not url:
            validation_results['errors'].append(f"{service_name} URL not configured")
            validation_results['valid'] = False
    
    return validation_results 