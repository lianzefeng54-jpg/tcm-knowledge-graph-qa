import json

from common.path_utils import get_file_path

json_file_path1 = get_file_path("__002__extract_information/extract_formula_finetune_data.json")
json_file_path2 = get_file_path("__002__extract_information/extract_herb_finetune_data.json")

with open(json_file_path1, "r", encoding="utf-8") as f:
    data_list1 = json.load(f)

with open(json_file_path2, "r", encoding="utf-8") as f:
    data_list2 = json.load(f)

all_data_list = data_list1 + data_list2
print(len(all_data_list))

with open(get_file_path("__007__fine_tune/zhongyi_zh_demo.json"), "w", encoding="utf-8") as f:
    json.dump(all_data_list, f, ensure_ascii=False, indent=2)
