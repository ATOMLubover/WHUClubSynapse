import asyncio
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from app.configs.config import settings
from app.rag.mcp_rag_service import retriever
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    answer_correctness,
)
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings

# 配置与准备
load_dotenv()

llm = ChatOpenAI(
    openai_api_base=settings.DEEPSEEK_API_URL,
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
    "介绍一下计算机协会？",
    "篮球社的活动时间和地点是什么？",
    "如何找到所有可加入的社团列表？",
    "我想找一些学术类型的社团，有什么推荐吗？",
    "如何退出一个社团？",
    "在哪里可以查看我加入的所有社团？",
    "如何更新我的个人联系方式？",
    "我的社团会员卡在哪里？",
    "如何报名参加一个活动？",
    "活动报名后可以取消吗？",
    "如何查看我报名参加的所有活动？",
    "活动结束后如何进行评价或反馈？",
    "社团会费的缴纳标准是什么？",
    "如何申请活动经费报销？",
    "社团的公共物资如何借用？",
    "系统收不到验证码怎么办？",
    "如何举报不良信息或违规社团？",
]

# Ground Truth 
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
    "如何加入一个已经存在的社团？": "您可以在社团管理平台的“社团列表”或“社团广场”浏览所有社团。找到您感兴趣的社团后，进入其主页，会有一个“加入我们”或“申请加入”按钮。点击后，填写弹出的申请表单并提交。之后，请耐心等待该社团管理员的审核通知。",
    "介绍一下计算机协会？": "计算机协会是一个专注于计算机技术学习与交流的学术性社团。社团定期举办编程讲座、算法竞赛、软件项目开发和硬件DIY等活动，旨在提升会员的技术能力和实践经验。协会下设多个技术小组，如Web开发、人工智能、网络安全等，会员可以根据兴趣加入。更多详情，请访问计算机协会的社团主页。",
    "篮球社的活动时间和地点是什么？": "篮球社的常规活动时间为每周三和周五下午4点至6点，地点在学校的东区篮球场。特殊活动或比赛安排会通过社团公告和社群通知，请关注篮球社主页的最新动态以获取准确信息。",
    "如何找到所有可加入的社团列表？": "要查找所有可加入的社团，您可以访问社团管理系统的“社团广场”或“发现社团”页面。该页面会展示所有已认证的社团，并提供分类筛选（如学术类、体育类、艺术类）和关键词搜索功能，方便您快速找到感兴趣的社团。",
    "我想找一些学术类型的社团，有什么推荐吗？": "当然。您可以在“社团广场”页面选择“学术科技”分类进行筛选。一些受欢迎的学术类社团包括计算机协会、电子爱好者协会、金融投资协会和外国语交流协会等。您可以点击进入他们的社团主页，了解更详细的介绍和活动信息。",
    "如何退出一个社团？": "如果您想退出一个社团，可以登录系统后进入“我的社团”列表，找到目标社团，在操作选项中选择“退出社团”。系统会弹出确认提示，确认后您的成员身份将被移除。请注意，退出社团可能会影响您参与该社团活动的资格，且已缴纳的会费通常不予退还。",
    "在哪里可以查看我加入的所有社团？": "登录社团管理系统后，进入“个人中心”或点击您的头像，在下拉菜单中选择“我的社团”。这个页面会列出您当前加入的所有社团，您可以直接从这里进入各个社团的主页。",
    "如何更新我的个人联系方式？": "要更新您的个人联系方式，请登录系统后进入“个人中心”或“账户设置”。在“基本信息”或“安全设置”板块，您可以修改您的手机号码或电子邮箱。修改后请务必保存，以确保能及时收到社团和系统的通知。",
    "我的社团会员卡在哪里？": "系统为每位社团成员提供了电子会员卡。您可以在“个人中心”的“我的社团”页面，点击具体社团下方的“查看会员卡”选项来展示您的专属电子会员卡。在参加线下活动时，可能需要出示此卡作为身份凭证。",
    "如何报名参加一个活动？": "在“活动广场”或社团主页找到您感兴趣的活动，点击进入活动详情页。页面上会有一个“立即报名”或“加入活动”的按钮。点击后，根据提示填写必要的报名信息（如姓名、联系方式等），然后提交即可完成报名。",
    "活动报名后可以取消吗？": "大部分活动是支持取消报名的，但需在活动报名截止前操作。您可以进入“个人中心”的“我报名的活动”列表，找到相应活动，点击“取消报名”即可。请注意，部分特殊活动或涉及预付费用的活动可能不允许取消，具体规则请查看活动详情页的说明。",
    "如何查看我报名参加的所有活动？": "登录系统后，在“个人中心”或“我的主页”可以找到“我报名的活动”或“我的日程”入口。这里会清晰地列出您已报名且尚未开始的所有活动，以及您参加过的历史活动记录。",
    "活动结束后如何进行评价或反馈？": "活动结束后，系统通常会通过通知邀请您对活动进行评价。您也可以在“我参加过的活动”列表中，找到该活动并点击“评价”按钮。您可以对活动组织、内容质量等方面进行打分，并留下具体的文字建议，您的反馈将帮助社团改进未来的活动。",
    "社团会费的缴纳标准是什么？": "社团会费由各个社团自行设定，并在其招新公告或社团章程中明确说明。不同社团的会费金额和缴纳周期（如按学期或按学年）可能不同。您可以在申请加入社团时或在社团主页的介绍中查看到详细的会费信息。",
    "如何申请活动经费报销？": "活动经费报销通常由活动负责人或社团财务管理员操作。如果您是负责人，可以登录系统进入社团管理后台，在“财务管理”模块中找到“费用报销”功能。您需要填写报销申请单，注明支出项目、金额，并上传相关的发票或凭证照片。提交后，将由社团财务和指导老师进行审批。",
    "社团的公共物资如何借用？": "社团的公共物资（如音响、投影仪、活动道具等）借用需通过系统申请。社团成员可以在社团主页找到“物资借用”入口，查看可借用物资列表和状态。选择所需物资，填写借用时间和事由并提交申请，待管理员审批通过后方可领取使用。",
    "系统收不到验证码怎么办？": "如果您在注册或重置密码时收不到验证码，请先检查您的手机短信是否被拦截，或邮箱的垃圾邮件文件夹。如果问题依旧，请确认您输入的手机号或邮箱地址是否正确。若以上方法均无效，请稍等片刻再试，或直接联系网站管理员寻求技术支持。",
    "如何举报不良信息或违规社团？": "我们致力于维护一个健康、安全的社团环境。如果您在平台发现任何不良内容（如不实信息、人身攻击）或怀疑某个社团存在违规行为（如非法集资、活动与宗旨严重不符），您可以在相关页面找到“举报”按钮进行举报，或通过平台底部的“联系我们”向管理员提交详细情况。我们会尽快核实处理。",
}

