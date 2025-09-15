#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
try:
    get_ipython
    current_dir = os.getcwd()
except NameError:
    current_dir = os.path.dirname(os.path.abspath(__file__))

# Set path，temporary path expansion
project_dir = os.path.abspath(os.path.join(current_dir, '..'))
if project_dir not in sys.path:
    sys.path.append(project_dir)



# In[2]:


from datetime import datetime
from tools.tool import skip_execution
from crewai.tools import BaseTool,tool
from rag_data import get_serarch


# In[3]:


IS_SKIP =True


# In[6]:


@tool("intent_recognition_tool")
def intent_recognition_tool(query: str):
    """根据用户输入查询相关对话，识别用户意图"""
    results = get_serarch(query=query,top_k=3)
    return results,  # 返回最相关的对话片段


# In[8]:


intent_recognition_tool.run("买套二的")


# In[ ]:


# 查询房产市场趋势
@tool("get_market_trends")
def get_market_trends(location, months=6):
    """查询指定区域最近几个月的房产市场趋势"""
    print(f"[工具调用] 查询市场趋势: 位置={location}, 时长={months}个月")
    
    # 模拟市场趋势数据
    trends = []
    current_date = datetime.now()
    for i in range(months, 0, -1):
        month_str = (current_date.month - i) % 12 + 1
        year_str = current_date.year
        if month_str > current_date.month:
            year_str -= 1
        trends.append({
            "month": f"{year_str}-{month_str:02d}",
            "average_price": 1000000 + i * 50000,
            "change_percent": round(i * 0.5, 2)
        })
    
    return trends


# In[ ]:


# 查询房产信息
# 模拟房产数据库工具
@tool("query_property_info")
def query_property_info(location, property_type, min_price, max_price):
    """查询指定区域、类型和价格范围内的房产信息"""
    print(f"[工具调用] 查询房产: 位置={location}, 类型={property_type}, 价格范围={min_price}-{max_price}")
    
    # 模拟数据库查询结果
    return [
        {
            "id": 1,
            "address": f"{location}中心区花园小区",
            "type": property_type,
            "price": min_price + (max_price - min_price) // 3,
            "bedrooms": 3,
            "bathrooms": 2,
            "area": 120,
            "description": f"{location}中心位置，交通便利，周边配套齐全"
        },
        {
            "id": 2,
            "address": f"{location}高新区科技苑",
            "type": property_type,
            "price": min_price + 2 * (max_price - min_price) // 3,
            "bedrooms": 4,
            "bathrooms": 2,
            "area": 150,
            "description": f"{location}高新区，环境优美，适合家庭居住"
        }
    ]


# In[ ]:


