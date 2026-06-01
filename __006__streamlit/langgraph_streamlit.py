# app.py
import json

import streamlit as st
import requests


def get_user_id():
    return "user_001"


def process(input: str):
    # 后端 FastAPI 服务地址
    url = "http://127.0.0.1:8000/process"

    # 要发送的 JSON 数据
    payload = {
        "input": input,
        "user_id": get_user_id()
    }

    # 发送 POST 请求
    response = requests.post(url, json=payload, stream=True)
    if response.status_code != 200:
        return "请求错误"
    for chunck in response.iter_content(chunk_size=None):
        yield json.loads(chunck.decode("utf-8"))


def run_process(input: str, think_placeholder, reply_placeholder):
    think_placeholder_content = ""
    reply_placeholder_content = ""
    is_start = False
    for chunk_dict in process(input):
        if chunk_dict.get("type") == "msg":
            content = chunk_dict.get("msg")
            think_placeholder_content += content
            print(think_placeholder_content)
            think_placeholder.text(think_placeholder_content)
            # 删除最后这条消息
            if is_start:
                st.session_state.messages = st.session_state.messages[:-1]
            # 添加新的消息
            st.session_state.messages.append(
                {"role": "assistant",
                 "content": reply_placeholder_content,
                 "think_content": think_placeholder_content})
        elif chunk_dict.get("type") == "reply":
            content = chunk_dict.get("msg")
            reply_placeholder_content += content
            reply_placeholder.markdown(reply_placeholder_content, unsafe_allow_html=True)
            # 删除最后一条消息
            if is_start:
                st.session_state.messages = st.session_state.messages[:-1]
            # 添加新的消息
            st.session_state.messages.append(
                {"role": "assistant",
                 "content": reply_placeholder_content,
                 "think_content": think_placeholder_content})
        elif chunk_dict.get("type") == "done":
            ...
        is_start = True


# 页面设置
st.set_page_config(page_title="中医对话机器人", page_icon="💬", layout="centered")
st.title("💬 中医对话机器人")
st.write("和智能机器人进行对话")

# 初始化聊天记录，session_state, 字典，存储聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示已有的聊天记录
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
    else:
        with st.chat_message(message["role"]):
            with st.expander("思考完毕", expanded=False):
                st.text(message["think_content"])
            st.markdown(message["content"], unsafe_allow_html=True)

# 输入框（Streamlit 的聊天输入组件）
if prompt := st.chat_input("请输入您的问题..."):
    # 如果用户进行输入，才进入这个代码
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": prompt})

    # 显示模型的回复
    with st.chat_message("assistant"):
        with st.expander("正在思考...", expanded=True):
            think_placeholder = st.empty()
        reply_placeholder = st.empty()

    # 调用后端 FastAPI 接口
    run_process(prompt, think_placeholder, reply_placeholder)
