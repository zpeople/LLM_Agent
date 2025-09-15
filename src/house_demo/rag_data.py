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
project_dir = os.path.abspath(os.path.join(current_dir, ""))
if project_dir not in sys.path:
    sys.path.append(project_dir)

import json
import re
from typing import List, Dict, Any,Tuple
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    RecursiveJsonSplitter,
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma



EMB_NAME = "/home/zzz/RAG_demo/model/BAAI/bge-small-zh"  
VECTOR_PATH = os.path.join(project_dir, "datasets/chroma_db")
IS_SKIP=True


# In[22]:


def parse_conversation_data(raw_data: Dict[str, Any],index) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    解析原始对话数据，转换为结构化格式
    
    参数:
        raw_data: 原始对话JSON数据
        
    返回:
        结构化后的对话数据和元数据
    """
    # 提取对话内容
    conversations = raw_data.get("conversations", [])
    
    # 分离用户查询和助手回答
    user_query = ""
    assistant_answer = ""
    assistant_thought = ""
    for conv in conversations:
        if conv.get("from") == "human":
            user_query = conv.get("value", "").strip()
        elif conv.get("from") == "assistant":
            assistant_answer = conv.get("value", "").strip()
  
    # 清理用户查询
    user_query = re.sub(r"[\n\r]+", " ", user_query)
    user_query = re.sub(r" +", " ", user_query)
    user_query = re.sub(r"，+", "，", user_query)
    user_query = re.sub(r"？+", "？", user_query)
    
    thought_match = re.search(r"<think>(.*?)</think>", assistant_answer, re.DOTALL)
    if thought_match:
        assistant_thought = thought_match.group(1).strip()
        # print(assistant_thought)
    
        
    # 清理回答内容（去除可能的思考标记）
    assistant_answer = re.sub(r"<think>(.*?)</think>", "", assistant_answer, flags=re.DOTALL)
    assistant_answer = re.sub(r"[\n\r]+", " ", assistant_answer)
    assistant_answer = re.sub(r" +", " ", assistant_answer)
    # 构建结构化数据
    structured_data = {
        "user_query": user_query,
        "think":assistant_thought,
        "answer": assistant_answer,
        
       
    },
    
    # 构建元数据
    meta_data = {
        "id": raw_data.get("id", F"{index}"),
        "conversation_count": len(conversations)
    }
    
    return structured_data, meta_data

def batch_process(
    raw_data_list: List[Dict[str, Any]]
) -> (List[Dict[str, Any]], List[Dict[str, Any]]):
    """批量处理数据列表，分别返回结构化数据和元数据"""
    structured_list = []
    meta_list = []

    for i, data in enumerate(raw_data_list):
        structured, meta = parse_conversation_data(data,index=i)
        structured_list.append(structured)
        meta_list.append(meta)

    return structured_list, meta_list


# In[23]:


from langchain.schema import Document


def load_json(file):
    """
    加载JSON
    """
    name, extension = os.path.splitext(file)
    if extension == ".json":
        # 处理JSON文件
        try:
            with open(file, "r", encoding="utf-8") as f:
                json_data = json.load(f)

                # 按每条instruction 拆分
                json_data, meta_data = batch_process(json_data)
                datas = [
                    Document(page_content=str(chunk), metadata=meta)
                    for chunk, meta in zip(json_data, meta_data)
                ]
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return None
    else:
        print("Document format is not supported!")
        return None

    print(f"pages: {len(datas)}")

    return datas


# In[24]:


def chunk_data(data, chunk_size=256, chunk_overlap=100):
    """
    将数据分割成块
    :param data:
    :param chunk_size: chunk块大小
    :param chunk_overlap: 重叠部分大小
    :return:
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    print(f"pages: {len(data)}")
    chunks = text_splitter.split_documents(data)
    return chunks


# In[25]:


def get_embedding(embedding_name):
    """
    根据embedding名称加载对应的嵌入模型
    """
    # 通用模型参数配置
    model_kwargs = {"device": "cuda"}
    encode_kwargs = {"normalize_embeddings": True}  # 归一化嵌入向量

    embedding_path = os.path.join(project_dir, "model", embedding_name)
    print(embedding_path)

    return HuggingFaceEmbeddings(
        model_name=embedding_path,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )


# In[26]:


# create embeddings using OpenAIEmbeddings() and save them in a Chroma vector store
def create_embeddings_chroma(
    embedding_name, chunks, persist_dir=os.path.join(project_dir, "db/chroma_db")
):
    """
    创建并保存 Chroma 向量库
    """
    # 获取嵌入模型
    embeddings = get_embedding(embedding_name)
    if not os.path.isdir(persist_dir):
        os.mkdir(persist_dir)

    # 创建向量库时指定保存路径
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,  # 指定本地保存目录
    )

    # 打印保存信息
    print(f"Chroma 向量库已保存到: {os.path.abspath(persist_dir)}")
    return vector_store


def load_embeddings_chroma(embedding_name, persist_dir):
    """
    加载已保存的 Chroma 向量库
    """
    # 获取与创建时相同的嵌入模型（必须一致，否则向量不兼容）
    embeddings = get_embedding(embedding_name)

    # 加载本地向量库
    vector_store = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    print(f"Chroma 向量库已从 {os.path.abspath(persist_dir)} 加载")
    return vector_store


# In[ ]:


def get_serarch(vector_path=VECTOR_PATH,embedding_name=EMB_NAME,query="",top_k=3):
    vecotr_db = load_embeddings_chroma(embedding_name, vector_path)
    results = vecotr_db.similarity_search_with_score(
        query,
        k=top_k,
    )
    serarched_datas=[]
    # print(results)
    for res, score in results:
        if not IS_SKIP:
            print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")
        serarched_datas.append(res.page_content)
    return serarched_datas


# In[28]:


def save_local_chroma():
    datas = load_json(os.path.join(project_dir,"datasets/sales_data.json"))
    print(datas[0])
    chunks =chunk_data(datas,chunk_size=512,chunk_overlap=100)
    create_embeddings_chroma(EMB_NAME, chunks, VECTOR_PATH)


# save_local_chroma()


# In[38]:


def test_load():
    data = get_serarch(vector_path=VECTOR_PATH,embedding_name=EMB_NAME,query="贷款",top_k=3)
    print(data)


test_load()


# In[ ]:




