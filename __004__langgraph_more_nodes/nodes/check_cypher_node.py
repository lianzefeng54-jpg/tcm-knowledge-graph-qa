from langchain_core.runnables import RunnableConfig

from __004__langgraph_more_nodes.agent_state import AgentState
from __005__fastapi.__003__msg_queue import put_msg_sentence_content
from common.neo4j_manager import neo4j_client


async def check_cypher_node(state:AgentState, config:RunnableConfig):
    print("开始检查cypher语句")
    user_id = config.get("configurable", {}).get("thread_id")
    await put_msg_sentence_content(user_id, "开始检查cypher语句...")
    cypher_query_list = state["cypher_query"]
    state['is_all_validate_cypher'] = True
    for cypher_query in cypher_query_list:
        if not neo4j_client.validate_cypher(cypher_query):
            state['is_all_validate_cypher'] = False
    print(f"完成检查cypher语句:{state['is_all_validate_cypher']}")
    await put_msg_sentence_content(user_id, "完成检查cypher语句...")
    return state


if __name__ == '__main__':
    print(check_cypher_node({"cypher_query":["MATCH (e:Employee) RETURN e.id, e.name, e.salary, e.deptno"]}))