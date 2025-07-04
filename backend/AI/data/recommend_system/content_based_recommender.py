import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from typing import List, Dict, Any
import jieba
import re
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentBasedRecommender:
    def __init__(self):
        # 初始化向量化器
        self.text_vectorizer = TfidfVectorizer(
            tokenizer=self._tokenize_text,
            stop_words='english',  # 英文停用词
            max_features=5000
        )
        self.tag_vectorizer = TfidfVectorizer(
            tokenizer=lambda x: x.split('|'),  # 标签以|分隔
            binary=True
        )
        self.tag_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.scaler = StandardScaler()
        
        # 缓存
        self.club_features = {}  # 存储社团特征向量
        self.user_features = {}  # 存储用户特征向量
        
    def _tokenize_text(self, text: str) -> List[str]:
        """使用结巴分词处理中文文本"""
        try:
            # 确保输入是字符串
            if not isinstance(text, str):
                text = str(text)
            # 使用结巴分词
            words = jieba.cut(text)
            return [w for w in words if w.strip()]
        except Exception as e:
            logger.error(f"Error in tokenization: {str(e)}")
            return []
    
    def _process_club_features(self, clubs_data: List[Dict[str, Any]]):
        """处理社团特征"""
        try:
            # 提取文本特征（描述）
            descriptions = [club.get('desc', '') for club in clubs_data]
            self.text_features = self.text_vectorizer.fit_transform(descriptions)
            
            # 提取标签特征
            tags = [club.get('tags', '') for club in clubs_data]
            self.tag_features = self.tag_vectorizer.fit_transform(tags)
            
            # 提取数值特征（如活跃度、成员数等）
            self.numeric_features = np.array([
                [
                    float(club.get('activity_level', 0.5)),
                    float(club.get('member_count', 0))
                ]
                for club in clubs_data
            ])
            
            # 标准化数值特征
            if len(self.numeric_features) > 0:
                self.numeric_features = (self.numeric_features - self.numeric_features.mean(axis=0)) / (self.numeric_features.std(axis=0) + 1e-8)
            
        except Exception as e:
            logger.error(f"Error processing club features: {str(e)}")
            raise
    
    def _calculate_similarity(self, user_data: Dict[str, Any], clubs_data: List[Dict[str, Any]]) -> np.ndarray:
        """计算用户与社团的相似度"""
        try:
            # 处理用户文本特征
            user_text = f"{user_data.get('interests', '')} {user_data.get('bio', '')}"
            user_text_features = self.text_vectorizer.transform([user_text])
            
            # 处理用户标签特征
            user_tags = '|'.join(user_data.get('tags', []))
            user_tag_features = self.tag_vectorizer.transform([user_tags])
            
            # 计算文本相似度
            text_sim = cosine_similarity(user_text_features, self.text_features).flatten()
            
            # 计算标签相似度
            tag_sim = cosine_similarity(user_tag_features, self.tag_features).flatten()
            
            # 计算专业匹配度（简单匹配）
            major_match = np.array([
                1.0 if club.get('target_major', '').lower() == user_data.get('major', '').lower()
                else 0.5
                for club in clubs_data
            ])
            
            # 组合所有相似度分数
            combined_sim = (
                0.4 * text_sim +  # 文本特征权重
                0.4 * tag_sim +   # 标签特征权重
                0.2 * major_match # 专业匹配权重
            )
            
            return combined_sim
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            raise
    
    def get_recommendations(
        self, 
        user_data: Dict[str, Any],
        clubs_data: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """获取推荐结果"""
        try:
            if not clubs_data:
                raise ValueError("No clubs data provided")
            
            # 处理社团特征
            self._process_club_features(clubs_data)
            
            # 计算相似度
            similarities = self._calculate_similarity(user_data, clubs_data)
            
            # 获取top_n推荐
            top_indices = np.argsort(similarities)[-top_n:][::-1]
            
            # 构建推荐结果
            recommendations = []
            for idx in top_indices:
                club_data = clubs_data[idx].copy()
                club_data['similarity_score'] = float(similarities[idx])
                recommendations.append(club_data)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise
    
    def _extract_text_features(self, texts: List[str]) -> np.ndarray:
        """提取文本特征"""
        # 合并多个文本字段
        combined_texts = [' '.join(text_list) for text_list in texts]
        return self.text_vectorizer.fit_transform(combined_texts).toarray()
    
    def _extract_tag_features(self, tags: List[List[str]]) -> np.ndarray:
        """提取标签特征"""
        # 将标签列表转换为适合 OneHotEncoder 的格式
        tags_array = np.array(tags).reshape(-1, 1)
        return self.tag_encoder.fit_transform(tags_array)
    
    def _extract_numeric_features(self, numeric_data: List[Dict[str, float]]) -> np.ndarray:
        """提取数值特征"""
        numeric_array = np.array([[v for v in d.values()] for d in numeric_data])
        return self.scaler.fit_transform(numeric_array)
    
    def build_club_features(self, clubs_data: List[Dict[str, Any]]) -> Dict[int, np.ndarray]:
        """构建社团特征向量"""
        club_texts = []  # 存储所有文本特征
        club_tags = []   # 存储所有标签
        club_nums = []   # 存储所有数值特征
        
        for club in clubs_data:
            # 收集文本特征
            texts = [
                club['club_name'],
                club['desc'],
            ]
            club_texts.append(texts)
            
            # 收集标签特征
            tags = club['tags'].split('|') if isinstance(club['tags'], str) else club['tags']
            club_tags.append(tags)
            
            # 收集数值特征
            numeric_features = {
                'posts': float(club['posts'])  # 转换为浮点数以便标准化
            }
            club_nums.append(numeric_features)
        
        # 提取各类特征
        text_features = self._extract_text_features(club_texts)
        tag_features = self._extract_tag_features(club_tags)
        numeric_features = self._extract_numeric_features(club_nums)
        
        # 合并所有特征
        club_features = np.concatenate([text_features, tag_features, numeric_features], axis=1)
        
        # 构建特征字典
        return {int(club['club_id']): club_features[i] for i, club in enumerate(clubs_data)}
    
    def build_user_profile(self, user_data: Dict[str, Any]) -> np.ndarray:
        """构建用户画像向量"""
        # 提取用户文本特征
        user_texts = [
            user_data['interests'],
            user_data['major'],
            user_data.get('bio', '')
        ]
        
        # 提取用户标签
        user_tags = user_data['tags'].split('|') if isinstance(user_data['tags'], str) else user_data['tags']
        
        # 提取用户数值特征
        user_numeric = {
            'posts': 0.0  # 用户没有帖子数量特征，填充0
        }
        
        # 使用与社团相同的向量化器处理
        text_features = self._extract_text_features([user_texts])
        tag_features = self._extract_tag_features([user_tags])
        numeric_features = self._extract_numeric_features([user_numeric])
        
        # 合并所有特征
        return np.concatenate([text_features[0], tag_features[0], numeric_features[0]])
    
    def compute_similarity(self, user_vector: np.ndarray, club_vector: np.ndarray) -> float:
        """计算用户向量和社团向量之间的余弦相似度"""
        dot_product = np.dot(user_vector, club_vector)
        user_norm = np.linalg.norm(user_vector)
        club_norm = np.linalg.norm(club_vector)
        
        if user_norm == 0 or club_norm == 0:
            return 0.0
        
        return dot_product / (user_norm * club_norm) 