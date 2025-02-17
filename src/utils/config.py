from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    # Qdrant配置
    QDRANT_LOCATION: str = ":memory:"  # 使用内存模式
    QDRANT_COLLECTION_NAME: str = "operations"
    
    # BGE模型配置
    BGE_MODEL_NAME: str = "BAAI/bge-large-zh"
    
    # 记忆系统配置
    MEMORY_SIMILARITY_THRESHOLD: float = 0.7
    TOP_K_SIMILAR_OPS: int = 3
    
    # DeepSeek配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings() 