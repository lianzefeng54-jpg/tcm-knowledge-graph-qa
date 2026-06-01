from openai import OpenAI

client = OpenAI(api_key="0",
                base_url="https://14aa1c57c03d4055858e5695256cdd4c--8000.ap-shanghai2.cloudstudio.club/v1")
messages = [{"role": "system", "content": "请从以下中医文本中抽取知识图谱结构，包括实体与关系。"},
            {"role": "user",
             "content": "【方剂名称】斩梦丹\n- 中医百科\n- 斩梦丹\n斩梦丹的药方\n出处\n《普济方》卷三十三\n组成\n知母30克黄柏30克（去皮）滑石90克\n【制法】\n上药为末，白水和丸。\n斩梦丹的功效\n主治\n治梦泄遗精。\n用法\n空腹时温酒送下。"}]

completions = client.chat.completions.create(
    messages=messages,
    model="/workspace/models/Qwen/Qwen2.5-0.5B-Instruct",
    stream=True)

for chunk in completions:
    print(chunk.choices[0].delta.content, end="", sep="", flush=True)
