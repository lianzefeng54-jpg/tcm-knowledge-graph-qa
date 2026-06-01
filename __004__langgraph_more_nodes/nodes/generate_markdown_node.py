import os
from langchain_core.runnables import RunnableConfig
from __004__langgraph_more_nodes.agent_state import AgentState
from __005__fastapi.__003__msg_queue import put_msg_sentence_content, put_reply_content
from common.path_utils import root_dir


def generate_xiaohongshu_success_fail(is_can_publish_xiaohongshu):
    if is_can_publish_xiaohongshu:
        return "小红书发布成功"
    else:
        return "小红书发布失败"


def trans_image_path_list(image_path_list: list):
    def trans_image_path(image_path):
        relative_path = os.path.relpath(image_path, root_dir)
        return f"http://localhost:8000/{relative_path}"

    return [trans_image_path(image_path) for image_path in image_path_list]


def generate_markdown_code(title, content, image_path_list, xiaohongshu_success_fail, image_width="300px", image_height="300px"):
    image_path_list = trans_image_path_list(image_path_list)
    # 创建 HTML 页面结构
    html_code = f"""
    <html>
        <head>
            <title>{title}</title>
            <style>
                .image-container {{
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    justify-content: flex-start;
                }}
                .image-container img {{
                    width: {image_width};
                    height: {image_height};
                }}
            </style>
        </head>
        <body>
            <p>{xiaohongshu_success_fail}</p>
            <h3>标题：{title}</h3>
            <p>内容：{content}</p>
            <div class="image-container">
    """

    # 为每张图片生成 <img> 标签
    for image_path in image_path_list:
        html_code += f'<img src="{image_path}" alt="image"/>\n'

    # 关闭 <div> 和 <body> 标签
    html_code += """</div>
        </body>
    </html>
    """

    return html_code


async def generate_markdown_node(state: AgentState, config: RunnableConfig):
    """根据标题和内容生成markdown"""
    user_id = config.get("configurable", {}).get("thread_id")
    await put_msg_sentence_content(user_id, "开始生成markdown文档...")
    title = state.get('xiaohongshu_tcm_post_title')
    content = state.get('xiaohongshu_tcm_post_content')
    image_path_list = state.get('xiaohongshu_image_path_list', [])
    is_can_publish_xiaohongshu = state.get("is_can_publish_xiaohongshu", True)
    print(image_path_list)
    xiaohongshu_success_fail = generate_xiaohongshu_success_fail(is_can_publish_xiaohongshu)
    markdown = generate_markdown_code(title, content, image_path_list, xiaohongshu_success_fail)
    state['xiaohongshu_markdown_output'] = markdown
    state['output'] = markdown
    await put_reply_content(user_id, markdown)
    await put_msg_sentence_content(user_id, "完成生成markdown文档...")
    return state


if __name__ == '__main__':
    print(generate_markdown_code("标题", "内容",
                                 ["/Users/duyi/PycharmProjects/auto_xiaohongshu_project/picture/20251014205753.png",
                                  "/Users/duyi/PycharmProjects/auto_xiaohongshu_project/picture/20251014210618.png"]))
