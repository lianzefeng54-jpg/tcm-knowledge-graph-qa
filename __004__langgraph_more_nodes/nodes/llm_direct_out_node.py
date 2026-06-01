from __004__langgraph_more_nodes.agent_state import AgentState
from langchain_core.messages import HumanMessage

from __005__fastapi.__003__msg_queue import put_msg_sentence_content, put_reply_content
from common.llm import my_llm
from langchain_core.runnables import RunnableConfig


async def llm_direct_out_node(state: AgentState, config:RunnableConfig):
    print("开始生成直接用户回答")
    user_id = config.get("configurable", {}).get("thread_id")
    await put_msg_sentence_content(user_id, "开始生成直接用户回答...")
    # 获取用户输入
    user_input = state["input"]

    # 构建提示词（专注中医回答）
    prompt = f"""
    用户输入: {user_input}

    你是一名专业的中医知识助手，回答时请尽量基于中医理论和术语来解释。  
    要求：
    - 优先从中医角度（如症状、方剂、中药材、功效、经络、辨证论治、典籍等）进行回答。  
    - 如果问题与中医无关，请直接给出简洁的常规回答，不要强行套用中医。  
    - 回答要准确、简洁，避免无关内容。  
    - 输出时只给出最终答案，不要解释你是如何推理的。
    """

    # 调用大模型
    result = ""
    for chunk in my_llm.stream([HumanMessage(content=prompt)]):
        result += chunk.content
        await put_reply_content(user_id, chunk.content)
        print(chunk.content, end="", flush=True)
    model_answer = result

    # 存入 state
    state["direct_out"] = model_answer
    state["output"] = model_answer
    print("完成生成直接用户回答")
    await put_msg_sentence_content(user_id, "完成生成直接用户回答...")
    return state
