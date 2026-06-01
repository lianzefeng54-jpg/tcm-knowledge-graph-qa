import requests
import json


def query_zhongyi_fastapi(input: str):
    url = "http://127.0.0.1:8000/process"
    payload = {"input": input, "user_id": "user_002"}

    result = requests.post(url, json=payload, stream=True)
    for chunck in result.iter_content(chunk_size=None):
        print(json.loads(chunck.decode("utf-8")))
    # json_dict = res.json()
    # return json_dict["output"]


query_zhongyi_fastapi("你好")
