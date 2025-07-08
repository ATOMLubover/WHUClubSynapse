from typing import List, Optional, Dict, Any
import logging
import os
import sys
import summary
from openai import OpenAI
from fastapi.responses import StreamingResponse, JSONResponse
import time
import re
import signal
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import httpx
import json

@app.post("/generate_user_data", response_model=MLDataGenerationResponse)
async def generate_user_data(request: MLDataGenerationRequest):
    """
    根据机器学习需求，使用AI生成模拟的社团、用户和互动数据。
    生成过程分为三个阶段：社团信息、个人偏好、以及基于前两者的互动信息。
    
    Args:
        request: 包含生成数量（社团、用户、互动）的请求体。
        
    Returns:
        MLDataGenerationResponse: 包含生成的社团、用户和互动数据。
    """
    try:
        # 固定每个批次LLM调用生成数量（为了多样性）
        LLM_BATCH_SIZE = 10 # 统一批次大小，LLM返回的实际数量会是这个值减2

        all_users = []

        user_prompt_template = """
你是一个顶尖的数据生成AI，专注于为机器学习任务生成高质量、结构化的模拟用户数据。

你的任务是根据以下数据模型和要求，一次性生成指定数量的模拟用户数据，并以JSON格式返回。



**重要：你必须生成与已提供数据不重复的全新数据。生成的 user_id 必须是未出现过的新ID。**



**数据模型:**

-   `user_id`: 整型，用户的唯一ID。

-   `username`: 字符串，用户名，例如 "user_001", "admin_test"。

-   `email`: 字符串，电子邮件地址，例如 "user001@example.com"。

-   `role`: 字符串，角色类型，只能是 "user" 或 "admin"。

-   `created_at`: 字符串，创建时间，ISO 8601 格式，例如 "2024-01-01T10:00:00.000000"。

-   `updated_at`: 字符串，更新时间，ISO 8601 格式，通常晚于 created_at。

-   `last_active_at`: 字符串，最后活动时间，ISO 8601 格式，通常晚于 updated_at。

-   `extension`: JSON 对象字符串，包含用户的额外信息,包括interestedCategories，emailNotifications，applicationNotifications，activityNotifications，profilePublic，showJoinedClubs，tags,phone，包括例如: `{{\"realName\":\"张三\",\"studentId\":\"20230001\",\"major\":\"计算机学院\",\"bio\":\"热爱编程和篮球\",\"preferences\":{{\"interestedCategories\":[\"科技\",\"运动\"],\"emailNotifications\":true,\"applicationNotifications\":true,\"activityNotifications\":false,\"profilePublic\":true,\"showJoinedClubs\":true}},\"tags\":[\"开朗外向\",\"逻辑清晰\"],\"phone\":\"138xxxx1234\"}}`



**注意：**

-   `password` 和 `avatar_url` 字段无需生成，它们将由其他系统处理。

-   `user_id` 应从 1 开始递增，确保在当前批次中唯一。



**生成数量要求:**

-   `num_users`: {num_users}



**输出格式要求:**

请**直接**按照以下JSON格式返回结果，**不要包含任何Markdown代码块或其他文本**：

{{

  "users": [

    {{\"user_id\": 1, \"username\": \"testadmin\", \"email\": \"aabb@cc.com\", \"role\": \"admin\", \"created_at\": \"2025-06-24T16:04:30.705418\", \"updated_at\": \"2025-07-04T09:22:57.908024\", \"last_active_at\": \"2025-06-25T19:44:11.12609\", \"extension\": {{\"realName\":\"张三\",\"studentId\":\"20230001\",\"major\":\"计算机学院\",\"bio\":\"热爱编程和篮球\",\"preferences\":{{\"interestedCategories\":[\"科技\",\"运动\"],\"emailNotifications\":true,\"applicationNotifications\":true,\"activityNotifications\":false,\"profilePublic\":true,\"showJoinedClubs\":true}},\"tags\":[\"开朗外向\",\"逻辑清晰\"],\"phone\":\"138xxxx1234\"}}}},

    {{\"user_id\": 2, \"username\": \"normaluser\", \"email\": \"user@example.com\", \"role\": \"user\", \"created_at\": \"2025-06-25T10:00:00.000000\", \"updated_at\": \"2025-07-05T10:30:00.000000\", \"last_active_at\": \"2025-07-05T11:00:00.000000\", \"extension\": {{\"realName\":\"李四\",\"studentId\":\"20230002\",\"major\":\"软件工程\",\"bio\":\"喜欢户外活动\",\"preferences\":{{\"interestedCategories\":[\"户外\",\"音乐\"],\"emailNotifications\":true,\"applicationNotifications\":false,\"activityNotifications\":true,\"profilePublic\":true,\"showJoinedClubs\":false}},\"tags\":[\"活泼开朗\",\"乐于助人\"],\"phone\":\"139xxxx5678\"}}}}

    // ... 其他用户数据 ...

  ]

}}



请开始生成数据。
"""

        max_iterations = 100  # Adjust as needed, safety break
        
        # --- Stage 2: Generate Users ---
        current_iteration = 0
        while len(all_users) < request.num_users and current_iteration < max_iterations:
            current_iteration += 1
            users_to_request = min(LLM_BATCH_SIZE, request.num_users - len(all_users))

            if users_to_request <= 0:
                break

            existing_users_str = "" # We'll let LLM handle uniqueness within batch and start from 1
            if all_users:
                # Pass existing user IDs and maybe a few other details to help LLM avoid duplicates/generate new ones
                existing_users_str = "\n".join([
                    f"- ID: {u.user_id}, Username: {u.username}, Email: {u.email}"
                    for u in all_users
                ])
                existing_users_str = f"**已有用户数据 (请在此基础上生成新的、不重复的用户):**\n{existing_users_str}\n"
            

            current_prompt_formatted = user_prompt_template.format(
                num_users=users_to_request + 2, # +2 for example discarding
                existing_data_str=existing_users_str
            )
            
            logger.info(f"AI用户数据生成Prompt (Users Iteration {current_iteration}): {current_prompt_formatted[:200]}...")

            messages = [
                Message(role="system", content="你是一个顶尖的数据生成AI，专注于为机器学习任务生成高质量、结构化的模拟用户数据。请严格按照要求的JSON格式返回数据。请确保生成的数据是全新的，并且ID不与提供的已有数据重复。"),
                Message(role="user", content=current_prompt_formatted)
            ]
            
            chat_request = ChatRequest(
                messages=messages,
                model=config.default_model,
                max_tokens=8000,
                temperature=0.7,
                top_p=0.95,
                stream=False
            )

            llm_response_content = ""
            try:
                chat_response = await chat(chat_request)
                llm_response_content = chat_response.response
            except HTTPException as e:
                logger.warning(f"LLM调用失败 (Users Iteration {current_iteration}): {e.detail}")
                continue
            except Exception as e:
                logger.warning(f"LLM调用发生未知错误 (Users Iteration {current_iteration}): {e}")
                continue

            if not llm_response_content.strip():
                logger.warning(f"AI未返回有效的响应内容 (Users Iteration {current_iteration})。")
                continue

            json_string = llm_response_content.strip()
            if json_string.startswith("```json") and json_string.endswith("```"):
                json_string = json_string[len("```json"): -len("```")].strip()
            
            match = re.search(r'"users":\s*\[.*?\]', json_string, re.DOTALL) # More specific regex for users list
            if not match:
                logger.warning(f"AI响应中未找到有效的users JSON结构 (Users Iteration {current_iteration}): {llm_response_content[:200]}...")
                continue
            
            try:
                # Extract only the users array for parsing
                users_array_str = "{\"users\": " + match.group(0).split(':', 1)[1] + "}"
                parsed_response = json.loads(users_array_str)
                users_data = parsed_response.get("users", [])

                existing_user_ids = {u.user_id for u in all_users}
                new_users_batch = []
                for item in users_data:
                    try:
                        # Ensure 'extension' is a dict, not a JSON string
                        if 'extension' in item and isinstance(item['extension'], str):
                            try:
                                item['extension'] = json.loads(item['extension'])
                            except json.JSONDecodeError as json_err:
                                logger.warning(f"Error decoding extension JSON string for user item: {item.get('user_id', 'N/A')}, Error: {json_err}. Original string: {item['extension'][:100]}...")
                                continue # Skip this item if extension is malformed
                            
                        user = UserItem(**item)
                        if user.user_id not in existing_user_ids:
                            new_users_batch.append(user)
                            existing_user_ids.add(user.user_id)
                        else:
                            logger.warning(f"Skipping duplicate user ID: {user.user_id} (Users Iteration {current_iteration})")
                    except Exception as e:
                        logger.warning(f"解析单个用户条目时出错: {item}, 错误: {e} (Users Iteration {current_iteration})")

                all_users.extend(new_users_batch)
                logger.info(f"Users Iteration {current_iteration}: Added {len(new_users_batch)} new users. Total so far: {len(all_users)}")

            except json.JSONDecodeError as e:
                logger.warning(f"AI响应不是有效的JSON (Users Iteration {current_iteration}): {e}, 响应内容: {json_string[:200]}...")
                continue
            except Exception as e:
                logger.warning(f"处理本批次用户数据时出错 (Users Iteration {current_iteration}): {e}")
                continue
        
        if not all_users and request.num_users > 0:
            raise ValueError("未能生成任何有效数据")

       

        # Final truncation to exact requested quantities
        final_users = all_users[:request.num_users]

        if not final_users :
            raise ValueError("未能生成任何有效数据")

        # Save to file
        save_path = None
        if request.save_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name, ext = os.path.splitext(request.save_file)
            file_name = f"{base_name}_{timestamp}{ext}" if ext else f"{base_name}_{timestamp}"
            save_path = os.path.join(current_dir, "generated_data", file_name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    for user in final_users:
                        json.dump(user.dict(), f, indent=2, ensure_ascii=False)
                        f.write('\n')
                logger.info(f"用户数据已成功保存到: {save_path}")
            except Exception as e:
                logger.error(f"保存用户数据到文件失败: {e}")
                save_path = None

        return MLDataGenerationResponse(
            users=final_users,
            message=f"成功生成 {len(final_users)} 条用户数据",
            file_path=save_path
        )
            
    except Exception as e:
        logger.error(f"AI机器学习数据生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI机器学习数据生成失败: {e}")
