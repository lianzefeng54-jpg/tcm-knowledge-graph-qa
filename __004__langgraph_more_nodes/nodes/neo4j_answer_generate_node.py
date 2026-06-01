from __004__langgraph_more_nodes.agent_state import AgentState
from langchain_core.messages import HumanMessage

from __005__fastapi.__003__msg_queue import put_msg_sentence_content, put_reply_content
from common.llm import my_llm
import json
from langchain_core.runnables import RunnableConfig


async def neo4j_answer_generate_node(state: AgentState, config:RunnableConfig) -> AgentState:
    print("开始进行neo4j输入大模型的回答")
    user_id = config.get("configurable", {}).get("thread_id")
    await put_msg_sentence_content(user_id, "开始进行neo4j输入大模型的回答...")
    user_input = state["input"]
    cypher_results = state.get("cypher_results", [])

    # 把 cypher_results 转成字符串，方便喂给大模型
    cypher_results_str = json.dumps(cypher_results, ensure_ascii=False, indent=2)

    prompt = f"""
    你是一个中医知识图谱问答助手。
    用户提出了问题：{user_input}

    我已经在 Neo4j 图数据库中执行了查询，查询结果如下：
    {cypher_results_str}

    请你根据这些查询结果，用简洁、清晰、自然的中文回答用户的问题。
    如果查询结果无法回答用户的问题，请如实告知用户没有找到相关答案。
    """
    result = ""
    for chunck in my_llm.stream([HumanMessage(content=prompt)]):
        print(chunck.content, end="", flush=True)
        result += chunck.content
        await put_reply_content(user_id, chunck.content)

    # 保存结果
    state["neo4j_answer"] = result
    state["output"] = result
    print("完成进行neo4j输入大模型的回答")
    await put_msg_sentence_content(user_id, "完成进行neo4j输入大模型的回答...")

    return state
