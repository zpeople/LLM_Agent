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


from crewai import Agent,LLM
import estate_tools  as ET
from dotenv import load_dotenv  


# In[ ]:


load_dotenv()
BASE_URL= os.getenv("BASE_URL")
ONLINE_MODEL_NAME = os.getenv("ONLINE_MODEL_NAME")
api_key = ( os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY" ) ) 


llm = LLM(
            base_url=BASE_URL,
            api_key=api_key,
            model="openai/"+ONLINE_MODEL_NAME,  # 本次使用的模型
            # temperature=0.7,  
            # timeout=None,
            # max_retries=2,
        )


# In[ ]:


# 定义智能体
class RealEstateAgents:
    @staticmethod
    def intent_recognition_agent():
        """意图识别智能体：分析用户输入，确定用户意图"""
        return Agent(
            role="房产意图识别专家",
            goal="准确识别用户在房产方面的具体意图，包括购房、租房、查询房价、计算贷款等",
            backstory="你是一位经验丰富的房产咨询意图分析专家，擅长从用户的提问中准确识别其真实需求和意图。",
            llm=llm,
            tools=[],  # 意图识别不需要工具，仅分析文本
            verbose=True,
            allow_delegation=False
        )
    
    @staticmethod
    def conversation_planner_agent():
        """对话规划智能体：规划对话流程，确定下一步行动"""
        return Agent(
            role="房产对话规划专家",
            goal="根据用户意图和当前对话状态，规划下一步对话策略和需要获取的信息",
            backstory="你是一位擅长房产咨询对话流程设计的专家，能够根据用户需求设计最优对话路径。",
            llm=llm,
            tools=[],  # 规划不需要工具
            verbose=True,
            allow_delegation=True,
            max_iter=3
        )
    
    @staticmethod
    def property_consultant_agent():
        """房产咨询智能体：提供房产信息和建议"""
        return Agent(
            role="房产咨询顾问",
            goal="为用户提供详细的房产信息、市场分析和专业建议",
            backstory="你是一位资深房产顾问，拥有丰富的房产知识和市场经验，能够解答各种房产问题。",
            llm=llm,
            tools=[ET.query_property_info,ET.calculate_mortgage,ET.get_market_trends],
            verbose=True,
            allow_delegation=False
        )
    
    @staticmethod
    def mortgage_expert_agent():
        """房贷专家智能体：提供贷款计算和建议"""
        return Agent(
            role="房贷专家",
            goal="为用户提供准确的房贷计算和贷款方案建议。"
             "如果用户未提供完整参数，可基于合理假设补充数据进行计算。"
             "需支持两种还款方式计算："
             "'equal_principal_interest'（等额本息）和'equal_principal'（等额本金）。"
             "房贷利率采用最新市场数据。",
            backstory="你是一位银行房贷部门的资深专家，拥有10年以上从业经验，精通各类房贷产品特性和计算方式，能够根据用户情况提供最优贷款建议。",
            llm=llm,
            tools=[ET.calculate_mortgage],  # 主要使用房贷计算工具
            verbose=True,
            allow_delegation=False
        )

