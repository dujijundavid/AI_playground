import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 基础参数配置
house_price = 2_000_000      # 房价（元）
down_payment = 500_000       # 首付（元）
loan_amount = house_price - down_payment  # 贷款总额（元）
rent = 3200                  # 月租金（元）
months = 360                 # 贷款期限（30年）
salary_monthly = 8400        # 月公积金缴存额
current_balance = 210_000    # 当前公积金余额

# 可调节参数
investment_return = 0.015    # 年化投资回报率（1.5%）
house_growth_rate = 0.03     # 房价年增长率（3%）
rent_growth_rate = 0.02      # 租金年增长率（2%）
commercial_rate = 0.0315     # 商业贷款利率（3.15%）
provident_rate = 0.0285      # 公积金贷款利率（2.85%）
property_tax_rate = 0.01     # 房产税（1%）
maintenance_fee = 2.5        # 物业费（元/平米/月）
house_area = 80              # 房屋面积（平米）

# 贷款月供计算器
def calculate_monthly_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 12
    n_payments = years * 12
    payment = principal * monthly_rate * (1 + monthly_rate)**n_payments / ((1 + monthly_rate)**n_payments - 1)
    return payment

# 组合贷款计算（公积金120万+商贷30万）
provident_loan = 1_200_000
commercial_loan = loan_amount - provident_loan

provident_payment = calculate_monthly_payment(provident_loan, provident_rate, 30)
commercial_payment = calculate_monthly_payment(commercial_loan, commercial_rate, 30)
total_payment = provident_payment + commercial_payment

# 现金流生成器
def generate_scenarios():
    df = pd.DataFrame(index=range(months))
    
    # 购房场景现金流
    df['购房_月供'] = -total_payment
    df['购房_公积金冲抵'] = np.minimum(salary_monthly, total_payment)
    df['购房_净现金流出'] = df['购房_月供'] - df['购房_公积金冲抵']
    
    # 房产价值增长
    df['房产净值'] = house_price * (1 + house_growth_rate/12)**df.index
    
    # 房产税和物业费
    df['房产税'] = -df['房产净值'] * property_tax_rate / 12
    df['物业费'] = -maintenance_fee * house_area
    df['购房_额外支出'] = df['房产税'] + df['物业费']
    
    # 租房场景现金流
    df['租房_租金'] = -rent * (1 + rent_growth_rate/12)**df.index
    df['租房_投资本金'] = down_payment * (1 + investment_return/12)**df.index
    df['租房_公积金余额'] = current_balance + (salary_monthly - rent) * (df.index + 1)
    
    # 个税抵扣（假设租房可抵扣1000元/月）
    df['租房_个税抵扣'] = 1000
    df['租房_净现金流出'] = df['租房_租金'] - df['租房_个税抵扣']
    
    return df

df = generate_scenarios()

# 关键指标计算
df['购房净资产'] = df['房产净值'] - (house_price - down_payment) - df['购房_净现金流出'].cumsum() + df['购房_额外支出'].cumsum()
df['租房净资产'] = df['租房_投资本金'] + df['租房_公积金余额']

# 月度现金流对比图
plt.figure(figsize=(12, 6))
plt.plot(df['购房_净现金流出'].cumsum(), label='购房累计支出')
plt.plot(df['租房_净现金流出'].cumsum(), label='租房累计支出')
plt.xlabel('月份')
plt.ylabel('累计现金流（元）')
plt.title('购房 vs 租房 长期现金流对比')
plt.legend()
plt.grid(True)
plt.show()

# 净资产对比图
plt.figure(figsize=(12, 6))
plt.plot(df['购房净资产'], label='购房净资产')
plt.plot(df['租房净资产'], label='租房净资产')
plt.xlabel('月份')
plt.ylabel('净资产（元）')
plt.title('长期净资产对比')
plt.legend()
plt.grid(True)
plt.show()

# 敏感性分析工具
def sensitivity_analysis(param_range, param_name):
    results = []
    for value in param_range:
        global investment_return, house_growth_rate, rent_growth_rate
        if param_name == 'investment_return':
            investment_return = value
        elif param_name == 'house_growth_rate':
            house_growth_rate = value
        elif param_name == 'rent_growth_rate':
            rent_growth_rate = value
            
        df = generate_scenarios()
        final_diff = df['购房净资产'].iloc[-1] - df['租房净资产'].iloc[-1]
        results.append(final_diff)
    
    plt.plot(param_range, results, 'o-')
    plt.xlabel(param_name)
    plt.ylabel('购房净资产优势（元）')
    plt.title(f'参数敏感性分析: {param_name}')
    plt.grid(True)
    plt.show()

# 示例：分析投资回报率影响
sensitivity_analysis(np.linspace(0.01, 0.05, 5), 'investment_return')

# 示例：分析房价增长率影响
sensitivity_analysis(np.linspace(0.01, 0.05, 5), 'house_growth_rate')

# 示例：分析租金增长率影响
sensitivity_analysis(np.linspace(0.01, 0.05, 5), 'rent_growth_rate')