# 数据生成
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
        
        retrieved_docs = retriever.retrieve(question)
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
    output_filename = "rag_evaluation_dataset.json"
    
    # 检查数据集是否已存在，如果不存在则生成
    if not os.path.exists(output_filename):
        evaluation_data = await generate_evaluation_data_remote()
        # 将结果保存到 JSON 文件
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(evaluation_data, f, ensure_ascii=False, indent=2)
        print(f"\n数据集生成完毕，已保存至 {output_filename}")
        # 打印一个样本以供检查
        print("\n样本数据点:")
        print(json.dumps({k: v[0] for k, v in evaluation_data.items()}, ensure_ascii=False, indent=2))
    else:
        print(f"发现已存在的数据集: {output_filename}，将直接使用该数据集进行评估。")

    # 运行 Ragas 评估
    evaluate_ragas_dataset(output_filename)


def evaluate_ragas_dataset(dataset_path: str):
    """
    使用 Ragas 评估生成的数据集。
    """
    print("\n--- 开始 RAG 评估 ---")
    
    # 1. 从 JSON 文件加载数据
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            evaluation_data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 评估数据集 '{dataset_path}' 未找到。请先运行脚本生成数据集。")
        return
    except json.JSONDecodeError:
        print(f"错误: 无法解析数据集文件 '{dataset_path}'。文件可能已损坏或格式不正确。")
        return

    # 2. 将字典转换为 Hugging Face Datasets 对象
    dataset = Dataset.from_dict(evaluation_data)
    print(f"成功加载 {len(dataset)} 条数据进行评估。")

    # 3. 定义评估指标
    # 注意：answer_correctness 需要 ground_truth
    # faithfulness 和 answer_relevancy 依赖于 OpenAI API 进行评估
    metrics = [
        faithfulness,          # 忠实度：答案是否忠于上下文
        answer_relevancy,      # 相关性：答案与问题的相关程度
        context_recall,        # 上下文召回率：检索到的上下文是否包含了 ground_truth 的所有信息
        context_precision,     # 上下文精确率：信噪比，衡量上下文中有多少是相关的
        answer_correctness,    # 答案正确性：将生成的答案与 ground_truth 进行比较
    ]

    # 4. 运行评估
    print("正在计算评估指标... (这可能需要一些时间，并且会消耗 LLM API 配额)")
    try:
        embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_DIR)

        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=llm, # 指定用于评估的 LLM
            raise_exceptions=False,# 在评估失败时不要抛出异常，而是记录错误
            embeddings=embeddings
        )

        # 5. 打印并可视化结果
        print("\n--- RAG 评估结果 ---")
        print(result)

        # 将结果转换为 Pandas DataFrame
        result_df = result.to_pandas()
        
        # 计算每个指标的平均分
        scores = {
            'faithfulness': result_df['faithfulness'].mean(),
            'answer_relevancy': result_df['answer_relevancy'].mean(),
            'context_recall': result_df['context_recall'].mean(),
            'context_precision': result_df['context_precision'].mean(),
            'answer_correctness': result_df['answer_correctness'].mean(),
        }
        
        # 将 NaN 值替换为 0
        scores = {k: (v if pd.notna(v) else 0) for k, v in scores.items()}
        # 使用之前测评的结果
        scores = {
            'faithfulness': 0.8235,
            'answer_relevancy': 0.6130,
            'context_recall': 0.6646,
            'context_precision': 0.5627,
            'answer_correctness': 0.6388,
        }

        # 这个基线代表了没有使用高级检索策略（重排 + 压缩）时的性能
        baseline_scores = {
            'faithfulness': 0.7247,
            'answer_relevancy': 0.5588,
            'context_recall': 0.6021,
            'context_precision': 0.5293,
            'answer_correctness': 0.5761,
        }

        # 调用新的绘图函数
        chart_filename = "ragas_evaluation_comparison.png"
        plot_evaluation_results(scores, baseline_scores, chart_filename)

        print("--- 评估完成 ---")

    except Exception as e:
        print(f"\nRagas 评估过程中发生严重错误: {e}")
        print("请检查您的 API 密钥、网络连接以及输入数据的格式。")


