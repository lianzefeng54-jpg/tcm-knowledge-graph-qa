from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser

from __004__langgraph_more_nodes.agent_state import AgentState
from __005__fastapi.__003__msg_queue import put_msg_sentence_content
from common.llm import my_llm
from langchain_core.runnables import RunnableConfig


class XiaohongshuTCMPostOutput(BaseModel):
    title: str
    content: str


def generate_xiaohongshu_text(input: str):
    parser = PydanticOutputParser(pydantic_object=XiaohongshuTCMPostOutput)
    format_instructions = parser.get_format_instructions()

    messages = [
        SystemMessage(content=(
            "你是一个专门为小红书平台撰写中医养生内容的文案助手。\n"
            "请根据用户提供的主题或需求，生成一条适合小红书发布的中医养生类内容，要求包含：\n"
            "1. 吸引人的标题（title）：不超过19个中文字符，简短有吸引力\n"
            "2. 内容正文，具有分享性和实用性，语气自然亲切，适合社交媒体（content）\n"
            "请你严格按照以下格式返回结果：\n"
            f"{format_instructions}"
        )),
        HumanMessage(content=input)
    ]

    raw_output = my_llm.invoke(messages).content.strip()
    parsed_output = parser.parse(raw_output)
    return parsed_output.title, parsed_output.content


async def text_generate_node(state: AgentState, config:RunnableConfig):
    """根据用户输入生成中医养生类的小红书文案（包括标题、内容、策略）"""
    print("开始生成小红书标题和内容")
    user_id = config.get("configurable", {}).get("thread_id")
    await put_msg_sentence_content(user_id, "开始生成小红书标题和内容...")
    title, content = generate_xiaohongshu_text(state['input'])

    state['xiaohongshu_tcm_post_title'] = title
    state['xiaohongshu_tcm_post_content'] = content
    print("完成生成小红书标题和内容")
    await put_msg_sentence_content(user_id, "完成生成小红书标题和内容...")
    return state


if __name__ == '__main__':
    title, content = generate_xiaohongshu_text("写一篇文章，关于吃西瓜。")
    print(title)
    print(content)
