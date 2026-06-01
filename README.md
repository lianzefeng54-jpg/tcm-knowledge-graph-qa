# 中医知识图谱问答系统 (TCM Knowledge Graph QA)

基于 Neo4j + LangGraph 的中医知识图谱智能问答系统，支持方剂、药材、症状、疾病等多维度知识查询，并支持生成小红书科普内容。

## 项目架构

```
ChineseMedicalNewProjectEdit/
├── __001__clawler/          # 爬虫：爬取中医方剂/药材数据
├── __002__extract_information/ # LLM 结构化抽取知识图谱
├── __003__create_neo4j_database/ # Neo4j 图数据库导入 + FAISS 向量化
├── __004__langgraph_more_nodes/  # LangGraph 多节点 Agent 工作流
├── __005__fastapi/          # FastAPI SSE 流式后端
├── __006__streamlit/        # Streamlit 前端对话界面
├── __007__fine_tune/        # 微调数据准备
├── common/                  # 公共模块 (LLM/Neo4j/Config/Embedding)
├── picture/                 # 图片资源
├── requirements.txt         # Python 依赖
└── .env.example             # 环境变量模板
```

## 流程图

```
用户输入 → 语义转写 → 意图识别
                        ├── 小红书意图 → 生成图文 → 发布
                        └── 中医意图 → 实体抽取 → Neo4j匹配
                                       → Cypher生成 → 验证 → 执行
                                       → 答案生成 → 输出
```

## 快速开始

### 1. 环境准备

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key、Neo4j 连接信息等
```

### 3. 启动 Neo4j

确保 Neo4j 数据库已启动并可通过配置的 URI 访问。

### 4. 运行爬虫 & 导入数据

```bash
# 爬取方剂数据
python __001__clawler/__001__get_formula_menu_list.py
python __001__clawler/__002__get_formula_detail_info.py

# 爬取药材数据
python __001__clawler/__003__get_herb_menu_list.py
python __001__clawler/__004__get_herb_detail_list.py

# LLM 抽取知识图谱
python __002__extract_information/__001__extract_herb_data.py
python __002__extract_information/__002__extract_formula_data.py

# 导入 Neo4j
python __003__create_neo4j_database/__001__graph_importer.py

# 构建 FAISS 向量索引
python __003__create_neo4j_database/__003__faiss_embedding.py
```

### 5. 启动服务

```bash
# 启动 FastAPI 后端
python __005__fastapi/__001__langgraph_fastapi.py

# 启动 Streamlit 前端（新终端）
streamlit run __006__streamlit/langgraph_streamlit.py
```

## 技术栈

- **知识图谱**: Neo4j
- **AI Agent 框架**: LangGraph
- **LLM**: OpenAI API 兼容接口 (可接入任意模型)
- **向量检索**: FAISS + sentence-transformers
- **后端**: FastAPI (SSE 流式)
- **前端**: Streamlit
- **爬虫**: Playwright

## 功能特性

- 🔍 中医知识智能问答 (方剂、药材、症状、疾病、功效)
- 🧠 多节点 Agent 工作流，自动生成并验证 Cypher 查询
- 📚 支持知识溯源 (《伤寒论》《本草纲目》等典籍)
- 📝 自动生成小红书中医科普内容 + 配图
- 🔄 SSE 流式输出，实时展示推理过程
- 💾 支持微调数据导出

## License

仅供学习交流使用
