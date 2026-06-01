# 🏥 中医知识图谱问答系统 (TCM Knowledge Graph QA)

基于 Neo4j 图数据库 + LangGraph 多节点 Agent 的中医知识智能问答与内容生成系统。

## 项目架构

```
tcm-knowledge-graph-qa/
├── common/                          # 公共模块
│   ├── config.py                    # 配置中心（读取所有环境变量）
│   ├── llm.py                       # LLM 客户端（OpenAI 兼容接口）
│   ├── neo4j_manager.py             # Neo4j 数据库操作封装
│   ├── embedding_model.py           # sentence-transformers 向量模型
│   ├── path_utils.py                # 路径工具
│   └── output_graph_utils.py        # LangGraph 状态图可视化输出
├── __001__clawler/                  # 🕷️ 爬虫模块
│   ├── __000__获取网页内容通用方法.py
│   ├── __001__get_formula_menu_list.py   # 爬取方剂列表
│   ├── __002__get_formula_detail_info.py # 爬取方剂详情
│   ├── __003__get_herb_menu_list.py      # 爬取药材列表
│   ├── __004__get_herb_detail_list.py    # 爬取药材详情
│   ├── 方剂/                        # 爬取的方剂 TXT 数据
│   └── 中药/                        # 爬取的药材 TXT 数据
├── __002__extract_information/      # 🧠 LLM 知识抽取
│   ├── __000__extract_graph_data_utils.py # 抽取工具（Pydantic 结构化解析）
│   ├── __001__extract_herb_data.py        # 批量抽取药材知识
│   └── __002__extract_formula_data.py     # 批量抽取方剂知识
├── __003__create_neo4j_database/    # 🗄️ 图数据库构建
│   ├── __001__graph_importer.py     # 将抽取结果导入 Neo4j
│   ├── __002__export_metadata.py    # 导出图谱元数据（Schema）
│   └── __003__faiss_embedding.py    # 构建 FAISS 向量索引（实体检索）
├── __004__langgraph_more_nodes/     # 🤖 LangGraph 多节点 Agent
│   ├── agent_state.py               # 状态定义（TypedDict）
│   ├── langgraph_more_nodes.py      # 状态图编排（路由逻辑）
│   └── nodes/                       # 各功能节点
│       ├── semantic_transcription_node.py    # 语义转写
│       ├── xiaohongshu_publish_intent_node.py # 小红书意图识别
│       ├── text_generate_node.py             # 小红书文案生成
│       ├── image_generate_node.py            # 即梦 AI 图片生成
│       ├── check_text_image_node.py          # 图文审核
│       ├── auto_publish_xiaohongshu_node.py  # Playwright 自动发布
│       ├── zhongyi_intent_node.py            # 中医意图分类
│       ├── llm_direct_out_node.py            # 非中医问题直接回答
│       ├── extract_entity_from_user_input_node.py # 实体抽取
│       ├── match_entity_from_neo4j_node.py   # Neo4j 模糊匹配实体
│       ├── generate_neo4j_cypher_node.py     # LLM 生成 Cypher 查询
│       ├── check_cypher_node.py              # Cypher 语法验证
│       ├── run_cypher_node.py                # 执行 Cypher
│       ├── neo4j_answer_generate_node.py     # 基于图查询结果生成回答
│       └── generate_markdown_node.py         # Markdown 格式化输出
├── __005__fastapi/                  # 🌐 FastAPI SSE 流式后端
│   ├── __001__langgraph_fastapi.py  # API 服务入口
│   ├── __002__langgraph_fastapi_client.py # 客户端调用示例
│   └── __003__msg_queue.py         # asyncio 消息队列（SSE 推送）
├── __006__streamlit/                # 💬 Streamlit 对话前端
│   ├── langgraph_streamlit.py       # 前端 UI
│   └── langgraph_streamlit_run.py   # 启动脚本
├── __007__fine_tune/                # 🔧 微调数据准备
│   ├── __001__json_join.py          # 数据合并
│   └── __002__fetch_url.py          # URL 抓取
├── picture/                         # 生成的示例图片
├── requirements.txt
├── .env.example
└── README.md
```

## 流程图

