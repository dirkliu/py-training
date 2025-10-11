import pandas as pd
import numpy as np
import os

# 读取 user_balance_table.csv 文件内容
data = pd.read_csv('user_balance_table.csv')
print(data.head());
print("__file__:", os.path.dirname(__file__));

a = np.array([[1, 2, 3], [4, 5, 6]])
print(a)