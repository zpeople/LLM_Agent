#!/usr/bin/env python
# coding: utf-8

# In[7]:


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


# In[ ]:


from crewai import Agent,LLM
import estate_tools  as ET
from dotenv import load_dotenv  
from pathlib import Path
import yaml


# In[9]:


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


# In[10]:


def get_agents_config(agents_config_path="./config/agents.yaml"):
    def load_yaml(config_path: Path):
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"File not found: {config_path}")
            raise
    try:
        agents_config = load_yaml(agents_config_path)
    except FileNotFoundError:
        print(
            f"Agent config file not found at {agents_config_path}. "
            "Proceeding with empty agent configurations."
        )
        agents_config = {}
    return agents_config
library_name="hahha"
agents_config =get_agents_config()


# In[11]:


# 定义智能体
class RealEstateAgents:
    @staticmethod
    def intent_recognition_agent():
        """意图识别智能体：分析用户输入，确定用户意图"""
        return Agent(
                    config=agents_config['intent'], 
                    llm=llm,
                    tools=[],  # 意图识别不需要工具，仅分析文本
                    verbose=True,
                    allow_delegation=False
                )
        
    @staticmethod
    def conversation_planner_agent():
        """对话规划智能体：规划对话流程，确定下一步行动"""
        return Agent(
                    config=agents_config['planner'], 
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
                    config=agents_config['consultant'], 
                    llm=llm,
                    tools=[ET.query_property_info,ET.calculate_mortgage,ET.get_market_trends],
                    verbose=True,
                    allow_delegation=False
                )
    
    @staticmethod
    def mortgage_expert_agent():
        """房贷专家智能体：提供贷款计算和建议"""
        return Agent(
                    config=agents_config['mortgage'], 
                    llm=llm,
                    tools=[ET.calculate_mortgage],  # 主要使用房贷计算工具
                    verbose=True,
                    allow_delegation=False
                )

