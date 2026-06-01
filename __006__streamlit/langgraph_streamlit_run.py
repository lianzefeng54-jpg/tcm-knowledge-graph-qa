import os

from common.path_utils import get_file_path

streamlit_path = get_file_path("__006__streamlit/langgraph_streamlit.py")
os.system(
    f"streamlit run {streamlit_path}")
