import os
import datetime

import pytz
import requests
from lxml import etree

from app.setting import PROXY
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


def save_image(url):
    cur_dir = os.getcwd()
    path = "pbs_newswrap_" + today.strftime("%Y%m%d") + ".jpg"
    f = open(os.path.join(cur_dir, "static/image", path), "wb")
    f.write(fetch_content(url, "byte"))
    f.close()
    return path


def parse_list(url=base_url):
    content = fetch_content(url)
    news_list_html = etree.HTML(content)
    articles = news_list_html.xpath(
        '//div[@class="latest__wrapper"]/article/div[@class="card-timeline__col-right"]'
    )

    news_wrap = {}
    for item in articles:
        article_html = etree.HTML(etree.tostring(item).decode())
        titleEl = article_html.xpath('//a[@class="card-timeline__title"]/span')
        title = len(titleEl) > 0 and titleEl[0].text
        title = title and title.replace("\n", "").strip()
        if title and title.lower().find("news wrap") != -1:
            articleEl = article_html.xpath('//a[@class="card-timeline__title"]')
            imageEl = article_html.xpath('//a[@class="card-timeline__img-link"]/img')
            article_from = len(articleEl) > 0 and articleEl[0].get("href")
            image_from = len(imageEl) > 0 and imageEl[0].get("src")

            news_wrap["title"] = title
            if article_from:
                news_wrap["source"] = article_from
            if image_from:
                news_wrap["image_from"] = image_from
            break

    return news_wrap


def parse_transcript_audio():
    # check database
    f_today = today.strftime("%Y-%m-%d")
    sql = f"Select `id` from `news` where `date`= %s"
    article_id = query_size(sql, f_today)
    if article_id:
        return "It Exists"

    news_wrap = parse_list()
    if "source" not in news_wrap:
        return "Can't Fetch File"

    source = news_wrap["source"]
    title = news_wrap["title"]
    image_from = "http://192.168.8.149:5000/The%20Latest%20_%20PBS%20NewsHour_files/newswrap15-425x300.jpg"
    # image_from = news_wrap["image_from"]
    article_html = etree.HTML(fetch_content(source))
    audioEl = article_html.xpath("//audio/source/@src")
    transcriptEl = article_html.xpath(
        '//div[@id="transcript"]/ul[@class="video-transcript"]'
    )
    transcript = (
        etree.tostring(transcriptEl[0]).decode()
        if len(transcriptEl) > 0
        else "no transcript"
    )
    text_list = etree.HTML(transcript).xpath("//li/div/p/text()")
    summary = len(text_list) > 0 and text_list[0]
    if len(audioEl) > 0:
        audio_from = audioEl[0]
        audio_url = save_audio(audio_from)
        image_url = save_image(image_from)
        sql = "INSERT INTO `news` \
        (`title`,`transcript`,`audio_url`, `image_url`,`source`,`audio_from`,`image_from`,`date`) \
        VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
        values = (
            title,
            transcript,
            audio_url,
            image_url,
            source,
            audio_from,
            image_from,
            today,
        )
        save_msg = exec_sql(sql, values)
        if save_msg == "Ok":
            send_message(title=title, content=summary, picUrl=image_url)
        return save_msg
    return "No File"


if __name__ == "__main__":
    try:
        print("Start Crawl...")
        message = parse_transcript_audio()
        print(f"Crawl Result: {message}")
    except Exception as e:
        print(f"{e}")
