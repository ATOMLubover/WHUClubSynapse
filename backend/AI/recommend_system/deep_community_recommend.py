import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from gensim.models import Word2Vec
import jieba
import re
from sklearn.model_selection import train_test_split

class TagEmbeddingDataset(Dataset):
    def __init__(self, users_df, communities_df, interactions_df, word2vec_model):
        self.users = users_df
        self.communities = communities_df
        self.interactions = interactions_df
        self.word2vec_model = word2vec_model
        self.vector_size = word2vec_model.vector_size
        
        # 创建用户和社团的映射字典
        self.user_to_idx = {uid: idx for idx, uid in enumerate(users_df['user_id'].unique())}
        self.community_to_idx = {cid: idx for idx, cid in enumerate(communities_df['community_id'].unique())}
        
        # 准备训练数据
        self.prepare_training_data()
    
    def prepare_training_data(self):
        """准备训练数据"""
        self.train_data = []
        
        # 对于每个用户-社团交互
        for _, row in self.interactions.iterrows():
            user_id = row['user_id']
            community_id = row['community_id']
            interaction = row['interaction']
            
            # 获取用户和社团的索引
            user_idx = self.user_to_idx[user_id]
            community_idx = self.community_to_idx[community_id]
            
            # 获取用户标签的嵌入向量
            user_data = self.users[self.users['user_id'] == user_id].iloc[0]
            user_tags = self._process_tags(user_data['user_tags'])
            user_embedding = self._get_tags_embedding(user_tags)
            
            # 获取社团标签的嵌入向量
            community_data = self.communities[self.communities['community_id'] == community_id].iloc[0]
            community_tags = self._process_tags(community_data['tags'])
            community_embedding = self._get_tags_embedding(community_tags)
            
            # 添加到训练数据
            self.train_data.append({
                'user_idx': user_idx,
                'community_idx': community_idx,
                'user_embedding': user_embedding,
                'community_embedding': community_embedding,
                'interaction': interaction
            })
    
    def _process_tags(self, tags_str):
        """处理标签字符串，分词并清理"""
        # 将标签字符串分割成列表
        tags = tags_str.split('|')
        # 对每个标签进行分词
        processed_tags = []
        for tag in tags:
            # 使用jieba分词
            words = jieba.cut(tag.strip())
            # 过滤掉空字符串和特殊字符
            words = [w for w in words if w.strip() and not re.match(r'[^\w\s]', w)]
            processed_tags.extend(words)
        return processed_tags
    
    def _get_tags_embedding(self, tags):
        """获取标签的词嵌入向量"""
        vectors = []
        for tag in tags:
            if tag in self.word2vec_model.wv:
                vectors.append(self.word2vec_model.wv[tag])
        
        if vectors:
            # 取所有标签向量的平均值
            return np.mean(vectors, axis=0)
        else:
            # 如果没有任何标签的词向量，返回零向量
            return np.zeros(self.vector_size)
    
    def __len__(self):
        return len(self.train_data)
    
    def __getitem__(self, idx):
        item = self.train_data[idx]
        return {
            'user_idx': torch.tensor(item['user_idx'], dtype=torch.long),
            'community_idx': torch.tensor(item['community_idx'], dtype=torch.long),
            'user_embedding': torch.tensor(item['user_embedding'], dtype=torch.float),
            'community_embedding': torch.tensor(item['community_embedding'], dtype=torch.float),
            'interaction': torch.tensor(item['interaction'], dtype=torch.float)
        }

