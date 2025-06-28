<template>
  <div class="markdown-test">
    <h1>Markdown 渲染测试</h1>
    
    <div class="test-section">
      <h2>状态显示测试</h2>
      <p>计算机科学协会状态: {{ getClubStatus('1') }}</p>
      <p>摄影艺术社状态: {{ getClubStatus('2') }}</p>
      <p>青年志愿者协会状态: {{ getClubStatus('3') }}</p>
      <el-button @click="testRouteJump2">测试跳转到计算机科学协会</el-button>
    </div>
    
    <div class="test-section">
      <h2>点击事件测试</h2>
      <div class="click-test-area" @click="handleClickTest">
        <p>点击这个区域测试点击事件是否正常工作</p>
        <p>点击次数: {{ clickCount }}</p>
      </div>
      <el-button @click="handleButtonClick">测试按钮点击</el-button>
    </div>
    
    <div class="test-section">
      <h2>路由跳转测试</h2>
      <el-button @click="testRouteJump">测试跳转到社团详情页</el-button>
      <el-button @click="testRouteJump2">测试跳转到社团详情页 (ID: 1)</el-button>
      <el-button @click="testRouteJump3">测试跳转到社团详情页 (ID: 2)</el-button>
    </div>
    
    <div class="test-section">
      <h2>Markdown 编辑器测试</h2>
      <MarkdownEditor
        v-model="testContent"
        :rows="10"
        placeholder="在这里输入Markdown内容进行测试..."
        :maxlength="3000"
      />
    </div>
    
    <div class="test-section">
      <h2>Markdown 渲染器测试</h2>
      <div class="renderer-demo">
        <MarkdownRenderer :content="testContent" />
      </div>
    </div>
    
    <div class="test-section">
      <h2>示例内容</h2>
      <el-button @click="loadExample">加载示例</el-button>
      <el-button @click="loadMathExample">加载数学公式示例</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import { mockClubs } from '@/utils/mockData'

const router = useRouter()
const testContent = ref('')
const clickCount = ref(0)

const getClubStatus = (clubId: string) => {
  const club = mockClubs.find(c => c.id === clubId)
  return club ? club.status : 'not_found'
}

const handleClickTest = () => {
  clickCount.value++
  console.log('点击测试区域，次数:', clickCount.value)
}

const handleButtonClick = () => {
  console.log('按钮点击测试')
  alert('按钮点击正常工作！')
}

const testRouteJump = () => {
  console.log('测试路由跳转...')
  try {
    router.push('/club/1')
    console.log('路由跳转成功')
  } catch (error) {
    console.error('路由跳转失败:', error)
  }
}

const testRouteJump2 = () => {
  console.log('测试路由跳转到社团ID: 1')
  try {
    router.push('/club/1')
    console.log('路由跳转成功')
  } catch (error) {
    console.error('路由跳转失败:', error)
  }
}

const testRouteJump3 = () => {
  console.log('测试路由跳转到社团ID: 2')
  try {
    router.push('/club/2')
    console.log('路由跳转成功')
  } catch (error) {
    console.error('路由跳转失败:', error)
  }
}

const loadExample = () => {
  testContent.value = `# 这是一个标题

## 二级标题

这是一段**粗体**文本和*斜体*文本。

### 代码示例

行内代码：\`console.log('Hello World')\`

代码块：
\`\`\`javascript
function hello() {
  console.log('Hello World!');
}
\`\`\`

### 列表

无序列表：
- 项目1
- 项目2
- 项目3

有序列表：
1. 第一项
2. 第二项
3. 第三项

### 引用

> 这是一个引用块
> 可以包含多行内容

### 链接和图片

[百度](https://www.baidu.com)

![示例图片](https://via.placeholder.com/300x200)

### 表格

| 姓名 | 年龄 | 职业 |
|------|------|------|
| 张三 | 25   | 工程师 |
| 李四 | 30   | 设计师 |
| 王五 | 28   | 产品经理 |
`
}

const loadMathExample = () => {
  testContent.value = `# 数学公式测试

## 行内数学公式

这是一个行内公式：$E = mc^2$

另一个行内公式：$\\sum_{i=1}^{n} x_i = x_1 + x_2 + \\cdots + x_n$

## 块级数学公式

二次方程求根公式：

$$
x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}
$$

积分公式：

$$
\\int_{a}^{b} f(x) dx = F(b) - F(a)
$$

矩阵：

$$
\\begin{pmatrix}
a & b \\\\
c & d
\\end{pmatrix}
$$

## 混合内容

在Markdown中，我们可以混合使用**文本格式**和数学公式：

- 列表项1：$\\alpha + \\beta = \\gamma$
- 列表项2：$\\frac{1}{2} + \\frac{1}{3} = \\frac{5}{6}$

> 引用中的公式：$\\lim_{x \\to \\infty} \\frac{1}{x} = 0$
`
}
</script>

<style scoped>
.markdown-test {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.test-section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background-color: #fafafa;
}

.test-section h2 {
  margin-bottom: 20px;
  color: #303133;
}

.renderer-demo {
  padding: 20px;
  background-color: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-height: 200px;
}

.el-button {
  margin-right: 10px;
}

.click-test-area {
  padding: 20px;
  background-color: #f0f9ff;
  border: 2px dashed #3b82f6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 16px;
}

.click-test-area:hover {
  background-color: #dbeafe;
  border-color: #1d4ed8;
}

.click-test-area p {
  margin: 8px 0;
  color: #1e40af;
  font-weight: 500;
}
</style>
