from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from typing import List, Optional, Union, Literal
from langchain_core.prompts import PromptTemplate
import os
from tqdm import tqdm
import json

from common.llm import my_llm
from common.path_utils import get_file_path

# ======================
# 枚举定义
# ======================
EntityType = Literal["Symptom", "Disease", "Formula", "Herb", "Effect", "Source"]

RelationType = Literal[
    "TREATS_DISEASE",
    "ALLEVIATES_SYMPTOM",
    "HAS_EFFECT",
    "HAS_INGREDIENT",
    "HAS_SYMPTOM",
    "FROM_SOURCE"
]


# ======================
# 属性定义
# ======================
class FormulaAttributes(BaseModel):
    alias: Optional[str] = None
    effect: Optional[str] = None
    indication: Optional[str] = None
    taboo: Optional[str] = None
    usage: Optional[str] = None


class HerbAttributes(BaseModel):
    dosage: Optional[str] = None
    effect: Optional[str] = None
    indication: Optional[str] = None
    meridian: Optional[str] = None
    origin: Optional[str] = None
    place: Optional[str] = None
    processing: Optional[str] = None
    property_flavor: Optional[str] = None
    taboo: Optional[str] = None
    traits: Optional[str] = None


# ======================
# 实体与关系结构
# ======================
class Entity(BaseModel):
    name: str
    type: EntityType
    attributes: Optional[Union[FormulaAttributes, HerbAttributes]] = None


class Relation(BaseModel):
    subject: str
    subject_type: EntityType
    relation: RelationType
    object: str
    object_type: EntityType


class TCMKnowledgeGraph(BaseModel):
    entities: List[Entity]
    relations: List[Relation]


# 初始化解析器
parser = JsonOutputParser(pydantic_object=TCMKnowledgeGraph)

# 定义 Prompt
prompt = PromptTemplate(
    template=(
        "你是一个中医知识图谱抽取专家。请从以下文本中提取结构化知识：\n"
        "仅当文本中存在实体之间的明确关系时（如‘某方剂治疗某疾病’、‘某药材具有某功效’、‘方剂包含药材’等），才进行抽取。\n"
        "如果文本中仅描述单个实体的信息、未涉及其他实体或关系，请不要抽取，返回空结构：\n"
        "{{\"entities\": [], \"relations\": []}}\n\n"

        "【实体类型说明】\n"
        "- Symptom：症状，如咳嗽、腹痛等\n"
        "- Disease：疾病，如感冒、肺炎、肾虚等\n"
        "- Formula：方剂，如四君子汤、桂枝汤等\n"
        "- Herb：药材，如人参、黄芪、丁香等\n"
        "- Effect：功效，如补气、活血、祛湿、止痛等\n"
        "- Source：出处，如《本草纲目》《伤寒论》等\n\n"

        "【关系类型说明】\n"
        "- TREATS_DISEASE：方剂或药材治疗某种疾病\n"
        "- ALLEVIATES_SYMPTOM：方剂或药材缓解某种症状\n"
        "- HAS_EFFECT：方剂或药材具有某种功效\n"
        "- HAS_INGREDIENT：方剂包含某种药材\n"
        "- HAS_SYMPTOM：疾病包含某种症状\n"
        "- FROM_SOURCE：方剂出自某文献或出处\n\n"

        "若文本涉及方剂或药材，请补充对应的属性字段（如功效、性味、剂量等）。\n"
        "如果文本主要是讲方剂的，请不要抽取药材的属性字段。\n"
        "如果文本主要是讲药材的，请不要抽取方剂的属性字段。\n"
        "如果值为空null，则不必显示键的值。"
        "所有输出必须严格符合以下 JSON 格式：\n"
        "{format_instructions}\n\n"
        "输入文本：{text}"
    ),
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)


# ======================
# 主函数封装
# ======================
def extract_tcm_knowledge(text: str) -> TCMKnowledgeGraph:
    # 构建抽取链
    chain = prompt | my_llm | parser
    return chain.invoke({"text": text})


def load_existing_results(save_path: str):
    """加载已存在的JSON结果，用于断点续跑"""
    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict) and "results" in data:
                    return data
            except json.JSONDecodeError:
                pass
    return {"results": []}


