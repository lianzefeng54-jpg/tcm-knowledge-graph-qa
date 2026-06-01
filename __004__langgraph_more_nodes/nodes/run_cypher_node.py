from __004__langgraph_more_nodes.agent_state import AgentState
from __005__fastapi.__003__msg_queue import put_msg_sentence_content
from common.neo4j_manager import neo4j_client
from langchain_core.runnables import RunnableConfig


async def run_cypher_node(state: AgentState, config:RunnableConfig):
    print("开始运行大模型cypher语句")
    user_id = config.get("configurable", {}).get("thread_id")
    await put_msg_sentence_content(user_id, "开始运行大模型cypher语句查询...")
    cypher_query_list = state.get("cypher_query", [])
    query_results = []

    for cypher_query in cypher_query_list:
        result_list = neo4j_client.run_cypher(cypher_query)
        query_results.append({
            "query": cypher_query,
            "result": result_list
        })

    # 存入 state
    state["cypher_results"] = query_results
    print("完成运行大模型cypher语句")
    await put_msg_sentence_content(user_id, "完成运行大模型cypher语句...")
    return state
