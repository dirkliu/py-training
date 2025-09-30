import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# 读取预测结果
df = pd.read_csv('factor_result2.csv')
df['report_date'] = pd.to_datetime(df['report_date'])

# 创建图表
fig, ax = plt.subplots(figsize=(12, 6))

# 绘制申购和赎回曲线
ax.plot(df['report_date'], df['purchase'], marker='o', label='申购金额', linewidth=2)
ax.plot(df['report_date'], df['redeem'], marker='s', label='赎回金额', linewidth=2)

# 设置图表标题和标签
ax.set_title('2014年9月申购赎回金额预测结果', fontsize=16, fontweight='bold')
ax.set_xlabel('日期', fontsize=12)
ax.set_ylabel('金额', fontsize=12)

# 设置x轴日期格式
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))  # 每3天显示一个日期
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

# 添加网格
ax.grid(True, linestyle='--', alpha=0.7)

# 添加图例
ax.legend(loc='upper left')

# 自动调整布局
plt.tight_layout()

# 保存图表
plt.savefig('prediction_chart.png', dpi=300, bbox_inches='tight')

# 显示图表
plt.show()

print("图表已保存为 prediction_chart.png")