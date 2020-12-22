import os
import datetime
from pathlib import Path

import pytz
import requests
from lxml import etree

from app.setting import PROXY
from app.libs.helper import exec_sql, query_size
from app.robot.index import send_message
from app.qiniu.index import save_file_2_qiniu

tz = pytz.timezone("America/New_York")

base_url = "https://www.pbs.org/newshour/latest"

# set retries number
requests.adapters.DEFAULT_RETRIES = 15
s = requests.session()
# close useless connect
s.keep_alive = False


def fetch_content(url, type="text"):
    try:
        r = requests.get(url, proxies=PROXY if type != "text" else None, timeout=60)
        if type == "text":
            return r.text

        return r.content
    except Exception as e:
        raise Exception(f"{e}")


def save_assets(url, date, type="audio"):
    cur_dir = os.getcwd()
    ext_name = "mp3" if type == "audio" else "jpg"
    asset_name = f"pbs_newswrap_{date.strftime('%Y%m%d')}.{ext_name}"
    asset_path = os.path.join(cur_dir, f"static/{type}", f"{asset_name}")
    if Path(asset_path).exists():
        return asset_name

    qiniu_key = save_file_2_qiniu(url, asset_name)
    if qiniu_key:
        return qiniu_key

    f = open(asset_path, "wb")
    f.write(fetch_content(url, "byte"))
    f.close()
    return asset_name


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
    news_wrap = parse_list()
    if "source" not in news_wrap:
        return "There is no news wrap now!"

    source = news_wrap.get("source")
    title = news_wrap.get("title")
    # check database
    sql = f"Select `id` from `news` where `title`=%s"
    article_id = query_size(sql, title)
    if article_id:
        return "It Exists"

    article_html = etree.HTML(fetch_content(source))

    audioEl = article_html.xpath("//audio/source/@src")
    transcriptEl = article_html.xpath(
        '//div[@id="transcript"]/ul[@class="video-transcript"]'
    )
    summaryEl = article_html.xpath(
        '//div[@id="transcript"]/div[@class="vt__excerpt body-text"]/p/text()'
    )
    audio_from = ""
    audio_url = ""
    image_from = ""
    transcript = ""
    summary = ""
    image_url = ""
    today = datetime.datetime.now(tz).date()
    if len(transcriptEl) > 0:
        transcript = etree.tostring(transcriptEl[0]).decode()
        text_list = etree.HTML(transcript).xpath("//li/div/p/text()")
        if len(summaryEl) > 0:
            summary = summaryEl[0]
        else:
            summary = len(text_list) > 0 and text_list[0]

    if len(audioEl) > 0:
        audio_from = audioEl[0]
        audio_url = save_assets(audio_from, today)
        image_from = news_wrap.get("image_from")
        if image_from:
            image_url = save_assets(image_from, today, type="image")

    if audio_url and transcript:
        sql = "INSERT INTO `news` \
        (`title`,`transcript`,`summary`,`audio_url`, `image_url`,`source`,`audio_from`,`image_from`,`date`) \
        VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s)"
        values = (
            title,
            transcript,
            summary,
            audio_url,
            image_url,
            source,
            audio_from,
            image_from,
            today,
        )
        return exec_sql(sql, values)
    return "News is still on the way!"


def push_news_by_date(date):
    q_sql = f"Select `id`,`title`,`summary`,`image_url` from `news` where `date`=%s"
    result = query_size(q_sql, date)
    err_msg = {"errmsg": "Push Fail!"}
    if result:
        # 05-12-2020
        article = result[0]
        f_date = date.strftime("%d-%m-%Y")
        err_msg = send_message(
            id=article[0],
            title=f"{f_date}:{article[1]}",
            content=article[2],
            picUrl=f"image/{article[3]}",
        )
    return err_msg


if __name__ == "__main__":
    try:
        print("Start Crawl...")
        result = parse_transcript_audio()
        print(f"Crawl Result: {result}")
        if result == "Ok":
            today = datetime.datetime.now(tz).date()
            # print(today + datetime.timedelta(-1))
            r_dict = push_news_by_date(today)
            print(f"Push Result: {r_dict.get('errmsg')}")
    except Exception as e:
        print(f"Error: {e}")
