#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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


from crewai import Task, Crew, Process
from estate_agents import RealEstateAgents 
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
from tool import skip_execution
IS_SKIP=True


# In[ ]:


class RealEstateCrew:
    def __init__(self, user_query):
        self.user_query = user_query
        self.output_path ="./result.md"
        self.agents = self._initialize_agents()
        self.intent_task =self._update_intent_task()
        self.tasks = self._create_tasks()
        self.crew = self._create_crew()
        self.history = []

    def _initialize_agents(self):
        """初始化所有智能体"""
        return {
            "intent_recognizer": RealEstateAgents.intent_recognition_agent(),
            "planner": RealEstateAgents.conversation_planner_agent(),
            "consultant": RealEstateAgents.property_consultant_agent(),
            "mortgage_expert": RealEstateAgents.mortgage_expert_agent()
        }
    
    def _update_intent_task(self):
        # 任务1：识别用户意图 
        identify_intent = Task(
            description=f"分析用户查询: '{self.user_query}'，确定用户的具体意图。可能的意图包括：购房、租房、查询特定区域房价、了解市场趋势、计算房贷等。",
            expected_output="明确的用户意图分类，例如：'用户想查询某地的住宅房价'，",
            agent=self.agents["intent_recognizer"]
        )
        return identify_intent
  
    def _create_tasks(self):
        """创建任务"""
        # 任务2：规划对话策略
        plan_conversation = Task(
            description="""根据识别出的用户意图，提取用户意图中位置、面积、户型、朝向等和购房有关的信息，规划下一步对话策略。
                            0. 检查是否已获取足够信息（位置、面积、户型、预算等关键信息）
                            1. 如果用户说"没有其他需求"类似语句，就直接标志"无需追问",把客户需求信息汇总给房产咨询用
                            2. 如果信息不足，明确需要追问的具体内容（例如："需要询问用户的购房预算和意向区域"）
                            3. 如果信息充足，直接生成"无需追问"标记并汇总信息准备回答框架
                            
                            输出格式要求：
                            - 第一行必须是"需要追问"或"无需追问"
                            - 后续内容为具体说明（追问的问题或回答框架）
                            - 追问的问题的格式为'{ask:问题内容}'
                            - 汇总的信息框架按照要素组装成键值对
                            """,

            expected_output="清晰的对话规划，包括是否需要追问用户，如果需要追问，追问什么信息，或者直接回答问题。" \
            "如果不需要追问就直接提供房产咨询",
            agent=self.agents["planner"],
            context=[ self.intent_task]
        )
        
        # 任务3：提供房产咨询
        provide_consultation = Task(
            description="根据用户意图和对话规划，为用户提供专业的房产咨询服务。如果需要，调用适当的工具获取数据。",
            expected_output="详细、有用的房产咨询回答，包括必要的数据和建议",
            agent=self.agents["consultant"],
            context=[  self.intent_task, plan_conversation],
            dependencies=[plan_conversation]  
        )
        
        # 任务4：处理房贷相关查询（条件任务，根据意图动态激活）
        handle_mortgage = Task(
            description="如果用户意图涉及房贷计算或贷款建议，提供详细的等额本金和等额本息计算结果和专业建议。",
            expected_output="输出一套户型介绍，对应的清晰的房贷计算结果和实用的贷款建议",
            agent=self.agents["mortgage_expert"],
            context=[  self.intent_task, plan_conversation],
            output_file=self.output_path
        )
    
        return {
            "plan_conversation": plan_conversation,
            "provide_consultation":provide_consultation,
            "handle_mortgage":handle_mortgage,
        
        }
   
    
    def _create_crew(self):
        """创建智能体团队"""
        return Crew(
            agents=[self.agents["intent_recognizer"],
                    self.agents["consultant"],
                    self.agents["mortgage_expert"]
                    ],
            tasks= [self.intent_task] + list(self.tasks.values()),
            process=Process.hierarchical,  # 层级流程，由规划者协调
            manager_agent=self.agents["planner"],  # 由对话规划专家作为管理器
            verbose=True
        )
    
    def run(self):
        """运行智能体团队"""
        return self.crew.kickoff()
    
    def run_task(self, task: Task, context=None):
        if context:
            task.context = context
        crew = Crew(agents=[task.agent], tasks=[task])
        return crew.kickoff()
    

    def run_dialog_flow(self,user_input):
        all_user_inputs = [item[0] for item in self.history]
        user_inputs_combined = "\n".join(all_user_inputs)  # 用换行符分隔
        self.user_query = user_inputs_combined+user_input  # 更新当前查询
        # Step 1: 识别意图
        self.intent_task =self._update_intent_task()
        intent_result = self.run_task( self.intent_task)
        
        # Step 2: 规划对话
        plan_result = self.run_task(self.tasks["plan_conversation"], context=[self.intent_task])
        print(type(plan_result))
        # 判断是否需要追问
        if "需要追问" in plan_result.raw:
            return plan_result  # 暂停流程，返回追问内容给用户
        
        # Step 3: 提供咨询（如果意图明确）
        consultation_result = self.run_task(self.tasks["provide_consultation"], context=[self.intent_task, self.tasks["plan_conversation"]])
        
        # Step 4: 房贷处理（如果意图涉及房贷）
  
    
        mortgage_result = self.run_task(self.tasks["handle_mortgage"], context=[self.intent_task, self.tasks["plan_conversation"]])
        return f"{consultation_result}\n\n{mortgage_result}"
        
        # return consultation_result
    
    def handle_user_input(self, user_input: str):
        result = self.run_dialog_flow(user_input)
        self.history.append((user_input, result))
        return result


# In[ ]:


@skip_execution(IS_SKIP)
def test_crew():
     # 用户查询示例
    user_queries = [
        "我想在天府新区买一套3居室的住宅，预算在100万到200万之间，首付预算50万，能帮我推荐一下吗？",
    ]
    query_num=0
    print("===== 处理用户查询 =====")
    print(f"用户查询: {user_queries[query_num]}\n")
    
    crew = RealEstateCrew(user_queries[query_num])
    result = crew.run()
    
    print("\n===== 最终回答 =====")
    print(result)

# test_crew()


# In[ ]:


# @skip_execution(IS_SKIP)
def start_real_estate_chat():
    print("欢迎来到房产智能咨询助手！请输入您的问题（输入 '退出' 结束对话）")
    user_query=None
    crew = RealEstateCrew(user_query)  # 初始化时可以为空，后续每轮更新
    user_input=user_query
    while True:
        if user_query ==None:
            user_input = input("您：")
        if user_input.strip().lower() in ["退出", "exit", "quit"]:
            print("感谢使用房产助手，再见！")
            break
        
        response = crew.handle_user_input(user_input)
        print(f"助手：{response}\n")

start_real_estate_chat()


# In[ ]:




