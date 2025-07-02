import asyncio
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from app.configs.config import settings
from app.rag.rag_service import retrieve

# 配置与准备
load_dotenv()

llm = ChatOpenAI(
    openai_api_base="https://api.deepseek.com/v1",
    api_key=settings.DEEPSEEK_API_KEY,
    model="deepseek-chat",
    temperature=0.1, # 在评估时使用低 temperature 以获得确定性回答
)

# RAG 的 Prompt 模板
RAG_PROMPT_TEMPLATE = """
请根据以下上下文信息，简洁而准确地回答用户的问题。只使用上下文中的信息，不要添加任何外部知识。如果上下文没有提供足够的信息，请回答“根据提供的资料，无法回答该问题。”

【上下文】
{context}

【问题】
{question}
"""

# 问题列表
questions = [
    "如何成为社团的认证成员？", 
    "社团管理员有什么权限？", 
    "如何查看社团的最新活动？",
    "忘记密码了怎么办？", 
    "如何创建新的社团？", 
    "如何申请创建新的社团？",
    "社团成员如何进行年度注册？", 
    "社团活动如何申请场地？", 
    "如何查看我的社团的财务状况？",
    "社团如何发布招新公告？", 
    "普通成员可以发起活动吗？", 
    "社团的认证流程是怎样的？",
    "如何修改社团的基本信息？", 
    "社团的年审需要提交哪些材料？", 
    "如何加入一个已经存在的社团？",
]

# 高质量 Ground Truth 
ground_truths = {
    "如何成为社团的认证成员？": "要成为社团的认证成员，需要完成以下步骤：首先，通过社团的官方招新渠道（线下招新摊位）提交加入申请；其次，参加社团组织的面试或审核流程；最后，在通过审核后，按照要求缴纳会费并完成信息注册。具体流程请参考目标社团的招新公告或直接联系社团管理员。",
    "社团管理员有什么权限？": "社团管理员拥有管理社团日常运营的多种权限，主要包括：1. **成员管理**：审核新成员申请、移除成员、设置成员角色和权限。2. **内容发布**：在社团主页发布新闻、活动预告和招新公告。3. **财务管理**：记录社团的财务收支，管理会费和活动预算。4. **活动管理**：创建和管理社团活动，包括场地申请、报名统计等。5. **信息修改**：编辑社团的基本信息，如介绍、联系方式和头像。",
    "如何查看社团的最新活动？": "您可以通过以下几种方式查看社团的最新活动：1. 访问社团管理系统的首页或“活动广场”板块，这里会集中展示所有社团的公开活动。2. 进入您感兴趣的特定社团的主页，查看其“活动列表”或“最新动态”。3. 关注社团的官方社交媒体账号或加入其通讯群组（如微信群、QQ群），社团通常会在此同步发布活动信息。",
    "忘记密码了怎么办？": "如果您忘记了社团管理系统的登录密码，请在登录页面点击“忘记密码”链接。系统会引导您进入密码重置流程，需要您输入注册时使用的邮箱或手机号来接收验证码。输入正确的验证码后，您就可以设置新的密码了。如果此方法无效，请联系平台的技术支持或网站管理员。",
    "如何创建新的社团？": "创建新的社团需要遵循学校或平台制定的官方流程。首先，您需要准备一份详细的社团创建申请书，内容包括社团章程、成立宗旨、指导老师信息、创始成员名单和年度活动计划。然后，将申请书提交至学生社团联合会或相关管理部门进行审核。审核通过后，您将获得创建社团的资格，并可以在系统中正式注册您的社团。",
    "如何申请创建新的社团？": "申请创建新社团的流程如下：第一步，撰写一份完整的社团创建申请材料，其中必须包含社团名称、宗旨、章程、指导老师简介、创始团队介绍及初步活动规划。第二步，登录社团管理系统，在“社团中心”找到“创建社团申请”入口，填写表单并上传您的申请材料。第三步，等待学生社团联合会的审核结果，审核状态会通过系统消息或邮件通知您。",
    "社团成员如何进行年度注册？": "社团成员的年度注册通常在每学年开始时进行。管理员会在社团内部发布通知，成员需要登录社团管理系统，进入个人中心或社团成员列表，找到“年度注册”或“确认成员资格”的选项，并按提示完成信息确认和会费缴纳。完成年度注册后，您新学年的成员资格才正式生效。",
    "社团活动如何申请场地？": "社团活动申请场地需通过社团管理系统内的“活动管理”模块进行。在创建新活动时，会有一个“场地申请”的流程。您需要填写活动时间、预计人数、所需设备等信息，并从可用场地列表中选择期望的场地。提交申请后，将由学校的场地管理部门进行审批。",
    "如何查看我的社团的财务状况？": "只有社团的指定管理员（如社长、财务部长）才有权限查看社团的详细财务状况。如果您是管理员，可以登录系统后进入社团的管理后台，找到“财务管理”板块。在这里，您可以查看收入记录、支出明细、当前余额以及生成财务报表。普通成员无法查看这些敏感信息。",
    "社团如何发布招新公告？": "社团管理员可以登录系统，进入社团的管理后台，选择“内容发布”或“公告管理”功能。然后点击“发布新公告”，选择公告类型为“招新”，填写标题、正文（包括社团介绍、招新要求、报名方式等），并可以上传宣传海报。发布后，该公告将显示在社团主页和平台的招新专区。",
    "普通成员可以发起活动吗？": "通常情况下，普通成员不能直接以社团名义发起官方活动。活动的创建和发布权限一般仅限于社团管理员。如果您有好的活动创意，建议您先向社团的管理员或管理团队提交您的活动策划方案。在方案获得批准后，再由管理员通过系统来正式创建和发布活动。",
    "社团的认证流程是怎样的？": "社团认证是指新创建的社团获得官方认可的流程。在提交创建申请并获得批准后，社团需要完成一系列认证步骤，可能包括：1. 提交创始成员和指导老师的详细信息备案。2. 完成社团负责人的安全知识培训。3. 在系统中完善社团的公开主页信息。全部完成后，社团的状态将由“待认证”更新为“已认证”，正式获得运营资格。",
    "如何修改社团的基本信息？": "若要修改社团的基本信息（如社团介绍、Logo、联系邮箱等），需要由社团管理员登录系统。进入社团管理后台，找到“社团设置”或“信息修改”页面。在此页面，您可以编辑相关信息字段并保存更改。请注意，某些核心信息（如社团名称）的修改需要提交申请并重新审核。",
    "社团的年审需要提交哪些材料？": "社团年审需要提交的材料通常包括：1. 年度工作总结报告：概述过去一年的活动、成就和成员发展情况。2. 年度财务报告：详细记录本年度的财务收支情况。3. 新一年度工作计划：阐述下一学年的发展目标和活动规划。4. 核心成员名单：更新社团主要负责人的信息。所有材料需通过社团管理系统的年审提交通道进行上传。",
    "如何加入一个已经存在的社团？": "您可以在社团管理平台的“社团列表”或“社团广场”浏览所有社团。找到您感兴趣的社团后，进入其主页，会有一个“加入我们”或“申请加入”按钮。点击后，填写弹出的申请表单并提交。之后，请耐心等待该社团管理员的审核通知。"
}

