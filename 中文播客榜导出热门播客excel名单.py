import json
import re
from datetime import datetime

import numpy as np
import requests

from bs4 import BeautifulSoup

import pandas as pd
import json
import pytz

# Constants
SCRIPT_SRC_PATTERN = r'<script[^>]+type="module"[^>]*src="([^"]+)"'
PI_PATTERN = r'pI="([^"]+)"'
GI_PATTERN = r'gI="([^"]+)"'
MI_PATTERN = r'mI="([^"]+)"'
_I_PATTERN = r'_I="([^"]+)"'

def convert_date_format(date_str):
    # 解析日期字符串
    try:
        dt = datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S %Z%z (China Standard Time)")
        china_tz = pytz.timezone('Asia/Shanghai')
        dt = dt.astimezone(china_tz)  # 转换日期到指定的格式并返回
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-7]
    except ValueError:
        return np.nan  # 如果转换失败，返回 NaN


def convert_date_format1(date_str):
    # 解析日期字符串
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
        china_tz = pytz.timezone('Asia/Shanghai')
        dt = dt.astimezone(china_tz)  # 转换日期到指定的格式并返回
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-7]
    except ValueError:
        return np.nan  # 如果转换失败，返回 NaN

def get_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print("Error getting page:", e)
        return None


def extract_script_src(page):
    match = re.search(SCRIPT_SRC_PATTERN, page)
    if match:
        return match.group(1)
    return None


def parse_script(script):
    pi = re.search(PI_PATTERN, script)
    gi = re.search(GI_PATTERN, script)
    mi = re.search(MI_PATTERN, script)
    _i = re.search(_I_PATTERN, script)

    if pi and gi and mi and _i:
        return pi.group(1), gi.group(1), mi.group(1), _i.group(1)
    else:
        print("Failed to extract keys")
        return None, None, None, None


def parse_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    data = json.loads(soup.find('script', id='__NEXT_DATA__').string)
    return data


# API Requests
def make_api_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print("API request failed:", e)
        return None

def get_podcast_data(pi):
    response = make_api_request(pi)
    if response and response.status_code == 200:
        obj = response.json()
        return obj
    else:
        return None

def export(data):
    # 为链接创建新的键值对
    for podcast in data['data']['podcasts']:
        for link in podcast['links']:
            key_name = link['name'] + '_link'
            podcast[key_name] = link['url']
        del podcast['links']

    # 将数据转换为 DataFrame
    df = pd.json_normalize(data['data']['podcasts'])

    df['lastReleaseDate'] = df['lastReleaseDate'].apply(convert_date_format)
    df['firstEpisodePostTime'] = df['firstEpisodePostTime'].apply(convert_date_format1)

    # 定义中文表头映射
    column_mapping = {
        "rank": "排名",
        "name": "名称",
        "primaryGenreName": "主要类型",
        "authorsText": "作者",
        "trackCount": "总集数",
        "lastReleaseDate": "最后发布日期",
        "lastReleaseDateDayCount": "最近更新天数",
        "firstEpisodePostTime": "首个节目发布时间",
        "activeRate": "活跃率",
        "avgDuration": "平均时长",
        "avgPlayCount": "平均播放数",
        "avgUpdateFreq": "平均更新频率",
        "avgCommentCount": "平均评论数",
        "avgInteractIndicator": "单播互动量",
        "avgOpenRate": "平均打开率",
        "xyz_link": "小宇宙链接",
        "apple_link": "iTunes链接",
        "rss_link": "RSS链接",
        "website_link": "官方网站链接"
    }
    # 添加不存在的列并为其赋予 NaN 值
    for col in column_mapping.keys():
        if col not in df.columns:
            df[col] = np.nan
    # 替换 DataFrame 列名为中文
    df.rename(columns=column_mapping, inplace=True)

    # 导出到 Excel
    df.to_excel('output.xlsx', index=False, columns=list(column_mapping.values()))

    # 导出到 CSV
    df.to_csv('output.csv', index=False, columns=list(column_mapping.values()))

def main():
    page = get_page('https://xyzrank.com/')

    # 2. Extract script src
    script_src = extract_script_src(page)

    # 3. Parse script
    pi, gi, mi, _i = parse_script(get_page(script_src))

    # 4. Make API requests
    podcast_data = get_podcast_data(pi)

    # 5. Export to Excel
    export(podcast_data)

if __name__ == '__main__':
    main()