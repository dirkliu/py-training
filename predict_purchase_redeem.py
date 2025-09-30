import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data():
    """
    生成示例历史数据用于演示
    实际使用时应替换为真实的历史数据
    """
    # 生成2013-01-01到2014-08-31的日期
    start_date = datetime(2013, 1, 1)
    end_date = datetime(2014, 8, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 生成随机的申购和赎回数据
    np.random.seed(42)  # 固定随机种子以保证结果可重现
    purchase = np.random.normal(1000000, 200000, len(date_range))  # 均值100万，标准差20万
    redeem = np.random.normal(800000, 150000, len(date_range))     # 均值80万，标准差15万
    
    # 添加一些周期性模式
    # 周期性因子：周一到周日的倍数
    weekday_factors = [1.1, 0.9, 0.95, 1.0, 1.05, 1.15, 0.85]  # 周一到周日的因子
    # 月份中每天的因子（简化为前15天和后15天）
    day_factors = [1.0 + 0.02 * (i % 10) for i in range(1, 32)]  # 1号到31号的因子
    
    for i, date in enumerate(date_range):
        # 应用weekday因子
        weekday_factor = weekday_factors[date.weekday()]
        purchase[i] *= weekday_factor
        redeem[i] *= weekday_factor
        
        # 应用day因子
        day_factor = day_factors[date.day - 1]
        purchase[i] *= day_factor
        redeem[i] *= day_factor
    
    df = pd.DataFrame({
        'report_date': date_range,
        'purchase': purchase,
        'redeem': redeem
    })
    
    return df

def calculate_period_factors(df):
    """
    计算周期因子
    :param df: 包含历史数据的DataFrame
    :return: weekday因子、day因子、month_week因子和holiday因子
    """
    # 只使用2014-03-01到2014-08-31的数据计算因子
    filtered_df = df[(df['report_date'] >= '2014-03-01') & (df['report_date'] <= '2014-08-31')]
    
    # 计算weekday因子（周一到周日）
    filtered_df['weekday'] = filtered_df['report_date'].dt.weekday
    weekday_purchase_mean = filtered_df.groupby('weekday')['purchase'].mean()
    weekday_redeem_mean = filtered_df.groupby('weekday')['redeem'].mean()
    
    # 计算day因子（1号到31号）
    filtered_df['day'] = filtered_df['report_date'].dt.day
    day_purchase_mean = filtered_df.groupby('day')['purchase'].mean()
    day_redeem_mean = filtered_df.groupby('day')['redeem'].mean()
    
    # 计算月内周期因子（将月份分为前三天、中间和后三天）
    def get_month_period(day):
        if day <= 3:
            return 'month_beginning'
        elif day >= 28:
            return 'month_end'
        else:
            return 'month_middle'
    
    filtered_df['month_period'] = filtered_df['report_date'].dt.day.apply(get_month_period)
    month_period_purchase_mean = filtered_df.groupby('month_period')['purchase'].mean()
    month_period_redeem_mean = filtered_df.groupby('month_period')['redeem'].mean()
    
    # 计算季度因子
    filtered_df['quarter'] = filtered_df['report_date'].dt.quarter
    quarter_purchase_mean = filtered_df.groupby('quarter')['purchase'].mean()
    quarter_redeem_mean = filtered_df.groupby('quarter')['redeem'].mean()
    
    # 简化的节假日因子（这里以五一劳动节为例）
    # 在实际应用中，应该使用完整的节假日列表
    def is_holiday(date):
        # 五一劳动节 (5月1日)
        if (date.month == 5 and date.day == 1):
            return 'May_Day'
        # 国庆节 (10月1日)
        elif (date.month == 10 and date.day == 1):
            return 'National_Day'
        else:
            return 'Regular_Day'
    
    filtered_df['holiday'] = filtered_df['report_date'].apply(is_holiday)
    holiday_purchase_mean = filtered_df.groupby('holiday')['purchase'].mean()
    holiday_redeem_mean = filtered_df.groupby('holiday')['redeem'].mean()
    
    return (weekday_purchase_mean, weekday_redeem_mean, 
            day_purchase_mean, day_redeem_mean,
            month_period_purchase_mean, month_period_redeem_mean,
            quarter_purchase_mean, quarter_redeem_mean,
            holiday_purchase_mean, holiday_redeem_mean)

def predict_september_2014(weekday_factors, day_factors, month_period_factors, quarter_factors, holiday_factors):
    """
    预测2014年9月的申购和赎回金额
    :param weekday_factors: 每周每天的因子
    :param day_factors: 每月每天的因子
    :param month_period_factors: 月内周期因子
    :param quarter_factors: 季度因子
    :param holiday_factors: 节假日因子
    :return: 预测结果DataFrame
    """
    # 生成2014年9月的日期
    sep_2014_dates = pd.date_range(start='2014-09-01', end='2014-09-30', freq='D')
    predictions = []
    
    # 定义月内周期函数
    def get_month_period(day):
        if day <= 3:
            return 'month_beginning'
        elif day >= 28:
            return 'month_end'
        else:
            return 'month_middle'
    
    for date in sep_2014_dates:
        weekday = date.weekday()
        day = date.day
        month_period = get_month_period(day)
        quarter = date.quarter
        
        # 判断是否为节假日
        def is_holiday(date):
            # 国庆节 (10月1日)
            if (date.month == 10 and date.day == 1):
                return 'National_Day'
            else:
                return 'Regular_Day'
        
        holiday = is_holiday(date)
        
        # 获取对应的因子
        weekday_purchase_factor = weekday_factors[0][weekday]
        weekday_redeem_factor = weekday_factors[1][weekday]
        day_purchase_factor = day_factors[0][day] if day in day_factors[0] else day_factors[0].mean()
        day_redeem_factor = day_factors[1][day] if day in day_factors[1] else day_factors[1].mean()
        
        # 获取月内周期因子
        month_period_purchase_factor = month_period_factors[0][month_period] if month_period in month_period_factors[0] else month_period_factors[0].mean()
        month_period_redeem_factor = month_period_factors[1][month_period] if month_period in month_period_factors[1] else month_period_factors[1].mean()
        
        # 获取季度因子
        quarter_purchase_factor = quarter_factors[0][quarter] if quarter in quarter_factors[0] else quarter_factors[0].mean()
        quarter_redeem_factor = quarter_factors[1][quarter] if quarter in quarter_factors[1] else quarter_factors[1].mean()
        
        # 获取节假日因子
        holiday_purchase_factor = holiday_factors[0][holiday] if holiday in holiday_factors[0] else holiday_factors[0].mean()
        holiday_redeem_factor = holiday_factors[1][holiday] if holiday in holiday_factors[1] else holiday_factors[1].mean()
        
        # 使用加权平均法结合所有因子
        # 为不同因子分配权重：weekday(25%), day(25%), month_period(20%), quarter(15%), holiday(15%)
        predicted_purchase = (0.25 * weekday_purchase_factor + 
                             0.25 * day_purchase_factor + 
                             0.20 * month_period_purchase_factor + 
                             0.15 * quarter_purchase_factor + 
                             0.15 * holiday_purchase_factor)
        
        predicted_redeem = (0.25 * weekday_redeem_factor + 
                           0.25 * day_redeem_factor + 
                           0.20 * month_period_redeem_factor + 
                           0.15 * quarter_redeem_factor + 
                           0.15 * holiday_redeem_factor)
        
        predictions.append({
            'report_date': date.strftime('%Y-%m-%d'),
            'purchase': predicted_purchase,
            'redeem': predicted_redeem
        })
    
    return pd.DataFrame(predictions)

def calculate_confidence(df, weekday_factors, day_factors, month_period_factors, quarter_factors, holiday_factors):
    """
    计算预测置信度
    :param df: 历史数据
    :param weekday_factors: 周期因子
    :param day_factors: 日期因子
    :param month_period_factors: 月内周期因子
    :param quarter_factors: 季度因子
    :param holiday_factors: 节假日因子
    :return: 置信度评分(0-100)
    """
    # 计算历史数据的平均值和标准差作为基准
    purchase_mean = df['purchase'].mean()
    purchase_std = df['purchase'].std()
    redeem_mean = df['redeem'].mean()
    redeem_std = df['redeem'].std()
    
    # 计算因子的平均值和标准差
    weekday_purchase_mean = weekday_factors[0].mean()
    weekday_purchase_std = weekday_factors[0].std()
    weekday_redeem_mean = weekday_factors[1].mean()
    weekday_redeem_std = weekday_factors[1].std()
    day_purchase_mean = day_factors[0].mean()
    day_purchase_std = day_factors[0].std()
    day_redeem_mean = day_factors[1].mean()
    day_redeem_std = day_factors[1].std()
    
    # 计算新增因子的平均值和标准差
    month_period_purchase_mean = month_period_factors[0].mean()
    month_period_purchase_std = month_period_factors[0].std()
    month_period_redeem_mean = month_period_factors[1].mean()
    month_period_redeem_std = month_period_factors[1].std()
    quarter_purchase_mean = quarter_factors[0].mean()
    quarter_purchase_std = quarter_factors[0].std()
    quarter_redeem_mean = quarter_factors[1].mean()
    quarter_redeem_std = quarter_factors[1].std()
    holiday_purchase_mean = holiday_factors[0].mean()
    holiday_purchase_std = holiday_factors[0].std()
    holiday_redeem_mean = holiday_factors[1].mean()
    holiday_redeem_std = holiday_factors[1].std()
    
    # 计算变异系数（标准差/平均值），衡量因子的稳定性
    # 变异系数越小，说明因子越稳定，置信度越高
    if purchase_mean > 0:
        weekday_purchase_cv = weekday_purchase_std / weekday_purchase_mean if weekday_purchase_mean != 0 else 0
        day_purchase_cv = day_purchase_std / day_purchase_mean if day_purchase_mean != 0 else 0
        month_period_purchase_cv = month_period_purchase_std / month_period_purchase_mean if month_period_purchase_mean != 0 else 0
        quarter_purchase_cv = quarter_purchase_std / quarter_purchase_mean if quarter_purchase_mean != 0 else 0
        holiday_purchase_cv = holiday_purchase_std / holiday_purchase_mean if holiday_purchase_mean != 0 else 0
        # 置信度与变异系数成反比，同时也考虑历史数据的稳定性
        purchase_cv = purchase_std / purchase_mean if purchase_mean != 0 else 0
        purchase_confidence = 100 * (1 - min(1, (weekday_purchase_cv + day_purchase_cv + month_period_purchase_cv + quarter_purchase_cv + holiday_purchase_cv) / 5)) * (1 - min(1, purchase_cv))
    else:
        purchase_confidence = 0
    
    if redeem_mean > 0:
        weekday_redeem_cv = weekday_redeem_std / weekday_redeem_mean if weekday_redeem_mean != 0 else 0
        day_redeem_cv = day_redeem_std / day_redeem_mean if day_redeem_mean != 0 else 0
        month_period_redeem_cv = month_period_redeem_std / month_period_redeem_mean if month_period_redeem_mean != 0 else 0
        quarter_redeem_cv = quarter_redeem_std / quarter_redeem_mean if quarter_redeem_mean != 0 else 0
        holiday_redeem_cv = holiday_redeem_std / holiday_redeem_mean if holiday_redeem_mean != 0 else 0
        # 置信度与变异系数成反比，同时也考虑历史数据的稳定性
        redeem_cv = redeem_std / redeem_mean if redeem_mean != 0 else 0
        redeem_confidence = 100 * (1 - min(1, (weekday_redeem_cv + day_redeem_cv + month_period_redeem_cv + quarter_redeem_cv + holiday_redeem_cv) / 5)) * (1 - min(1, redeem_cv))
    else:
        redeem_confidence = 0
    
    # 确保置信度在0-100范围内
    purchase_confidence = max(0, min(100, purchase_confidence))
    redeem_confidence = max(0, min(100, redeem_confidence))
    
    return purchase_confidence, redeem_confidence

def main():
    # 生成示例数据（实际使用时应加载真实数据）
    df = generate_sample_data()
    
    # 计算周期因子（只使用2014-03-01到2014-08-31的数据）
    (weekday_purchase_mean, weekday_redeem_mean, 
     day_purchase_mean, day_redeem_mean,
     month_period_purchase_mean, month_period_redeem_mean,
     quarter_purchase_mean, quarter_redeem_mean,
     holiday_purchase_mean, holiday_redeem_mean) = calculate_period_factors(df)
    
    # 预测2014年9月
    predictions = predict_september_2014(
        (weekday_purchase_mean, weekday_redeem_mean), 
        (day_purchase_mean, day_redeem_mean),
        (month_period_purchase_mean, month_period_redeem_mean),
        (quarter_purchase_mean, quarter_redeem_mean),
        (holiday_purchase_mean, holiday_redeem_mean)
    )
    
    # 计算置信度
    purchase_conf, redeem_conf = calculate_confidence(df, 
        (weekday_purchase_mean, weekday_redeem_mean), 
        (day_purchase_mean, day_redeem_mean),
        (month_period_purchase_mean, month_period_redeem_mean),
        (quarter_purchase_mean, quarter_redeem_mean),
        (holiday_purchase_mean, holiday_redeem_mean))
    
    # 输出结果
    print(f"预测结果已保存到 factor_result2.csv")
    print(f"申购预测置信度: {purchase_conf:.2f}%")
    print(f"赎回预测置信度: {redeem_conf:.2f}%")
    
    # 保存到CSV文件
    predictions.to_csv('factor_result2.csv', index=False)

if __name__ == "__main__":
    main()