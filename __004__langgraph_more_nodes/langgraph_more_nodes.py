from langchain_core.runnables import RunnableConfig
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from __004__langgraph_more_nodes.agent_state import AgentState
from __004__langgraph_more_nodes.nodes.check_text_image_node import check_text_image_node
from __004__langgraph_more_nodes.nodes.xiaohongshu_publish_intent_node import xiaohongshu_publish_intent_node
from __004__langgraph_more_nodes.nodes.text_generate_node import text_generate_node
from __004__langgraph_more_nodes.nodes.image_generate_node import image_generator_node
from __004__langgraph_more_nodes.nodes.auto_publish_xiaohongshu_node import xiaohongshu_auto_publish_node
from __004__langgraph_more_nodes.nodes.zhongyi_intent_node import zhongyi_intent_node
from __004__langgraph_more_nodes.nodes.llm_direct_out_node import llm_direct_out_node
from __004__langgraph_more_nodes.nodes.extract_entity_from_user_input_node import extract_entity_from_user_input_node
from __004__langgraph_more_nodes.nodes.match_entity_from_neo4j_node import match_entity_from_neo4j_node
from __004__langgraph_more_nodes.nodes.generate_neo4j_cypher_node import generate_neo4j_cypher_node
from __004__langgraph_more_nodes.nodes.check_cypher_node import check_cypher_node
from __004__langgraph_more_nodes.nodes.run_cypher_node import run_cypher_node
from __004__langgraph_more_nodes.nodes.neo4j_answer_generate_node import neo4j_answer_generate_node
from __004__langgraph_more_nodes.nodes.generate_markdown_node import generate_markdown_node
from __004__langgraph_more_nodes.nodes.semantic_transcription_node import semantic_transcription_node
from common.ouput_graph_utils import output_pic_graph
from common.path_utils import get_file_path


def build_graph():
    # 定义状态图
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node(semantic_transcription_node.__name__, semantic_transcription_node)
    graph_builder.add_node(xiaohongshu_publish_intent_node.__name__, xiaohongshu_publish_intent_node)
    graph_builder.add_node(text_generate_node.__name__, text_generate_node)
    graph_builder.add_node(image_generator_node.__name__, image_generator_node)
    graph_builder.add_node(xiaohongshu_auto_publish_node.__name__, xiaohongshu_auto_publish_node)
    graph_builder.add_node(zhongyi_intent_node.__name__, zhongyi_intent_node)
    graph_builder.add_node(llm_direct_out_node.__name__, llm_direct_out_node)
    graph_builder.add_node(extract_entity_from_user_input_node.__name__, extract_entity_from_user_input_node)
    graph_builder.add_node(match_entity_from_neo4j_node.__name__, match_entity_from_neo4j_node)
    graph_builder.add_node(generate_neo4j_cypher_node.__name__, generate_neo4j_cypher_node)
    graph_builder.add_node(check_cypher_node.__name__, check_cypher_node)
    graph_builder.add_node(run_cypher_node.__name__, run_cypher_node)
    graph_builder.add_node(neo4j_answer_generate_node.__name__, neo4j_answer_generate_node)
    graph_builder.add_node(check_text_image_node.__name__, check_text_image_node)
    graph_builder.add_node(generate_markdown_node.__name__, generate_markdown_node)

    # 添加边
    graph_builder.add_edge(START, semantic_transcription_node.__name__)
    graph_builder.add_edge(semantic_transcription_node.__name__, xiaohongshu_publish_intent_node.__name__)

    def is_xiaohongshu_publish_intent_condition(state: AgentState):
        if state['is_xiaohongshu_publish_intent']:
            return text_generate_node.__name__
        else:
            return zhongyi_intent_node.__name__

    graph_builder.add_conditional_edges(xiaohongshu_publish_intent_node.__name__, is_xiaohongshu_publish_intent_condition,
                                path_map={
                                    text_generate_node.__name__: text_generate_node.__name__,
                                    zhongyi_intent_node.__name__: zhongyi_intent_node.__name__
                                })

    def is_zhongyi_intent_condition(state: AgentState):
        if state['is_zhongyi_intent']:
            return extract_entity_from_user_input_node.__name__
        else:
            return llm_direct_out_node.__name__

    graph_builder.add_conditional_edges(zhongyi_intent_node.__name__, is_zhongyi_intent_condition,
                                path_map={
                                    extract_entity_from_user_input_node.__name__: extract_entity_from_user_input_node.__name__,
                                    llm_direct_out_node.__name__: llm_direct_out_node.__name__
                                })
    graph_builder.add_edge(extract_entity_from_user_input_node.__name__, match_entity_from_neo4j_node.__name__)
    graph_builder.add_edge(match_entity_from_neo4j_node.__name__, generate_neo4j_cypher_node.__name__)
    graph_builder.add_edge(generate_neo4j_cypher_node.__name__, check_cypher_node.__name__)

    def is_all_validate_cypher_condition(state: AgentState):
        if state['is_all_validate_cypher']:
            return run_cypher_node.__name__
        else:
            return generate_neo4j_cypher_node.__name__

    graph_builder.add_conditional_edges(check_cypher_node.__name__, is_all_validate_cypher_condition,
                                path_map={
                                    run_cypher_node.__name__: run_cypher_node.__name__,
                                    generate_neo4j_cypher_node.__name__: generate_neo4j_cypher_node.__name__
                                }
                                )
    graph_builder.add_edge(run_cypher_node.__name__, neo4j_answer_generate_node.__name__)
    graph_builder.add_edge(neo4j_answer_generate_node.__name__, END)
    graph_builder.add_edge(text_generate_node.__name__, image_generator_node.__name__)
    graph_builder.add_edge(image_generator_node.__name__, check_text_image_node.__name__)

    def is_check_text_image_condition(state: AgentState):
        if state['is_can_publish_xiaohongshu']:
            return xiaohongshu_auto_publish_node.__name__
        else:
            return generate_markdown_node.__name__

    graph_builder.add_conditional_edges(check_text_image_node.__name__, is_check_text_image_condition, path_map={
        xiaohongshu_auto_publish_node.__name__: xiaohongshu_auto_publish_node.__name__,
        generate_markdown_node.__name__: generate_markdown_node.__name__
    })
    graph_builder.add_edge(xiaohongshu_auto_publish_node.__name__, generate_markdown_node.__name__)
    graph_builder.add_edge(generate_markdown_node.__name__, END)

    # 编译状态图
    graph = graph_builder.compile()
    return graph


graph = build_graph()
# 输出表的状态图
output_pic_graph(graph, get_file_path("__004__langgraph_more_nodes/graph.jpg"))


async def zhongyi_response(input: str, thread_id: str):
    config = RunnableConfig(configurable={
        "thread_id": thread_id
    })
    result = await graph.ainvoke({"input": input}, config=config)
    return result["output"]
