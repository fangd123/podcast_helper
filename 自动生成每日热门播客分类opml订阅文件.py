import json
import re
from datetime import datetime

import numpy as np
import requests
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

import pandas as pd
import pytz

def parse_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    data = json.loads(soup.find('script', id='__NEXT_DATA__').string)
    return data

def fetch_title(url, type='rss'):
    try:
        response = requests.get(url)
        response.raise_for_status()
        title = ''
        if type == 'rss':
            tree = ET.fromstring(response.content)
            channel = tree.find("channel")
            title = channel.find("title").text if channel is not None else 'Unknown Title'

        elif type == 'xyz':
            data = parse_html(response.text)
            title = data['props']['pageProps']['podcast']['title']

        return title
    except requests.RequestException:
        return 'Unknown Title'

def generate_opml(names:list, rss_list: list, xyz_list: list = [], opml_filename="output.opml"):
    opml = ET.Element("opml", version="2.0")
    head = ET.SubElement(opml, "head")
    ET.SubElement(head, "title").text = "我的播客订阅"
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    ET.SubElement(head, "dateCreated").text = current_time
    body = ET.SubElement(opml, "body")

    count = max(len(rss_list), len(xyz_list))
    rss_list.extend([None] * (count - len(rss_list)))
    xyz_list.extend([None] * (count - len(xyz_list)))

    for name, rss_url, xyz_url in zip(names, rss_list, xyz_list):
        attrs = {
            "text": name,
            "title": name,
            "type": "rss",
            "xmlUrl": rss_url,
            "version": "RSS"
        }
        ET.SubElement(body, "outline", **attrs)

    tree = ET.ElementTree(opml)
    tree.write(opml_filename, encoding="utf-8", xml_declaration=True)

def main(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')

    unique_primary_genres = df['主要类型'].unique()

    combined_names = []
    combined_xiaoyuzhou_links = []
    combined_rss_links = []

    for genre in unique_primary_genres:
        filtered_df = df[df['主要类型'] == genre]
        if len(filtered_df) < 5:
            combined_names.extend(filtered_df['名称'].tolist())
            combined_xiaoyuzhou_links.extend(filtered_df['小宇宙链接'].tolist())
            combined_rss_links.extend(filtered_df['RSS链接'].tolist())
        else:
            names = filtered_df['名称'].tolist()
            xiaoyuzhou_links = filtered_df['小宇宙链接'].tolist()
            rss_links = filtered_df['RSS链接'].tolist()

            # Generating a filename based on the primary genre
            opml_filename = f"20230906/{genre}.opml"
            generate_opml(names, xiaoyuzhou_links, rss_links, opml_filename)

    # Generating combined OPML file for primary genres with counts less than 5
    if combined_names:
        generate_opml(combined_names, combined_xiaoyuzhou_links, combined_rss_links, "20230906/combined.opml")

if __name__ == '__main__':
    main('output.xlsx')