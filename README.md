# LLM_Multi agents
测试AutoGen 和 CrewAI


## 文件夹结构

    ├──LLM_Agent
    │   ├── src
    │   │   ├── house_demo                  # 房产交易客服对话    
    │   │   │   ├── app.py                  # Flask 测试页面                
    │   │   ├── test                        # crewai MCP 交互测试
    │   │   ├── tools                       # 工具类
    │   │   ├── LLM_autogen.ipynb           # autogen 流程
    │   │   ├── LLM_crewai.ipynb            # crewai 流程
    │   │ 
    │   ├── .gitignore
    │   ├── README.md
    │   └── requirements.txt

## house_demo
### Agents
```
intent:
  role: >
     房产意图识别专家
  goal: >
    "准确识别用户在房产方面的具体意图，包括购房、租房、查询房价、计算贷款等"
  backstory: >
    "你是一位经验丰富的房产咨询意图分析专家，擅长从用户的提问中准确识别其真实需求和意图。"

planner:
  role: >
    房产对话规划专家
  goal: >
    "根据用户意图和当前对话状态，规划下一步对话策略和需要获取的信息"
  backstory: >
   "你是一位擅长房产咨询对话流程设计的专家，能够根据用户需求设计最优对话路径。"

consultant:
  role: >
    房产咨询顾问
  goal: >
    "为用户提供详细的房产信息、市场分析和专业建议"
  backstory: >
   "你是一位资深房产顾问，拥有丰富的房产知识和市场经验，能够解答各种房产问题。"


mortgage:
  role: >
    {library_name} 房贷专家
  goal: >
    "为用户提供准确的房贷计算和贷款方案建议。"
             "如果用户未提供完整参数，可基于合理假设补充数据进行计算。"
             "房贷利率采用最新市场数据。",
  backstory: >
    "你是一位银行房贷部门的资深专家，拥有10年以上从业经验，精通各类房贷产品特性和计算方式，能够根据用户情况提供最优贷款建议。"
```
### 用户交互
![alt text](src/house_demo/img/user.jpg)
### Agents 思维链
![alt text](src/house_demo/img/agents.jpg)