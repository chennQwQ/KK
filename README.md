# 天涯 kk 神贴 RAG 知识库

基于 LangChain + ChromaDB，对天涯神贴楼主 kk 的帖子进行学习和分析，生成 RAG（检索增强生成）知识库问答系统。

当前实现是 Streamlit 原型，入口为 `app.py`。下面的产品化扩展路线是后续规划，用于把原型升级为可登录使用的 Web 产品。

## 产品化扩展路线

规划定位：以下内容是未来产品化架构路线，不代表当前 Streamlit 原型已经实现。
产品目标：给别人登录使用的 Web 产品。
主应用：Next.js + TypeScript。
RAG 服务：FastAPI + Python。
当前阶段：先在 Python 项目里建立 manifest、answer pipeline、persistence schema。

## Memory 持久化设计

规划定位：以下持久化方案用于后续产品化重构。
权威数据：PostgreSQL。
临时状态：Redis。
聊天消息、长期 memory、引用和任务状态要先有稳定的持久化边界，再接入前端产品壳。

## 向量数据库优化与部署

规划定位：以下是未来部署和检索 adapter 方向。
语义检索：Qdrant 或 Chroma。
第一阶段继续保留 Chroma 的轻量优势，同时为后续切换到 Qdrant 预留 adapter 边界。

## 对话分类存储

规划定位：以下分类存储设计用于后续多用户产品形态。
PostgreSQL 存储会话分类、消息分类、任务分类和引用归属，保证产品侧可以按用户、知识库、主题和任务状态查询。

## 多虚拟对话对象设计

规划定位：以下虚拟对象设计用于后续角色化、多对象对话能力。
PostgreSQL 存储虚拟对象配置，RAG 服务根据虚拟对象加载不同 prompt、memory、知识库和回答策略。
关系图谱：Neo4j。

## 第一阶段重构计划

规划定位：第一阶段先在现有 Python 项目内建立产品化基础，不直接等同于当前 Streamlit 原型。
当前阶段：先在 Python 项目里建立 manifest、answer pipeline、persistence schema。
先把入库记录、回答流水线和持久化 schema 做清楚，再把 Next.js 产品壳接到稳定接口上。

## 项目简介

本项目爬取并整理了天涯神贴楼主 kk 的经典帖子，使用 embedding 模型向量化存储，通过大模型实现智能问答。

**核心功能：**
- 构建向量知识库
- 支持语义检索和 AI 问答
- 调用流式 API 生成回答，当前 Streamlit UI 一次性展示完整回答

## 快速开始

### 1. 安装依赖

```bash
#安装 LangChain 核心组件和本地模型依赖
pip install langchain chromadb pypdf sentence-transformers ollama
#安装云端 API 依赖
pip install openai chromadb tiktoken pypdf langchain
#推荐方式，从 requirements.txt 统一安装所有依赖
pip install -r requirements.txt
```

### 2. 配置大模型

**方案一：本地 Ollama（免费）**
```bash
# 安装 Ollama: https://ollama.ai
ollama pull qwen3.5:latest
```

**方案二：云端 API（推荐 DeepSeek）**
- 获取 API Key：https://platform.deepseek.com
- 设置环境变量 `DEEPSEEK_API_KEY`，配置读取位置为 `src/config.py`：
```powershell
$env:DEEPSEEK_API_KEY = "你的 API_KEY"
```

### 3. 运行

```bash
streamlit run app.py
```

首次运行会自动构建知识库，之后直接加载。

## 使用方法

输入问题，系统会基于 kk 的帖子内容回答：

```
❓ 输入问题（exit 退出）：kk 对...怎么看

🤖 回答：

根据 kk 在 2010 年的帖子，他认为...
```

## 项目结构

```
KK/
├── app.py              # Streamlit 应用入口
├── main.py             # 旧版命令行/实验入口，不作为当前推荐运行入口
├── src/                # 配置和 RAG 核心模块
│   └── config.py       # 环境变量和模型配置
├── requirements.txt     # 依赖
├── data/               # kk 的帖子文件
│   ├── book1.pdf
│   ├── book2.pdf
│   └── qa.pdf
├── chroma_db/          # 向量数据库（自动生成）
└── README.md
```

## 技术栈

- **LangChain** - 大模型应用框架
- **ChromaDB** - 向量数据库
- **BGE-Large-Zh** - 中文 Embedding 模型
- **Ollama / DeepSeek** - 大语言模型

## 配置说明

**src/config.py 关键配置：**
```python
DATA_PATH = "./data"           # 帖子文件目录
DB_PATH = "./chroma_db"        # 向量库存储
EMBED_MODEL = "BAAI/bge-large-zh"  # Embedding 模型
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
```

PowerShell 临时设置示例：
```powershell
$env:DEEPSEEK_API_KEY = "你的 API_KEY"
streamlit run app.py
```

## 关于天涯 kk 神贴

楼主 kk 是天涯社区传奇人物，其帖子被誉为中国房地产启蒙神贴，影响了无数人的房产观和财富观。

本项目旨在通过 RAG 技术，让 kk 的思想以 AI 问答的形式继续传承。

---