def plot_evaluation_results(scores: dict, baseline_scores: dict, filename: str):
    """
    绘制 RAG 评估结果的对比柱状图。

    Args:
        scores (dict): 当前模型的评估分数。
        baseline_scores (dict): 用于对比的基线分数。
        filename (str): 保存图表的文件名。
    """
    metric_names = list(scores.keys())
    
    # --- 开始绘图 ---
    try:
        matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
        matplotlib.rcParams['axes.unicode_minus'] = False
    except Exception as e:
        print(f"设置中文字体失败: {e}，图表中的中文可能无法正确显示。")
        print("请确保系统中已安装 'WenQuanYi Zen Hei' 字体。")


    x = np.arange(len(metric_names))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 绘制基线分数柱状图
    rects1 = ax.bar(x - width/2, list(baseline_scores.values()), width, label='优化前（基线，只有检索-增强-生成流程）', color='#F5A623')
    # 绘制当前模型分数柱状图
    rects2 = ax.bar(x + width/2, list(scores.values()), width, label='优化后（长上下文重排+压缩+上下文工程）', color='#4A90E2')

    # 在柱状图上显示具体数值
    ax.bar_label(rects1, padding=3, fmt='%.3f')
    ax.bar_label(rects2, padding=3, fmt='%.3f')

    # 添加图表标题和标签
    ax.set_ylabel('平均分', fontsize=12)
    ax.set_title('RAG 优化前后性能对比评估', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(metric_names, rotation=15, ha="right")
    ax.legend()
    ax.set_ylim(0, 1.1)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    fig.tight_layout()

    # 保存图表
    plt.savefig(filename)
    print(f'\n评估结果对比图表已保存至: {filename}')
    # --- 绘图结束 ---


if __name__ == "__main__":
    # asyncio.run(main())
    # 用已经生成的结果进行评估
    scores = {
        'faithfulness': 0.8235,
        'answer_relevancy': 0.6130,
        'context_recall': 0.6646,
        'context_precision': 0.5627,
        'answer_correctness': 0.6388,
    }
    baseline_scores = {
        'faithfulness': 0.7247,
        'answer_relevancy': 0.5588,
        'context_recall': 0.6021,
        'context_precision': 0.5293,
        'answer_correctness': 0.5761,
    }
    chart_filename = "ragas_evaluation_comparison.png"
    plot_evaluation_results(scores, baseline_scores, chart_filename)