def save_results(data: dict, save_path: str):
    """将当前结果保存到JSON"""
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_from_folder(folder_path: str, save_path: str, finetune_save_path: str):
    all_results = load_existing_results(save_path)
    processed_files = {r["filename"] for r in all_results["results"]}

    # 用于存储微调数据
    finetune_data = []
    if os.path.exists(finetune_save_path):
        with open(finetune_save_path, "r", encoding="utf-8") as f:
            try:
                finetune_data = json.load(f)
            except json.JSONDecodeError:
                pass

    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    print(f"🔍 共发现 {len(txt_files)} 个文本文件。")

    for filename in tqdm(txt_files, desc="处理中..."):
        if filename in processed_files:
            print(f"⏭ 跳过已处理文件：{filename}")
            continue

        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if not text:
                tqdm.write(f"⚠️ 文件为空：{filename}")
                continue

        try:
            result_dict = extract_tcm_knowledge(text)
            record = {
                "filename": filename,
                "extract_dict": result_dict
            }

            all_results["results"].append(record)
            save_results(all_results, save_path)
            tqdm.write(f"✅ 已保存结果：{filename}")

            # === 新增：保存微调格式 ===
            finetune_item = {
                "instruction": "请从以下中医文本中抽取知识图谱结构，包括实体与关系。",
                "input": text,
                "output": json.dumps(
                    result_dict,
                    ensure_ascii=False,
                    indent=2
                )
            }
            finetune_data.append(finetune_item)
            with open(finetune_save_path, "w", encoding="utf-8") as f:
                json.dump(finetune_data, f, ensure_ascii=False, indent=2)

            tqdm.write(f"📘 已追加微调数据：{filename}")


        except Exception as e:
            tqdm.write(f"❌ 处理失败：{filename}, 错误：{e}")

    print(f"\n🎯 处理完成，共抽取 {len(all_results['results'])} 个文件结果。")


# ======================
# ✅ 示例调用
# ======================
if __name__ == "__main__":
    ...
    # print(extract_tcm_knowledge("我今天有点头疼，该吃什么药呢？"))
    # extract_from_folder(get_file_path("__001__clawler/中药"),
    #                     get_file_path("__002__extract_information/extract_formula_data.json"))
#     example_text = """
#     【中药名称】三叶鬼针草
# - 中医百科
# - 三叶鬼针草
# 盲肠草
# - 盲肠草
# 三叶鬼针草的种植和炮制
# 来源
# 为菊科植物三叶鬼针草Bidens pilosa L.的全草。夏、秋季采收，晒干或鲜用。
# 【原形态】
# 三叶鬼针草，一年生草本，高30-100cm。茎钝四棱形，无毛呀上部被极稀的柔毛。茎下部叶较小，3裂或不分裂，通常在开花前枯萎；中部叶具柄，柄长1.5-5cm，三出；小叶3枚，很少为5-7的羽状复叶，两侧小叶椭圆形或卵状椭圆形，先端锐尖，基部近圆或阔楔形，有时不对稀，具短柄，边缘有锯齿，顶端小叶较大，长椭圆形或卵状长圆形，先端渐尖，基部渐狭或近圆形，具1-2cm，的柄，边缘有锯齿，上部叶小，3裂或不分裂，线状披针形。头状花序单生，有长1-6（果时长3-10）cm的花序梗；总苞基部被短柔毛，苞片7-8枚，线状匙形，上部较宽，果时长至5mm，外层托片披针形，背面褐色，具黄色边缘，内层较狭，线状披针形；舌状花白色或无舌状花；盘花筒状，冠檐5齿裂。瘦果黑色，线形，略扁，具棱，上部具稀疏瘤状突起及刚毛，先端芒刺3-4枚，具倒刺毛。花期春季。
# 【生境分布】
# 生于路边、荒野。分布于华北、华东、中南、西南。
# 性味
# 性平，味苦。
# 性状
# 茎钝四棱形，基部直径可达6mm。中部叶对生，茎下部叶较小，常在开花前枯萎；中部叶对生具柄，三出，小叶椭圆形或卵状椭圆形，叶缘具粗锯齿；顶生小叶稍大对生或互生。头状花序总苞草质，绿色，边缘被短柔毛，托片膜质，背面褐色，边缘黄棕色；花黄棕色或黄褐色，无舌状花。有时可见10余个长条形具4棱的果实；果实棕黑色，先端有针状冠毛3-4条，具倒刺。气微，味淡。
# 三叶鬼针草的效果
#     """
#     result_dict = extract_tcm_knowledge(example_text)
#     print("\n\n=== 解析结果 ===")
#     print(result_dict)
