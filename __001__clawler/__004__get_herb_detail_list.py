import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm


def fetch_formula_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    # 提取标题
    title_tag = soup.find("h1", class_="p_title")
    title_text = title_tag.get_text(strip=True) if title_tag else "未知标题"

    # 定位正文主区域
    main_div = soup.select_one(".p_main_container")
    if not main_div:
        print(f"❌ 未找到正文区域：{url}")
        return None, None

    # 提取结构化文本
    content_lines = []

    for tag in main_div.find_all(["h1", "h2", "h3", "p", "ul", "ol", "div"]):
        if tag.name in ["p", "h2", "h3"]:
            text = tag.get_text(separator="", strip=True)
            if text:
                content_lines.append(text)
        elif tag.name in ["ul", "ol"]:
            for li in tag.find_all("li", recursive=False):
                li_text = li.get_text(separator="", strip=True)
                if li_text:
                    content_lines.append(f"- {li_text}")

    # 去除空行并组合文本
    content_lines = [line for line in content_lines if line.strip()]
    full_text = f"【中药名称】{title_text}\n" + "\n".join(content_lines)

    return title_text, full_text


def batch_fetch_from_excel(excel_path, overwrite=False):
    df = pd.read_excel(excel_path)
    output_dir = "中药"
    os.makedirs(output_dir, exist_ok=True)

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="📦 抓取中医中药内容"):
        formula_name = str(row["中药名称"]).strip()
        formula_url = str(row["完整链接"]).strip()

        # 先构造预期文件名
        safe_title = formula_name.replace("/", "_")
        filepath = os.path.join(output_dir, f"{safe_title}.txt")

        # 若文件已存在，直接跳过
        if os.path.exists(filepath) and not overwrite:
            tqdm.write(f"⏩ 已存在，跳过：{safe_title}.txt")
            continue

        try:
            title, content = fetch_formula_details(formula_url)
            if content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                tqdm.write(f"✅ 保存成功：{safe_title}.txt")
            else:
                tqdm.write(f"⚠️ 内容为空：{formula_name}")
        except Exception as e:
            tqdm.write(f"❌ 出错：{formula_name}，错误信息：{e}")


if __name__ == "__main__":
    batch_fetch_from_excel("中医中药列表.xlsx", overwrite=False)
