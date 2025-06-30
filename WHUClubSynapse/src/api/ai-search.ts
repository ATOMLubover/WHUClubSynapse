import type { 
  SmartSearchRequest, 
  SmartSearchResponse, 
  SmartSearchError, 
  SmartSearchSource,
  SideChatRequest,
  SideChatResponse,
  ChatMessage
} from '@/types'
import { getSmartSearchURL, getSideChatURL, getApiKey, isAiSearchEnabled, isSideChatEnabled } from '@/config/ai-search'
import { config } from '@/config'

// 检查是否使用Mock API
const getIsUsingMockAPI = () => {
  return config.apiMode === 'mock'
}

// 模拟延迟
const delay = (ms: number = config.mockDelay) => new Promise((resolve) => setTimeout(resolve, ms))

// AI智能搜索API
export const smartSearch = async (request: SmartSearchRequest): Promise<SmartSearchResponse> => {
  if (getIsUsingMockAPI()) {
    return await mockSmartSearch(request)
  }

  if (!isAiSearchEnabled()) {
    throw new Error('AI搜索功能未启用')
  }

  try {
    const response = await fetch(getSmartSearchURL(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': getApiKey(),
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData: SmartSearchError = await response.json()
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
    }

    const data: SmartSearchResponse = await response.json()
    return data
  } catch (error) {
    console.error('AI智能搜索请求失败:', error)
    throw error
  }
}

// 侧边栏对话API
export const sideChat = async (request: SideChatRequest): Promise<SideChatResponse> => {
  if (getIsUsingMockAPI()) {
    return await mockSideChat(request)
  }

  if (!isSideChatEnabled()) {
    throw new Error('侧边栏对话功能未启用')
  }

  try {
    const response = await fetch(getSideChatURL(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': getApiKey(),
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData: SmartSearchError = await response.json()
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
    }

    const data: SideChatResponse = await response.json()
    return data
  } catch (error) {
    console.error('侧边栏对话请求失败:', error)
    throw error
  }
}

// Mock AI智能搜索
export const mockSmartSearch = async (request: SmartSearchRequest): Promise<SmartSearchResponse> => {
  await delay(2000) // 模拟AI处理时间

  // 根据查询内容生成不同的回答
  const query = request.query.toLowerCase()
  let answer = ''
  let source: SmartSearchSource[] = []

  if (query.includes('社团') && query.includes('创建')) {
    answer = `### **核心摘要**
要创建一个新的社团，您需要先提交一份包含社团基本信息的申请表，并通过管理员的审核。

### **关键信息/步骤**
1. **登录系统**：使用您的学号和密码登录社团管理系统。
2. **进入申请页面**：在导航栏找到"社团管理"，点击"创建社团"。
3. **填写申请表**：按要求填写社团名称、简介、负责人信息等。
4. **提交审核**：确认信息无误后，点击提交，等待管理员审核。

### **实用技巧/补充**
- 建议在申请前准备好详细的社团章程和活动计划，这会加快审核过程。
- 您可以在"我的申请"页面随时查看审核进度。`

    source = [
      {
        id: 'doc1_chunk3',
        content: '社团创建流程：用户需在系统中填写并提交《社团成立申请表》。管理员将在后台收到申请并进行审核，审核结果将通过系统消息通知申请人...',
        metadata: {
          source: '社团管理手册.pdf',
          page: 5
        }
      }
    ]
  } else if (query.includes('加入') || query.includes('申请')) {
    answer = `### **加入社团流程**
1. **浏览社团**：在首页或搜索页面浏览感兴趣的社团。
2. **查看详情**：点击社团卡片查看详细信息。
3. **提交申请**：点击"申请加入"按钮，填写申请理由。
4. **等待审核**：社团管理员会在3-5个工作日内审核您的申请。
5. **接收通知**：审核结果会通过系统消息通知您。

### **申请建议**
- 认真填写申请理由，说明您对该社团的兴趣和期望。
- 确保个人信息完整，包括学号、联系方式等。`

    source = [
      {
        id: 'doc2_chunk1',
        content: '社团申请流程：用户选择心仪社团后，点击申请加入，填写个人信息和申请理由。社团管理员审核通过后，用户正式成为社团成员...',
        metadata: {
          source: '用户操作指南.pdf',
          page: 12
        }
      }
    ]
  } else if (query.includes('活动') || query.includes('event')) {
    answer = `### **社团活动管理**
1. **发布活动**：社团管理员可以在社团页面发布活动信息。
2. **活动类型**：包括例会、培训、比赛、联谊等多种类型。
3. **报名参与**：成员可以查看活动详情并报名参加。
4. **活动记录**：系统会自动记录活动参与情况。

### **活动建议**
- 提前发布活动信息，给成员充分的准备时间。
- 活动结束后及时总结，分享活动照片和成果。`

    source = [
      {
        id: 'doc3_chunk2',
        content: '社团活动是增强成员凝聚力的重要方式。管理员可以发布各类活动，成员可以报名参与，系统会记录活动历史...',
        metadata: {
          source: '活动管理规范.pdf',
          page: 8
        }
      }
    ]
  } else {
    answer = `### **智能搜索帮助**
我理解您的问题，但可能需要更具体的信息。您可以尝试以下搜索：

- **社团相关**：如何创建社团、如何加入社团、社团活动等
- **系统功能**：用户管理、申请审核、数据统计等
- **操作指南**：登录注册、个人信息设置、权限管理等

### **搜索技巧**
- 使用关键词搜索，如"社团"、"申请"、"活动"等
- 描述具体问题，如"如何修改社团信息"
- 查看相关文档和帮助页面`

    source = [
      {
        id: 'doc4_chunk1',
        content: '系统提供了丰富的帮助文档和操作指南，用户可以通过搜索功能快速找到所需信息...',
        metadata: {
          source: '系统帮助文档.pdf',
          page: 1
        }
      }
    ]
  }

  return {
    answer,
    source
  }
}

// Mock 侧边栏对话
export const mockSideChat = async (request: SideChatRequest): Promise<SideChatResponse> => {
  await delay(1500) // 模拟AI处理时间

  const query = request.query.toLowerCase()
  const history = request.history || []
  
  let answer = ''
  let source: SmartSearchSource[] = []

  // 根据历史对话和当前查询生成上下文相关的回答
  if (query.includes('审核') && query.includes('多久')) {
    // 如果之前讨论过社团创建，现在问审核时间
    const hasCreationContext = history.some(msg => 
      msg.role === 'user' && msg.content.toLowerCase().includes('创建')
    )
    
    if (hasCreationContext) {
      answer = `### **核心摘要**
社团创建的审核过程通常需要3到5个工作日。

### **关键信息/步骤**
1. **自动流转**：您提交申请后，系统会自动将申请流转至对应的管理部门。
2. **人工审核**：相关负责老师会在此期间对您提交的材料进行人工审核。
3. **结果通知**：审核完成后，无论通过与否，系统都会通过站内信和邮件通知您。

### **实用技巧/补充**
- 如果超过5个工作日仍未收到通知，建议您通过系统的申诉渠道联系管理员进行咨询。
- 审核期间请保持联系方式畅通，以便及时接收通知。`

      source = [
        {
          id: 'doc1_chunk4',
          content: '关于审核时效的说明：所有社团成立申请，将在提交后的3-5个工作日内完成审批流程。特殊情况除外。',
          metadata: {
            source: '社团管理手册.pdf',
            page: 6
          }
        }
      ]
    } else {
      answer = `### **审核时间说明**
不同类型的审核有不同的时间要求：

**社团申请审核**：3-5个工作日
**活动申请审核**：1-2个工作日
**内容审核**：24小时内

### **影响因素**
- 申请材料的完整性
- 当前申请数量
- 节假日和特殊时期

### **建议**
- 提前准备完整的申请材料
- 在非高峰期提交申请
- 保持联系方式畅通`

      source = [
        {
          id: 'doc5_chunk2',
          content: '审核时间标准：社团申请3-5个工作日，活动申请1-2个工作日，内容审核24小时内完成。',
          metadata: {
            source: '审核流程规范.pdf',
            page: 3
          }
        }
      ]
    }
  } else if (query.includes('材料') || query.includes('准备')) {
    answer = `### **申请材料清单**
根据您之前提到的社团创建，需要准备以下材料：

**必需材料：**
1. 社团名称和简介
2. 负责人基本信息
3. 社团章程草案
4. 活动计划书

**建议材料：**
1. 社团Logo设计
2. 成员招募计划
3. 经费预算方案
4. 指导教师信息

### **材料要求**
- 所有材料必须真实有效
- 文件格式支持PDF、Word、图片等
- 单个文件大小不超过10MB

### **提交建议**
- 材料准备充分后再提交申请
- 可以咨询已有社团的经验
- 保持材料的专业性和完整性`

    source = [
      {
        id: 'doc6_chunk1',
        content: '申请材料要求：社团名称、简介、负责人信息、章程草案、活动计划书为必需材料。',
        metadata: {
          source: '申请材料指南.pdf',
          page: 2
        }
      }
    ]
  } else if (query.includes('拒绝') || query.includes('失败')) {
    answer = `### **申请被拒绝的常见原因**
根据经验，申请被拒绝的主要原因包括：

**材料问题：**
1. 申请材料不完整或格式错误
2. 社团名称与现有社团重复
3. 章程内容不符合学校规定

**内容问题：**
1. 社团性质与学校政策不符
2. 活动计划不够具体可行
3. 负责人资质不符合要求

### **解决方案**
1. **仔细检查材料**：确保所有必需材料都已提交
2. **修改完善内容**：根据拒绝原因调整申请内容
3. **重新提交申请**：修改后可以重新提交申请
4. **咨询管理员**：如有疑问可以联系管理员咨询

### **预防措施**
- 提交前仔细检查所有材料
- 参考成功案例的申请材料
- 确保社团活动符合学校规定`

    source = [
      {
        id: 'doc7_chunk3',
        content: '申请被拒绝的常见原因：材料不完整、名称重复、内容不符合规定等。建议仔细检查后重新提交。',
        metadata: {
          source: '申请审核标准.pdf',
          page: 8
        }
      }
    ]
  } else {
    // 通用回答
    answer = `### **继续对话**
我理解您的问题。基于我们之前的对话，我可以为您提供更具体的帮助。

### **相关建议**
- 如果您想了解更多细节，请具体说明您的问题
- 我可以根据您的具体情况提供个性化建议
- 您可以随时询问其他相关问题

### **对话技巧**
- 提供更多上下文信息
- 描述您的具体需求
- 我会结合历史对话为您提供更精准的回答`

    source = [
      {
        id: 'doc8_chunk1',
        content: '智能对话系统会根据历史对话内容，为用户提供更精准和个性化的回答。',
        metadata: {
          source: '智能对话指南.pdf',
          page: 1
        }
      }
    ]
  }

  return {
    answer,
    source
  }
} 