import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_formulas(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    result = []
    main_div = soup.find("div", class_="p_content")
    if not main_div:
        print("未找到主内容区块")
        return result

    current_category = None       # 方剂大类，如“解表剂”
    current_subcategory = None   # 功效分类，如“辛温解表”

    for tag in main_div.find_all(["h2", "strong", "a"]):
        if tag.name == "h2":
            current_category = tag.text.strip()
        elif tag.name == "strong":
            current_subcategory = tag.text.strip()
        elif tag.name == "a" and tag.get("href", "").startswith("/wiki/"):
            formula_name = tag.text.strip()
            formula_url = tag["href"]
            result.append([
                formula_name,
                current_subcategory,
                current_category,
                formula_url
            ])
    return result

if __name__ == "__main__":
    url = "https://zhongyibaike.com/wiki/中药大全"
    data = fetch_formulas(url)

    df = pd.DataFrame(data, columns=["中药名称", "功效分类", "中药大类", "相对链接"])
    df["完整链接"] = "https://zhongyibaike.com" + df["相对链接"]

    # 保存为 Excel 文件
    df.to_excel("中医中药列表.xlsx", index=False)
    print("已成功保存为：中医中药列表.xlsx")
