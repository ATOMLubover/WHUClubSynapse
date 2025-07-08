import json
import csv
from collections import defaultdict

input_file = 'local_synced_data.jsonl'
output_file = 'recommend_system/extracted_clubs.csv'

def extract_club_data():
    # 使用字典存储每个社团的信息
    clubs = defaultdict(lambda: {
        'club_name': '',
        'tags': [],
        'desc': '',  # 将使用置顶帖子的标题
        'posts': 0,  # 帖子计数
        'pinned_posts': []  # 临时存储置顶帖子
    })
    
    # 第一次遍历：收集所有社团基本信息和帖子信息
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            try:
                data = json.loads(line.strip())
                
                # 处理社团信息
                if data['id'].startswith('dynamic::club_id::'):
                    club_id = data['id'].split('::')[-1]
                    metadata = data.get('metadata', {})
                    clubs[club_id]['club_name'] = metadata.get('name', data.get('document', ''))
                    
                    # 处理标签
                    tags_str = metadata.get('tags', '[]')
                    try:
                        if isinstance(tags_str, str):
                            tags_list = json.loads(tags_str)
                        else:
                            tags_list = tags_str
                        if isinstance(tags_list, list):
                            clubs[club_id]['tags'] = tags_list
                    except json.JSONDecodeError:
                        clubs[club_id]['tags'] = []
                
                # 处理帖子信息
                elif data['id'].startswith('dynamic::post_id::'):
                    metadata = data.get('metadata', {})
                    club_id = str(metadata.get('club_id', ''))
                    if club_id:
                        # 增加帖子计数
                        clubs[club_id]['posts'] += 1
                        
                        # 如果是置顶帖子，添加到置顶帖子列表
                        if metadata.get('is_pinned', False):
                            clubs[club_id]['pinned_posts'].append(metadata.get('title', ''))
                
            except json.JSONDecodeError:
                print(f"Skipping malformed JSON line: {line.strip()}")
            except KeyError as e:
                print(f"Skipping line due to missing key {e}: {line.strip()}")
    
    # 写入CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        csv_writer = csv.writer(outfile)
        # 写入头部
        csv_writer.writerow(['club_id', 'club_name', 'tags', 'desc', 'posts'])
        
        # 写入社团数据
        for club_id, club_info in clubs.items():
            # 使用第一个置顶帖子作为描述，如果没有则为空
            desc = club_info['pinned_posts'][0] if club_info['pinned_posts'] else ''
            
            # 将标签列表转换为管道分隔的字符串
            tags_str = '|'.join(club_info['tags']) if club_info['tags'] else ''
            
            csv_writer.writerow([
                club_id,
                club_info['club_name'],
                tags_str,
                desc,
                club_info['posts']
            ])
    print(f"社团数据已提取并保存到 {output_file}")

if __name__ == '__main__':
    extract_club_data() 