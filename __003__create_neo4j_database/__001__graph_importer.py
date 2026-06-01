import json

from common.neo4j_manager import neo4j_client
from common.path_utils import get_file_path
from tqdm import tqdm


# ======================
# 知识图谱导入逻辑
# ======================
class TCMGraphImporter:
    def __init__(self, neo4j_client):
        self.neo4j_client = neo4j_client

    def create_entity(self, entity):
        """
        创建或合并实体节点（MERGE 保证唯一）
        """
        label = entity["type"]
        name = entity["name"]
        attributes = entity.get("attributes", {}) or {}

        # 构造属性字段
        set_clause = ", ".join([f"n.{k} = ${k}" for k in attributes.keys()])
        parameters = {"name": name, **attributes}

        if set_clause:
            cypher = f"""
                MERGE (n:{label} {{name: $name}})
                SET {set_clause}
            """
        else:
            cypher = f"MERGE (n:{label} {{name: $name}})"
        self.neo4j_client.run_cypher(cypher, parameters)

    def create_relation(self, relation):
        """
        创建关系
        """
        cypher = f"""
        MATCH (a:{relation['subject_type']} {{name: $subject}}),
              (b:{relation['object_type']} {{name: $object}})
        MERGE (a)-[r:{relation['relation']}]->(b)
        """
        params = {"subject": relation["subject"], "object": relation["object"]}
        self.neo4j_client.run_cypher(cypher, params)

    def import_from_json(self, json_path):
        """
        从 JSON 文件读取并导入到 Neo4j
        """
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in tqdm(data["results"], desc="总进度"):
            try:
                extract_dict = item["extract_dict"]
                entities = extract_dict["entities"]
                relations = extract_dict["relations"]

                # 1️⃣ 插入实体
                for ent in entities:
                    self.create_entity(ent)

                # 2️⃣ 插入关系
                for rel in relations:
                    self.create_relation(rel)
            except Exception as e:
                print(f"❌ 错误：{item['filename']}")
                print(f"❌ 错误：{e}")
                continue

        print("✅ 数据已成功导入 Neo4j 数据库！")


if __name__ == "__main__":
    tcm_graph_importer = TCMGraphImporter(neo4j_client)
    tcm_graph_importer.import_from_json(get_file_path("__002__extract_information/extract_formula_data.json"))
    tcm_graph_importer.import_from_json(get_file_path("__002__extract_information/extract_herb_data.json"))
