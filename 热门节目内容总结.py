import json
import random
import re
import time

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Constants
SCRIPT_SRC_PATTERN = r'<script[^>]+type="module"[^>]*src="([^"]+)"'
PI_PATTERN = r'pI="([^"]+)"'
GI_PATTERN = r'gI="([^"]+)"'
MI_PATTERN = r'mI="([^"]+)"'
_I_PATTERN = r'_I="([^"]+)"'
# Page parsing
def get_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print("Error getting page:", e)
        return None

# API Requests
def make_api_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print("API request failed:", e)
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


def get_hot_episodes(mi):
    """
    Get the hot episodes from the html text.
    """
    response = make_api_request(mi)
    if response and response.status_code == 200:
        obj = response.json()
    return obj['data']['episodes']


def get_episode_info(episodes):
    """
    Get the episode info from the html text.
    """
    episodes_info = {}
    for episode in tqdm(episodes):
        time.sleep(random.randint(1, 10)/10)
        title = episode['title']
        xyz_link = episode['link']
        xyz_episode_data = parse_html(requests.get(xyz_link).text)
        description = xyz_episode_data['props']['pageProps']['episode']['description']
        url = xyz_episode_data['props']['pageProps']['episode']['enclosure']['url']
        episodes_info[title] = [description, url]
        break
    return episodes_info


def parse_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    data = json.loads(soup.find('script', id='__NEXT_DATA__').string)
    return data

if __name__ == '__main__':
    # 1. Get page
    page = get_page('https://xyzrank.com/')

    # 2. Extract script src
    script_src = extract_script_src(page)

    # 3. Parse script
    pi, gi, mi, _i = parse_script(get_page(script_src))
    episodes = get_hot_episodes(mi)
    episodes_info = get_episode_info(episodes)
    print(episodes_info)
