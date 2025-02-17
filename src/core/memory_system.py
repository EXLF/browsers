from typing import List, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModel
from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.utils.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemorySystem:
    def __init__(self):
        """初始化记忆系统，包括BGE模型和Qdrant客户端"""
        logger.info("初始化记忆系统...")
        
        # 初始化BGE模型
        self.tokenizer = AutoTokenizer.from_pretrained(settings.BGE_MODEL_NAME)
        self.model = AutoModel.from_pretrained(settings.BGE_MODEL_NAME)
        
        # 初始化Qdrant客户端（内存模式）
        self.client = QdrantClient(location=settings.QDRANT_LOCATION)
        
        # 确保collection存在
        self._ensure_collection()
        
        logger.info("记忆系统初始化完成")

    def _ensure_collection(self):
        """确保Qdrant中存在所需的collection"""
        collections = self.client.get_collections().collections
        if not any(c.name == settings.QDRANT_COLLECTION_NAME for c in collections):
            self.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=1024,  # BGE-large-zh 模型输出维度
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"创建collection: {settings.QDRANT_COLLECTION_NAME}")

    def _get_embedding(self, text: str) -> List[float]:
        """使用BGE模型生成文本的向量表示"""
        encoded_input = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            return_tensors='pt'
        )
        
        with torch.no_grad():
            model_output = self.model(**encoded_input)
            
        # 使用[CLS]标记的输出作为句子表示
        embedding = model_output.last_hidden_state[:, 0].numpy()
        return embedding[0].tolist()

    def store_operation(self, instruction: str, actions: List[Dict[str, Any]]) -> bool:
        """存储操作到记忆系统
        
        Args:
            instruction: 用户指令
            actions: 执行的操作序列
            
        Returns:
            bool: 存储是否成功
        """
        try:
            # 生成向量
            vector = self._get_embedding(instruction)
            
            # 存储到Qdrant
            self.client.upsert(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                points=[models.PointStruct(
                    id=hash(instruction),
                    vector=vector,
                    payload={
                        "instruction": instruction,
                        "actions": actions
                    }
                )]
            )
            logger.info(f"成功存储操作: {instruction}")
            return True
            
        except Exception as e:
            logger.error(f"存储操作失败: {str(e)}")
            return False

    def find_similar_operations(self, instruction: str) -> List[Dict[str, Any]]:
        """查找与给定指令相似的历史操作
        
        Args:
            instruction: 用户指令
            
        Returns:
            List[Dict]: 相似操作列表，按相似度排序
        """
        try:
            # 生成查询向量
            vector = self._get_embedding(instruction)
            
            # 在Qdrant中搜索
            search_result = self.client.search(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                query_vector=vector,
                limit=settings.TOP_K_SIMILAR_OPS,
                score_threshold=settings.MEMORY_SIMILARITY_THRESHOLD
            )
            
            # 转换结果
            similar_ops = [
                {
                    "instruction": hit.payload["instruction"],
                    "actions": hit.payload["actions"],
                    "similarity": hit.score
                }
                for hit in search_result
            ]
            
            logger.info(f"找到 {len(similar_ops)} 个相似操作")
            return similar_ops
            
        except Exception as e:
            logger.error(f"搜索相似操作失败: {str(e)}")
            return []

    def clear_memory(self) -> bool:
        """清空记忆系统（用于测试）"""
        try:
            self.client.delete_collection(settings.QDRANT_COLLECTION_NAME)
            self._ensure_collection()
            logger.info("记忆系统已清空")
            return True
        except Exception as e:
            logger.error(f"清空记忆系统失败: {str(e)}")
            return False 