# 计算房贷
@tool("calculate_mortgage")
def calculate_mortgage(price, down_payment_percent, loan_term_years, interest_rate, payment_method='equal_principal_interest'):
    """
    计算房贷月供和总利息，支持等额本金和等额本息两种方式
    
    参数:
        price: 房价
        down_payment_percent: 首付比例(%)
        loan_term_years: 贷款年限
        interest_rate: 年利率(%)
        payment_method: 还款方式，'equal_principal_interest'为等额本息，'equal_principal'为等额本金
        
    返回:
        包含还款信息的字典
    """
    print(f"[工具调用] 计算房贷: 房价={price}, 首付比例={down_payment_percent}%, 贷款年限={loan_term_years}, 利率={interest_rate}%, 还款方式={payment_method}")
    
    # 计算基础数据
    down_payment = price * (down_payment_percent / 100)
    loan_amount = price - down_payment
    monthly_rate = (interest_rate / 100) / 12
    total_months = loan_term_years * 12
    
    # 确保贷款金额为正数
    if loan_amount <= 0:
        return {
            "down_payment": round(down_payment, 2),
            "loan_amount": 0,
            "monthly_payment": 0,
            "total_interest": 0,
            "total_payment": round(down_payment, 2),
            "payment_schedule": []
        }
    
    result = {
        "down_payment": round(down_payment, 2),
        "loan_amount": round(loan_amount, 2),
        "total_months": total_months,
        "monthly_rate": round(monthly_rate * 100, 4),  # 转换为百分比显示
    }
    
    # 等额本息: 每月还款额相同
    if payment_method == 'equal_principal_interest':
        # 计算月供
        if monthly_rate == 0:
            monthly_payment = loan_amount / total_months
        else:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** total_months) / \
                            ((1 + monthly_rate) ** total_months - 1)
        
        total_payment = monthly_payment * total_months
        total_interest = total_payment - loan_amount
        
        result.update({
            "monthly_payment": round(monthly_payment, 2),
            "total_interest": round(total_interest, 2),
            "total_payment": round(total_payment, 2),
            "payment_method": "等额本息"
        })
        
        # 生成还款计划表（前12期和最后一期）
        payment_schedule = []
        remaining_principal = loan_amount
        
        for month in range(1, total_months + 1):
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_principal -= principal_payment
            
            # 只保存前12期和最后一期，避免数据量过大
            if month <= 12 or month == total_months:
                payment_schedule.append({
                    "month": month,
                    "principal_payment": round(principal_payment, 2),
                    "interest_payment": round(interest_payment, 2),
                    "remaining_principal": round(remaining_principal, 2)
                })
        
        result["payment_schedule"] = payment_schedule
    
    # 等额本金: 每月还固定的本金和剩余本金产生的利息，月供逐月递减
    elif payment_method == 'equal_principal':
        monthly_principal = loan_amount / total_months
        total_payment = 0
        payment_schedule = []
        
        for month in range(1, total_months + 1):
            remaining_principal = loan_amount - monthly_principal * (month - 1)
            interest_payment = remaining_principal * monthly_rate
            monthly_payment = monthly_principal + interest_payment
            total_payment += monthly_payment
            
            # 只保存前12期和最后一期
            if month <= 12 or month == total_months:
                payment_schedule.append({
                    "month": month,
                    "principal_payment": round(monthly_principal, 2),
                    "interest_payment": round(interest_payment, 2),
                    "monthly_payment": round(monthly_payment, 2),
                    "remaining_principal": round(remaining_principal - monthly_principal, 2)
                })
        
        total_interest = total_payment - loan_amount
        
        result.update({
            "first_month_payment": round(payment_schedule[0]["monthly_payment"], 2),
            "last_month_payment": round(payment_schedule[-1]["monthly_payment"], 2),
            "total_interest": round(total_interest, 2),
            "total_payment": round(total_payment, 2),
            "payment_method": "等额本金"
        })
        
        result["payment_schedule"] = payment_schedule
    
    return result


# In[5]:


@skip_execution(IS_SKIP)
def test_mortgage():    
    # 测试等额本息
    result_epi = calculate_mortgage.run(
        price=500000, 
        down_payment_percent=30, 
        loan_term_years=20, 
        interest_rate=4.9,
        payment_method='equal_principal_interest'
    )
    print("等额本息结果:")
    print(f"首付: {result_epi['down_payment']}元")
    print(f"贷款金额: {result_epi['loan_amount']}元")
    print(f"月供: {result_epi['monthly_payment']}元")
    print(f"总利息: {result_epi['total_interest']}元")
    print(f"还款总额: {result_epi['total_payment']}元\n")
    
    # 测试等额本金
    result_ep = calculate_mortgage.run(
        price=500000, 
        down_payment_percent=30, 
        loan_term_years=20, 
        interest_rate=4.9,
        payment_method='equal_principal'
    )
    print("等额本金结果:")
    print(f"首付: {result_ep['down_payment']}元")
    print(f"贷款金额: {result_ep['loan_amount']}元")
    print(f"首月月供: {result_ep['first_month_payment']}元")
    print(f"末月月供: {result_ep['last_month_payment']}元")
    print(f"总利息: {result_ep['total_interest']}元")
    print(f"还款总额: {result_ep['total_payment']}元")
    
test_mortgage()

