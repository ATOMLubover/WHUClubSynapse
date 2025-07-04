from recommend_service import CommunityRecommendService
import pandas as pd

def create_test_communities():
    """创建测试用的社团数据"""
    # 示例社团数据，可以替换为从其他来源加载的任意社团信息
    return pd.DataFrame({
        'community_id': [101, 102, 103, 104, 105, 106, 107, 108],
        'community_name': ['历史研究社', '科幻小说社', '户外摄影俱乐部', '街舞社', '古典音乐鉴赏', '心理学探索社', '美食烹饪坊', '数字艺术创作'],
        'tags': [
            '历史|文化|考古',
            '科幻|小说|未来',
            '摄影|户外|自然',
            '街舞|现代舞|律动',
            '古典音乐|乐器|鉴赏',
            '心理学|情商|成长',
            '美食|烹饪|烘焙',
            '数字艺术|建模|设计'
        ]
    })

def test_recommendations():
    """测试推荐功能"""
    
    try:
        # 加载所有社团数据作为可推荐的社团池
        all_communities = pd.read_csv('communities.csv')
        service = CommunityRecommendService('community_recommender.pth', all_communities)
        
        # 演示如何为现有用户生成推荐
        print("\n=== 测试案例：现有用户推荐 ===")
        # 假设用户ID 3 存在于 users.csv 中
        existing_user_id = 3
        existing_user_data = service.all_users[service.all_users['user_id'] == existing_user_id]
        if not existing_user_data.empty:
            existing_user_tags = existing_user_data.iloc[0]['user_tags']
            print(f"用户ID: {existing_user_id}, 用户标签: {existing_user_tags}")
            recommendations_for_existing_user = service.get_recommendations(
                user_id=existing_user_id,
                user_tags=existing_user_tags,
                target_communities_df=all_communities, # 从所有社团中推荐
                num_recommendations=5
            )
            print_recommendations(recommendations_for_existing_user)
        else:
            print(f"用户ID {existing_user_id} 不存在于 users.csv 中，请检查数据。")

        # 演示如何为新用户（或不在训练数据中的用户ID）生成推荐
        print("\n=== 测试案例：新用户推荐 ===")
        new_user_id = 9999 # 假设这个用户ID不在 users.csv 中
        new_user_tags = "历史|文学|哲学|艺术|博物馆|考古|文化遗产"
        print(f"用户ID: {new_user_id}, 用户标签: {new_user_tags}")
        recommendations_for_new_user = service.get_recommendations(
            user_id=new_user_id,
            user_tags=new_user_tags,
            target_communities_df=all_communities, # 从所有社团中推荐
            num_recommendations=5
        )
        print_recommendations(recommendations_for_new_user)

        # 演示如何为特定社团子集生成推荐
        print("\n=== 测试案例：指定社团子集推荐 ===")
        # 创建自定义的社团信息DataFrame (可以是用户提供的任意社团)
        custom_communities = create_test_communities()
        
        # 假设为新用户推荐来自这些自定义社团的信息
        custom_user_id = 8888
        custom_user_tags = "编程|技术|算法|数据分析|人工智能|机器学习"
        print(f"用户ID: {custom_user_id}, 用户标签: {custom_user_tags}")
        print("目标社团子集：")
        for _, row in custom_communities.iterrows():
            print(f"  - {row['community_name']} (标签: {row['tags']})")

        recommendations_from_custom_set = service.get_recommendations(
            user_id=custom_user_id,
            user_tags=custom_user_tags,
            target_communities_df=custom_communities, # 传入自定义社团DataFrame
            num_recommendations=3
        )
        print_recommendations(recommendations_from_custom_set)

        # 原始的测试案例1：技术爱好者 (保留作为参考)
        print("\n=== 原始测试案例1：技术爱好者 (保留作为参考) ===")
        tech_user_tags = "编程|人工智能|技术开发|算法|数据分析"
        recommendations = service.get_recommendations(
            user_id=1,
            user_tags=tech_user_tags,
            target_communities_df=all_communities,
            num_recommendations=3
        )
        print(f"用户标签: {tech_user_tags}")
        print_recommendations(recommendations)

        # 原始的测试案例2：艺术爱好者 (保留作为参考)
        print("\n=== 原始测试案例2：艺术爱好者 (保留作为参考) ===")
        art_user_tags = "绘画|创意|艺术|音乐|摄影"
        recommendations = service.get_recommendations(
            user_id=2,
            user_tags=art_user_tags,
            target_communities_df=all_communities,
            joined_communities=[1],  # 假设已加入摄影社
            num_recommendations=3
        )
        print(f"用户标签: {art_user_tags}")
        print_recommendations(recommendations)
        
        # 原始的测试案例3：多领域爱好者 (保留作为参考)
        print("\n=== 原始测试案例3：多领域爱好者 (保留作为参考) ===")
        multi_user_tags = "编程|音乐|动漫|创作|设计"
        recommendations = service.get_recommendations(
            user_id=3,
            user_tags=multi_user_tags,
            target_communities_df=all_communities,
            num_recommendations=4
        )
        print(f"用户标签: {multi_user_tags}")
        print_recommendations(recommendations)

        # 原始测试更新用户标签 (保留作为参考)
        print("\n=== 原始测试更新用户标签 (保留作为参考) ===")
        updated_tags = "编程|音乐|人工智能|创新|设计"
        updated_recommendations = service.update_recommendations(
            user_id=3,
            new_tags=updated_tags
        )
        print(f"更新后的标签: {updated_tags}")
        print_recommendations(updated_recommendations)
        
    except FileNotFoundError:
        print("错误：找不到模型文件 'community_recommender.pth'")
        print("请先运行 deep_community_recommend.py 训练模型")
    except Exception as e:
        print(f"发生错误: {str(e)}")

def print_recommendations(recommendations):
    """打印推荐结果"""
    print("\n推荐的社团：")
    if not recommendations:
        print("无推荐社团。")
        return
    for rec in recommendations:
        print(f"社团名称: {rec['community_name']}")
        print(f"社团标签: {rec['tags']}")
        print(f"匹配度: {rec['score']:.4f}")
        print("-" * 50)

if __name__ == '__main__':
    test_recommendations() 