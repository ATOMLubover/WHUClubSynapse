import torch
import pandas as pd
import numpy as np
import jieba
from deep_community_recommend import DeepCommunityRecommender, TagEmbeddingDataset

class CommunityRecommendService:
    def __init__(self, model_path, communities_df):
        """
        初始化推荐服务
        
        Args:
            model_path: 模型文件路径
            communities_df: 社团信息DataFrame，包含community_id, community_name, tags
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 在服务初始化时加载完整的数据，以获取正确的 num_users 和 num_communities
        # 这确保了模型加载时与训练时的维度匹配
        self.all_users = pd.read_csv('users.csv')
        self.all_communities = pd.read_csv('communities.csv')

        self.communities = communities_df # 这是传入的用于推荐的子集或全部社团
        # 创建社团ID到内部索引的映射，基于all_communities
        self.community_to_idx = {cid: idx for idx, cid in enumerate(self.all_communities['community_id'].unique())}
        self.load_model(model_path)
        
    def load_model(self, model_path):
        """加载预训练模型"""
        # 加载保存的模型
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        
        # 获取词嵌入模型
        self.word2vec_model = checkpoint['word2vec_model']
        
        # 获取用户和社团的映射
        self.user_to_idx = checkpoint['user_to_idx']  # 加载用户ID到索引的映射
        # self.community_to_idx = checkpoint['community_to_idx'] # 社团映射已在__init__中处理
        
        # 初始化推荐模型，使用检查点中保存的num_users和num_communities
        num_users_from_checkpoint = checkpoint['num_users']
        num_communities_from_checkpoint = checkpoint['num_communities']

        self.model = DeepCommunityRecommender(
            num_users=num_users_from_checkpoint,
            num_communities=num_communities_from_checkpoint,
            embedding_dim=100,
            hidden_dim=64
        ).to(self.device)
        
        # 加载模型参数
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
    
    def _process_tags(self, tags_str):
        """处理标签字符串"""
        tags = tags_str.split('|')
        processed_tags = []
        for tag in tags:
            words = jieba.cut(tag.strip())
            words = [w for w in words if w.strip()]
            processed_tags.extend(words)
        return processed_tags
    
    def _get_tag_embedding(self, tags):
        """获取标签的词嵌入向量"""
        vectors = []
        for tag in tags:
            if tag in self.word2vec_model.wv:
                vectors.append(self.word2vec_model.wv[tag])
        
        if vectors:
            return np.mean(vectors, axis=0)
        else:
            return np.zeros(self.word2vec_model.vector_size)
    
    def get_recommendations(self, user_id, user_tags, target_communities_df, joined_communities=None, num_recommendations=5):
        """
        为用户推荐社团
        
        Args:
            user_id: 用户ID
            user_tags: 用户标签字符串，格式如 "标签1|标签2|标签3"
            target_communities_df: 用于推荐的社团信息DataFrame (只从这些社团中推荐)
            joined_communities: 用户已加入的社团ID列表，可选
            num_recommendations: 推荐数量
            
        Returns:
            推荐的社团列表，包含社团信息和相似度分数
        """
        # 处理用户标签
        processed_user_tags = self._process_tags(user_tags)
        user_tag_embedding = self._get_tag_embedding(processed_user_tags)
        
        # 准备已加入的社团集合
        if joined_communities is None:
            joined_communities = set()
        else:
            joined_communities = set(joined_communities)
        
        # 计算用户与所有目标社团的匹配度
        predictions = []
        
        # 获取用户内部索引
        if user_id in self.user_to_idx:
            user_internal_idx = self.user_to_idx[user_id]
        else:
            # 对于新用户，使用一个默认的用户索引（例如，0），模型将主要依赖标签嵌入
            user_internal_idx = 0 
            print(f"Warning: User ID {user_id} not found in training data. Using default user index {user_internal_idx}.")
            
        user_idx = torch.tensor([user_internal_idx]).to(self.device)  # 使用获取到的用户索引
        user_embedding = torch.tensor(user_tag_embedding).float().to(self.device)
        
        with torch.no_grad():
            for _, community in target_communities_df.iterrows():
                community_id = community['community_id']
                
                # 跳过已加入的社团
                if community_id in joined_communities:
                    continue
                
                # 获取社团的内部索引，如果不在训练数据中，则跳过
                if community_id not in self.community_to_idx:
                    print(f"Warning: Community ID {community_id} not found in training data, skipping.")
                    continue
                community_internal_idx = self.community_to_idx[community_id]
                
                # 处理社团标签
                community_tags = self._process_tags(community['tags'])
                community_embedding = self._get_tag_embedding(community_tags)
                community_embedding = torch.tensor(community_embedding).float().to(self.device)
                
                # 获取社团索引 (使用内部索引)
                community_idx = torch.tensor([community_internal_idx]).to(self.device)
                
                # 预测匹配度
                score = self.model(
                    user_idx,
                    community_idx,
                    user_embedding.unsqueeze(0),
                    community_embedding.unsqueeze(0)
                )
                
                predictions.append({
                    'community_id': community['community_id'],
                    'community_name': community['community_name'],
                    'tags': community['tags'],
                    'score': score.item()
                })
        
        # 按分数排序并返回前N个推荐
        predictions.sort(key=lambda x: x['score'], reverse=True)
        return predictions[:num_recommendations]

    def update_recommendations(self, user_id, new_tags, num_recommendations=5):
        """
        根据用户新标签更新推荐。

        Args:
            user_id: 用户ID
            new_tags: 用户新的标签字符串
            num_recommendations: 推荐数量

        Returns:
            更新后的推荐社团列表
        """
        # 这里我们假设更新推荐也是从初始化服务时传入的 communities 中进行。
        # 如果需要从所有社团中推荐，可以使用 self.all_communities
        return self.get_recommendations(
            user_id=user_id,
            user_tags=new_tags,
            target_communities_df=self.communities,
            num_recommendations=num_recommendations
        )

def create_sample_service():
    """创建示例推荐服务"""
    # 示例社团数据
    communities = pd.read_csv('communities.csv')
    
    # 初始化服务
    service = CommunityRecommendService('community_recommender.pth', communities)
    return service

# 使用示例
if __name__ == '__main__':
    # 加载所有社团数据，用于初始化服务
    all_communities = pd.read_csv('communities.csv')
    service = CommunityRecommendService('community_recommender.pth', all_communities)
    
    # 假设我们只想从"体育"类别或"科技"类别社团中推荐，这里我们使用所有社团作为目标池
    # 您可以根据实际需求筛选 target_communities_df
    target_communities_for_recommendation = all_communities.copy() 
    
    # 为新用户生成推荐
    user_tags = "摄影|编程|人工智能"
    recommendations = service.get_recommendations(
        user_id=999,
        user_tags=user_tags,
        target_communities_df=target_communities_for_recommendation, # 传入目标社团DataFrame
        joined_communities=[2]  # 假设用户已加入ID为2的社团（例如篮球社）
    )
    
    print("为用户(标签:", user_tags, ")推荐的社团：")
    for rec in recommendations:
        print(f"社团: {rec['community_name']}")
        print(f"标签: {rec['tags']}")
        print(f"匹配度: {rec['score']:.4f}")
        print()

    # 示例：假设现在只希望从标签包含"音乐"的社团中进行推荐
    music_communities = all_communities[all_communities['tags'].str.contains('音乐', na=False)]
    if not music_communities.empty:
        print("仅从包含'音乐'标签的社团中为用户(标签:", user_tags, ")推荐：")
        music_recommendations = service.get_recommendations(
            user_id=999,
            user_tags=user_tags,
            target_communities_df=music_communities,
            joined_communities=[] # 假设这次没有已加入的社团需要排除
        )
        for rec in music_recommendations:
            print(f"社团: {rec['community_name']}")
            print(f"标签: {rec['tags']}")
            print(f"匹配度: {rec['score']:.4f}")
            print()
    else:
        print("没有找到包含'音乐'标签的社团。") 