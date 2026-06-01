from langchain_core.runnables import RunnableConfig
import os
from __004__langgraph_more_nodes.agent_state import AgentState
from __005__fastapi.__003__msg_queue import put_msg_sentence_content


async def check_text_image_node(state: AgentState, config: RunnableConfig):
    """检查是否可以发布小红书"""
    user_id = config.get("configurable", {}).get("thread_id")
    await put_msg_sentence_content(user_id, "开始检查是否可以发小红书...")
    title = state.get("xiaohongshu_tcm_post_title", "")
    content = state.get("xiaohongshu_tcm_post_content", "")
    image_path_list = state.get("xiaohongshu_image_path_list", [])
    state["is_can_publish_xiaohongshu"] = True
    if not title:
        state["is_can_publish_xiaohongshu"] = False
        state["output"] = "发布小红书失败，标题缺失！"
    if not content:
        state["is_can_publish_xiaohongshu"] = False
        state["output"] = "发布小红书失败，内容缺失！"
    if not image_path_list:
        state["is_can_publish_xiaohongshu"] = False
        state["output"] = "发布小红书失败，图片缺失！"
    # 检查图片是否存在
    for image_path in image_path_list:
        if not os.path.exists(image_path):
            state["is_can_publish_xiaohongshu"] = False
    await put_msg_sentence_content(user_id, f"完成检查是否可以发小红书:{state['is_can_publish_xiaohongshu']}")
    return state
