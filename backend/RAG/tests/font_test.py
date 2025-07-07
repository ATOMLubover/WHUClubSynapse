import matplotlib.pyplot as plt
import matplotlib

# 注意：如果上一步找到的名称不同，请在这里替换
FONT_NAME = 'WenQuanYi Zen Hei' 

try:
    # 设置字体
    matplotlib.rcParams['font.sans-serif'] = [FONT_NAME]
    matplotlib.rcParams['axes.unicode_minus'] = False # 解决负号显示为方块的问题

    # 创建一个简单的图表
    plt.figure()
    plt.title("中文标题测试")
    plt.xlabel("X 轴")
    plt.ylabel("Y 轴")
    plt.plot([1, 2, 3], [4, 5, 1])
    
    # 保存图表
    test_filename = "font_test_output.png"
    plt.savefig(test_filename)
    
    print(f"成功：测试图表已保存至 '{test_filename}'。")
    print("请打开该图片文件，检查中文是否正常显示。")

except Exception as e:
    print(f"失败：创建图表时发生错误: {e}")
    print(f"请确认字体 '{FONT_NAME}' 已正确安装，且名称无误。")