# 重写后的数据生成
async def generate_evaluation_data_remote():
    """
    使用远程 LLM API 生成 RAG 评估数据集。
    """
    data = {
        "question": [],
        "contexts": [],
        "answer": [],
        "ground_truth": []
    }
    
    # 构建 LangChain 调用链
    rag_chain = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE) | llm | StrOutputParser()

    for question in questions:
        print(f"正在处理问题: {question}")
        
        retrieved_docs = retrieve(question)
        contexts = [doc['content'] for doc in retrieved_docs]
        ground_truth = ground_truths.get(question, "")
        
        try:
            # 使用 LangChain 调用远程 LLM 生成回答
            full_answer = await rag_chain.ainvoke({
                "context": "\n\n".join(contexts),
                "question": question
            })
            
            # 填充数据集
            data["question"].append(question)
            data["contexts"].append(contexts)
            data["answer"].append(full_answer)
            data["ground_truth"].append(ground_truth)

        except Exception as e:
            print(f"处理问题 '{question}' 时发生错误: {e}")
            # 发生错误时，也添加空数据点以保持数据集的完整性
            data["question"].append(question)
            data["contexts"].append(contexts) # 仍然记录我们试图使用的上下文
            data["answer"].append(f"生成失败: {e}")
            data["ground_truth"].append(ground_truth)

    return data

# --- 5. 运行脚本 ---
async def main():
    print("开始生成评估数据集...")
    evaluation_data = await generate_evaluation_data_remote()
    
    # 将结果保存到 JSON 文件
    output_filename = "rag_evaluation_dataset.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(evaluation_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n数据集生成完毕，已保存至 {output_filename}")
    # 打印一个样本以供检查
    print("\n样本数据点:")
    print(json.dumps({k: v[0] for k, v in evaluation_data.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # 确保你已经创建了 .env 文件并填入了 API_KEY
    # 例如: OPENAI_API_KEY="sk-..."
    asyncio.run(main())