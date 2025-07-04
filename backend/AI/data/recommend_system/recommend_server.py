from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from recommend_service import RecommendationService
import uvicorn
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Club Recommendation Service")

# 确保使用正确的数据文件路径
current_dir = os.path.dirname(os.path.abspath(__file__))
recommendation_service = RecommendationService()

class UserProfile(BaseModel):
    user_id: str
    interests: str
    major: str
    tags: List[str]
    bio: Optional[str] = ""
    year: Optional[int] = 1
    activity_level: Optional[float] = 0.5

class RecommendationResponse(BaseModel):
    status: str
    user_id: str
    recommendations: List[Dict[str, Any]]
    recommendation_type: str
    total_clubs_considered: int
    profile_completeness: float

@app.on_event("startup")
async def startup_event():
    """启动时加载数据"""
    try:
        clubs_file = os.path.join(current_dir, 'extracted_clubs.csv')
        recommendation_service.load_data(clubs_file)
        logger.info("Successfully loaded club data on startup")
    except Exception as e:
        logger.error(f"Error loading data on startup: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(user_profile: UserProfile, top_n: int = 5):
    """获取社团推荐"""
    try:
        # 转换用户数据格式
        user_data = user_profile.dict()
        
        # 获取推荐
        recommendations = recommendation_service.get_recommendations(user_data, top_n)
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reload_data")
async def reload_data():
    """重新加载社团数据"""
    try:
        clubs_file = os.path.join(current_dir, 'extracted_clubs.csv')
        recommendation_service.load_data(clubs_file)
        return {"status": "success", "message": "Successfully reloaded club data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)  # 使用8001端口，避免与主服务器冲突 