class DeepCommunityRecommender(nn.Module):
    def __init__(self, num_users, num_communities, embedding_dim, hidden_dim):
        super(DeepCommunityRecommender, self).__init__()
        
        # 用户和社团的嵌入层
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.community_embedding = nn.Embedding(num_communities, embedding_dim)
        
        # 标签特征转换层
        self.tag_transform = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        # 组合层
        self.combine_layer = nn.Sequential(
            nn.Linear(embedding_dim * 2 + hidden_dim * 2, hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
    
    def forward(self, user_idx, community_idx, user_tag_embedding, community_tag_embedding):
        # 获取用户和社团的ID嵌入
        user_emb = self.user_embedding(user_idx)
        community_emb = self.community_embedding(community_idx)
        
        # 转换标签嵌入
        user_tag_features = self.tag_transform(user_tag_embedding)
        community_tag_features = self.tag_transform(community_tag_embedding)
        
        # 组合所有特征
        combined = torch.cat([
            user_emb,
            community_emb,
            user_tag_features,
            community_tag_features
        ], dim=1)
        
        # 预测交互概率
        return self.combine_layer(combined)

class CommunityRecommenderTrainer:
    def __init__(self, model, device, learning_rate=0.001):
        self.model = model
        self.device = device
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    def train_epoch(self, train_loader):
        self.model.train()
        total_loss = 0
        for batch in train_loader:
            # 将数据移到设备上
            user_idx = batch['user_idx'].to(self.device)
            community_idx = batch['community_idx'].to(self.device)
            user_embedding = batch['user_embedding'].to(self.device)
            community_embedding = batch['community_embedding'].to(self.device)
            interaction = batch['interaction'].to(self.device)
            
            # 前向传播
            self.optimizer.zero_grad()
            output = self.model(user_idx, community_idx, user_embedding, community_embedding)
            loss = self.criterion(output.squeeze(), interaction)
            
            # 反向传播
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def evaluate(self, val_loader):
        self.model.eval()
        total_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                user_idx = batch['user_idx'].to(self.device)
                community_idx = batch['community_idx'].to(self.device)
                user_embedding = batch['user_embedding'].to(self.device)
                community_embedding = batch['community_embedding'].to(self.device)
                interaction = batch['interaction'].to(self.device)
                
                output = self.model(user_idx, community_idx, user_embedding, community_embedding)
                loss = self.criterion(output.squeeze(), interaction)
                total_loss += loss.item()
        
        return total_loss / len(val_loader)

def create_sample_data():
    # 社团数据
    communities = pd.read_csv('communities.csv')
    
    # 用户数据（带自定义标签）
    users = pd.read_csv('users.csv')
    
    # 用户-社团互动数据
    interactions = pd.read_csv('interactions.csv')
    
    return communities, users, interactions

def train_word2vec(communities_df, users_df):
    """训练词嵌入模型"""
    # 收集所有标签文本
    all_tags = []
    
    # 处理社团标签
    for tags in communities_df['tags']:
        words = jieba.cut(tags.replace('|', ' '))
        all_tags.append(list(words))
    
    # 处理用户标签
    for tags in users_df['user_tags']:
        words = jieba.cut(tags.replace('|', ' '))
        all_tags.append(list(words))
    
    # 训练Word2Vec模型
    model = Word2Vec(sentences=all_tags, vector_size=100, window=5, min_count=1, workers=4)
    return model

def main():
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 创建示例数据
    communities, users, interactions = create_sample_data()
    
    # 训练词嵌入模型
    word2vec_model = train_word2vec(communities, users)
    
    # 创建数据集
    dataset = TagEmbeddingDataset(users, communities, interactions, word2vec_model)
    
    # 划分训练集和验证集
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)
    
    # 初始化模型
    model = DeepCommunityRecommender(
        num_users=len(users),
        num_communities=len(communities),
        embedding_dim=100,
        hidden_dim=64
    ).to(device)
    
    # 创建训练器
    trainer = CommunityRecommenderTrainer(model, device)
    
    # 训练模型
    num_epochs = 10
    for epoch in range(num_epochs):
        train_loss = trainer.train_epoch(train_loader)
        val_loss = trainer.evaluate(val_loader)
        print(f'Epoch {epoch+1}/{num_epochs}:')
        print(f'Training Loss: {train_loss:.4f}')
        print(f'Validation Loss: {val_loss:.4f}')
    
    # 保存模型
    torch.save({
        'model_state_dict': model.state_dict(),
        'word2vec_model': word2vec_model,
        'num_users': len(users),
        'num_communities': len(communities),
        'user_to_idx': dataset.user_to_idx,
        'community_to_idx': dataset.community_to_idx
    }, 'community_recommender.pth')

if __name__ == '__main__':
    main() 