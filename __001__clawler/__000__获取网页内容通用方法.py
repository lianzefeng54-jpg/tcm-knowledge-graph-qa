import os
import requests
import pandas as pd
from bs4 import BeautifulSoup


def fetch_formula_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    print(response.text)


if __name__ == "__main__":
    fetch_formula_details("https://zhongyibaike.com/tag/%E7%96%BE%E7%97%85%E5%A4%A7%E5%85%A8/%E5%86%85%E7%A7%91%E7%96%BE%E7%97%85")
