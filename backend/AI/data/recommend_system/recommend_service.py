from typing import List, Dict, Any
from content_based_recommender import ContentBasedRecommender
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.content_recommender = ContentBasedRecommender()
        self.clubs_data = None
        
    def load_data(self, clubs_file: str = 'extracted_clubs.csv'):
        """加载社团数据"""
        try:
            # 读取社团数据
            clubs_df = pd.read_csv(clubs_file)
            self.clubs_data = clubs_df.to_dict('records')
            logger.info(f"Successfully loaded {len(self.clubs_data)} clubs")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def get_recommendations(self, user_data: Dict[str, Any], top_n: int = 5) -> Dict[str, Any]:
        """获取用户推荐结果"""
        try:
            if not self.clubs_data:
                raise ValueError("Clubs data not loaded. Please call load_data() first.")
            
            # 确保用户资料包含必要字段
            required_fields = ['interests', 'major', 'tags']
            missing_fields = [field for field in required_fields if field not in user_data]
            
            if missing_fields:
                raise ValueError(f"Missing required fields in user data: {', '.join(missing_fields)}")
            
            # 获取推荐结果
            recommendations = self.content_recommender.get_recommendations(
                user_data=user_data,
                clubs_data=self.clubs_data,
                top_n=top_n
            )
            
            # 构建推荐响应
            response = {
                "status": "success",
                "user_id": user_data.get("user_id", "unknown"),
                "recommendations": recommendations,
                "recommendation_type": "content_based",
                "total_clubs_considered": len(self.clubs_data),
                "profile_completeness": self._calculate_profile_completeness(user_data)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e),
                "user_id": user_data.get("user_id", "unknown")
            }
    
    def _calculate_profile_completeness(self, user_profile: Dict[str, Any]) -> float:
        """计算用户资料完整度"""
        total_fields = ['interests', 'major', 'tags', 'bio', 'year', 'activity_level']
        filled_fields = sum(1 for field in total_fields if user_profile.get(field))
        return filled_fields / len(total_fields)
    
    def update_club_data(self, new_club_data: Dict[str, Any]) -> bool:
        """更新社团数据"""
        try:
            if not self.clubs_data:
                self.clubs_data = []
            
            # 检查是否存在相同ID的社团
            existing_club = next(
                (club for club in self.clubs_data if club['club_id'] == new_club_data['club_id']), 
                None
            )
            
            if existing_club:
                # 更新现有社团数据
                existing_club.update(new_club_data)
            else:
                # 添加新社团
                self.clubs_data.append(new_club_data)
            
            logger.info(f"Successfully updated club data for club_id: {new_club_data['club_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating club data: {str(e)}")
            return False 