```
用户输入
  │
  ▼
语义转写 ─── 意图识别 ──┬── 小红书意图 ──→ 文案生成 ──→ 图片生成(即梦AI) ──→ 图文审核
                        │                                                    │
                        │                                    ┌──通过──→ 自动发布(Playwright)
                        │                                    │
                        │                                    └──不通过──→ Markdown预览
                        │
                        └── 中医意图 ──→ 实体抽取 ──→ Neo4j模糊匹配
                                              │
                                              ▼
                                        Cypher生成 ──→ 语法验证
                                              │             │
                                              │        ┌──失败──→ 重新生成
                                              │        │
                                              ▼        ▼
                                         执行Cypher ──→ 答案生成 ──→ 输出
                        │
                        └── 非中医意图 ──→ 直接LLM回答 ──→ 输出
```

## 依赖的外部 API / 服务

本项目依赖 **4 个外部服务**，全部通过环境变量配置：

### 1. LLM 大模型（必需）

用于知识抽取、意图识别、实体抽取、Cypher 生成、答案生成等所有 AI 推理环节。

- **接口类型**：OpenAI 兼容 API（支持任意符合 OpenAI 格式的服务）
- **需要注册的服务**（任选其一）：
  - [OpenAI](https://platform.openai.com/) — 原生 GPT 服务
  - [DeepSeek](https://platform.deepseek.com/) — 性价比高，中文能力强
  - [火山引擎豆包](https://www.volcengine.com/product/doubao) — 国内服务
  - [智谱 AI](https://open.bigmodel.cn/) — GLM 系列
  - [阿里百炼](https://bailian.console.aliyun.com/) — 通义千问
  - 任何兼容 OpenAI 接口格式的 API 网关

```
MODEL_API_KEY=sk-xxxxxxxxxxxxxxxx    # API Key
MODEL_BASE_URL=https://api.openai.com/v1   # API 地址
MODEL_NAME=gpt-4o                    # 模型名称
```

### 2. Neo4j 图数据库（必需）

存储中医知识图谱（方剂、药材、症状、疾病、功效、典籍等节点及关系）。

- **获取方式**：
  - [Neo4j AuraDB](https://neo4j.com/cloud/aura/) — 云端免费版（无需安装）
  - [Neo4j Desktop](https://neo4j.com/download/) — 本地安装
  - [Docker](https://hub.docker.com/_/neo4j) — 容器部署

```
NEO4J_URI=bolt://localhost:7687      # 数据库地址
NEO4J_USER=neo4j                     # 用户名
NEO4J_PASSWORD=your_password         # 密码
```

### 3. 即梦 AI 图片生成（可选，小红书功能需要）

火山引擎的 AI 图片生成服务，用于为小红书文案自动生成中医养生主题配图。

- **获取方式**：
  1. 注册 [火山引擎](https://www.volcengine.com/)
  2. 开通 [即梦 AI](https://www.volcengine.com/product/jimeng) 服务
  3. 在控制台获取 AK/SK

```
JIMENG_AK=your_access_key            # 火山引擎 Access Key
JIMENG_SK=your_secret_key            # 火山引擎 Secret Key
```

> 💡 如果不需要小红书图文生成功能，这两个配置可以不填，系统会在调用时抛出异常（不影响中医问答功能）。

### 4. Embedding 向量模型（必需）

用于 FAISS 向量检索，将用户输入的实体名与 Neo4j 中的实体进行语义匹配。

- **不需要外部 API 密钥**，使用本地模型
- 模型会自动从 Hugging Face 下载到本地

```
EMBEDDING_MODEL_PATH=BAAI/bge-small-zh-v1.5   # 中文 embedding 模型
```

> 其他可选模型：`BAAI/bge-large-zh-v1.5`（更准但更慢）、`shibing624/text2vec-base-chinese`

---

## 快速开始

### 前置要求

- Python 3.10+
- Neo4j 数据库（本地或云端）
- LLM API 密钥

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium    # 小红书发布需要
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入你的真实配置：

```env
# === LLM（必须） ===
MODEL_API_KEY=sk-your-api-key-here
MODEL_BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat

# === Neo4j（必须） ===
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# === 即梦图片生成（小红书功能需要） ===
JIMENG_AK=your_ak_here
JIMENG_SK=your_sk_here

# === Embedding 模型（必须） ===
EMBEDDING_MODEL_PATH=BAAI/bge-small-zh-v1.5
```

### 3. 准备数据（首次使用）

按顺序执行以下步骤构建知识图谱：

```bash
# Step 1: 爬取中医数据
python __001__clawler/__001__get_formula_menu_list.py
python __001__clawler/__002__get_formula_detail_info.py
python __001__clawler/__003__get_herb_menu_list.py
python __001__clawler/__004__get_herb_detail_list.py

# Step 2: LLM 抽取结构化知识
python __002__extract_information/__001__extract_herb_data.py
python __002__extract_information/__002__extract_formula_data.py

# Step 3: 导入 Neo4j
python __003__create_neo4j_database/__001__graph_importer.py

# Step 4: 构建 FAISS 向量索引
python __003__create_neo4j_database/__003__faiss_embedding.py
```

### 4. 启动服务

```bash
# 终端 1: 启动 FastAPI 后端
python __005__fastapi/__001__langgraph_fastapi.py

# 终端 2: 启动 Streamlit 前端
streamlit run __006__streamlit/langgraph_streamlit.py
```

浏览器打开 `http://localhost:8501` 即可使用。

---

## 知识图谱 Schema

### 节点类型

| 标签 | 说明 | 示例 |
|------|------|------|
| `Herb` | 中药材 | 人参、黄芪、当归 |
| `Formula` | 方剂 | 四君子汤、桂枝汤 |
| `Symptom` | 症状 | 咳嗽、发热、腹痛 |
| `Disease` | 疾病 | 风寒感冒、脾虚泄泻 |
| `Effect` | 功效 | 补气、活血、祛湿 |
| `Source` | 典籍出处 | 《伤寒论》《本草纲目》 |
| `HerbNature` | 药性 | 寒、热、温、凉、平 |
| `HerbFlavor` | 药味 | 甘、苦、辛、酸、咸 |
| `Meridian` | 归经 | 肺经、肝经、脾经 |
| `EffectCategory` | 功效分类 | 补益类、清热类 |
| `FormulaCategory` | 方剂分类 | 清热剂、补益剂 |

### 关系类型

| 关系 | 方向 | 示例 |
|------|------|------|
| `HAS_INGREDIENT` | Formula→Herb | 四君子汤 包含 人参 |
| `TREATS_DISEASE` | Formula/Herb→Disease | 桂枝汤 治疗 风寒感冒 |
| `ALLEVIATES_SYMPTOM` | Formula/Herb→Symptom | 甘草 缓解 咳嗽 |
| `HAS_EFFECT` | Formula/Herb→Effect | 黄芪 具有 补气 |
| `HAS_SYMPTOM` | Disease→Symptom | 感冒 症状 发热 |
| `FROM_SOURCE` | Formula→Source | 四君子汤 出自 《太平惠民和剂局方》 |

---

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 知识图谱 | Neo4j | 图数据库存储 |
| AI 框架 | LangGraph | 多节点 Agent 工作流编排 |
| LLM | OpenAI 兼容 API | 推理、抽取、生成 |
| 向量检索 | FAISS + sentence-transformers | 实体语义匹配 |
| 后端 | FastAPI + SSE | 流式 API |
| 前端 | Streamlit | 对话 UI |
| 爬虫 | Playwright + requests | 数据采集 |
| 图片生成 | 火山引擎即梦 AI | 小红书配图 |

---

## API 接口

### POST /process

SSE 流式接口，用于前端实时获取 Agent 推理过程。

**请求：**
```json
{
  "input": "我感冒咳嗽了，有什么方子推荐？",
  "user_id": "user_001"
}
```

**SSE 事件类型：**
```json
{"type": "msg", "msg": "开始识别是否是中医的意图识别...\n"}
{"type": "msg", "msg": "完成识别是否是中医的意图识别：True...\n"}
{"type": "reply", "msg": "根据您描述的症状..."}
{"type": "done", "msg": ""}
```

- `type: "msg"` — 推理过程提示（Streamlit 中显示为思考过程）
- `type: "reply"` — 最终回答内容（流式逐字返回）
- `type: "done"` — 流结束标记

---

## 微调数据

`__007__fine_tune/` 目录包含微调数据准备工具，可将抽取的知识图谱数据转换为 LLM 微调格式（instruction-input-output）。

```bash
python __007__fine_tune/__001__json_join.py
```

---

## License

仅供学习交流使用。中医数据来源于公开网站，请遵守数据源的使用条款。
