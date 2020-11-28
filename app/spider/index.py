import os
from os import error
import datetime

import pytz
import requests
from lxml import etree

from app.config.setting import PROXY
from app.libs.helper import exec_sql, query_size
from app.robot.index import send_message

tz = pytz.timezone("America/New_York")
today = datetime.datetime.now(tz)


base_url = "https://www.pbs.org/newshour/latest"
# base_url = "http://192.168.8.149:5000/The Latest _ PBS NewsHour.htm"

# 设置重连次数
requests.adapters.DEFAULT_RETRIES = 15
s = requests.session()
s.keep_alive = False  # 关闭多余连接


def fetch_content(url, type="text"):
    r = requests.get(url, proxies=PROXY if type != "text" else None, timeout=60)
    if type == "text":
        return r.text

    return r.content


def save_audio(url):
    cur_dir = os.getcwd()
    path = "pbs_newswrap_" + today.strftime("%Y%m%d") + ".mp3"
    f = open(os.path.join(cur_dir, "static/audio", path), "wb")
    f.write(fetch_content(url, "byte"))
    f.close()
    return path


def parse_list(url=base_url):
    content = fetch_content(url)
    html = etree.HTML(content, etree.HTMLParser())
    result = html.xpath(
        '//div[@class="latest__wrapper"]/article//div[@class="card-timeline__intro"]/a'
    )

    news_wrap = {}
    for news in result:
        href = news.get("href")
        title = news.getchildren()[0].text.replace("\n", "").strip()
        if title.lower().find("news wrap") != -1:
            news_wrap["href"] = href
            news_wrap["title"] = title

    return news_wrap


def parse_transcript_audio():
    # check database
    f_today = today.strftime("%Y-%m-%d")
    sql = f"Select `id` from `news` where `date`= %s"
    news_id = query_size(sql, f_today)
    if news_id:
        return "It Exists"

    news_wrap = parse_list()
    if "href" not in news_wrap:
        return "Can't fetch file"
    url = news_wrap["href"]
    title = news_wrap["title"]
    content = fetch_content(url)
    html = etree.HTML(content, etree.HTMLParser())
    transcriptEl = html.xpath('//div[@id="transcript"]/ul[@class="video-transcript"]')
    transcript = (
        etree.tostring(transcriptEl[0]) if len(transcriptEl) > 0 else "no transcript"
    )
    audioEl = html.xpath("//audio/source/@src")
    if len(audioEl) > 0:
        audio = audioEl[0]
        audio_url = save_audio(audio)
        sql = "INSERT INTO `news` (`audio_url`, `title`,`transcript`,`date`) VALUES (%s, %s, %s, %s)"
        values = (audio_url, title, transcript, today)
        save_msg = exec_sql(sql, values)
        send_message(title=title, content="pbs")
        return save_msg
    return "No File"


if __name__ == "__main__":
    try:
        print("Start Crawl...")
        message = parse_transcript_audio()
        print(f"Crawl Result: {message}")
    except error:
        print("Error Happened")
