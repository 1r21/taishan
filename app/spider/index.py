import os
from datetime import datetime
from pathlib import Path

import pytz
import requests
from lxml import etree

from app.setting import PROXY, TARGET_URL
from app.libs.helper import exec_sql, query_size
from app.robot.index import send_message
from app.qiniu.index import save_file_2_qiniu
from app.weixin.index import upload_material, add_material
from app.ghost.index import publish_blog

tz = pytz.timezone("America/New_York")

# set retries number
requests.adapters.DEFAULT_RETRIES = 15
s = requests.session()
# close useless connect
s.keep_alive = False
s.headers.update({"cache-control": "no-cache"})


def fetch_content(url, type="text"):
    try:
        proxies = PROXY if type != "text" else None
        r = requests.get(url, proxies=proxies, timeout=60)
        return r.text if type == "text" else r.content
    except Exception as e:
        raise Exception(f"Fetch Fail: {e}")


def save_assets(url, date, file_type="audio"):
    cur_dir = os.getcwd()
    ext_name = "mp3" if file_type == "audio" else "jpg"
    asset_name = f"pbs_newswrap_{date.strftime('%Y%m%d')}.{ext_name}"
    asset_path = os.path.join(cur_dir, f"static/{file_type}", f"{asset_name}")

    if not Path(asset_path).exists():
        f = open(asset_path, "wb")
        f.write(fetch_content(url, "byte"))
        f.close()

    try:
        # save qiniu
        save_file_2_qiniu(asset_path, f"{file_type}/{asset_name}")

        # save weixin
        if file_type == "audio":
            new_filename = f"{date.strftime('%d-%m-%Y')}.{ext_name}"
            dstFile = os.path.join(cur_dir, f"static/{file_type}", f"{new_filename}")
            os.rename(asset_path, dstFile)
            upload_material(dstFile, "voice")
    except Exception as e:
        print("Save Assets Err: ", e)

    return asset_name


def parse_list(url=TARGET_URL):
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
            news_wrap["source"] = article_from
            news_wrap["image_from"] = image_from
            break
    return news_wrap


def parse_transcript_audio(date):
    news_wrap = parse_list()
    title = news_wrap.get("title")
    print("title", title)
    err_msg = "News is still on the way!"

    if not news_wrap:
        return err_msg

    sql = f"SELECT `transcript`,`source`,`title` FROM `news` WHERE `title`=%s"
    articles = query_size(sql, title)
    if articles:
        (article,) = articles
        (transcript, *_) = article
        return "News Exists" if transcript else parse_transcript(article)

    # save cover
    image_from = news_wrap.get("image_from")
    image_url = save_assets(image_from, date, file_type="image")

    source = news_wrap.get("source")
    article_html = etree.HTML(fetch_content(source))
    audioEl = article_html.xpath("//audio/source/@src")

    audio_from = ""
    audio_url = ""

    if audioEl:
        (audio_from,) = audioEl
        audio_url = save_assets(audio_from, date)

    sql = "INSERT INTO `news` \
        (`title`,`audio_url`,`image_url`,`source`,`audio_from`,`image_from`,`date`) \
        VALUES (%s,%s,%s,%s,%s,%s,%s)"
    values = (title, audio_url, image_url, source, audio_from, image_from, date)
    return exec_sql(sql, values)


def parse_transcript(article):
    (_, source, title) = article
    article_html = etree.HTML(fetch_content(source))
    transcriptEl = article_html.xpath(
        '//div[@id="transcript"]/ul[@class="video-transcript"]'
    )
    summaryEl = article_html.xpath(
        '//div[@id="transcript"]/div[@class="vt__excerpt body-text"]/p/text()'
    )

    summary = None
    transcript = None
    text_list = None

    if transcriptEl:
        transcript = etree.tostring(transcriptEl[0]).decode()
        text_list = etree.HTML(transcript).xpath("//li/div/p/text()")

    if summaryEl:
        summary = summaryEl[0]
    else:
        summary = text_list[0] if text_list else ""

    if summary and transcript:
        sql = "UPDATE `news` SET `summary`=%s,`transcript`=%s WHERE `title`=%s"
        return exec_sql(sql, (summary, transcript, title))
    return "No Transcript"


def push_news_by_date(article):
    article_id, title, transcript, image_url, date, *_ = article
    # 05-12-2020
    f_date = date.strftime("%d-%m-%Y")
    tip_text = "Here comes the transcript ⬆️"
    return send_message(
        m_type="text" if transcript else "link",
        id=article_id,
        title=f"{f_date}",
        content=tip_text if transcript else title,
        picUrl=f"image/{image_url}",
    )


def crawl_by_date(date):
    try:
        date = datetime.strptime(date, "%Y-%m-%d") if type(date) == str else date
        s_date = date.strftime("%Y-%m-%d")
        print(f"[{s_date}]:Start Crawl...")
        result = parse_transcript_audio(date)
        print(f"Crawl Result: {result}")
        if result == "Ok":
            q_sql = f"SELECT `id`,`title`,`transcript`,`image_url`,`date`,`source`,`summary` FROM `news` WHERE `date`=%s"
            articles = query_size(q_sql, date)
            if articles:
                (article,) = articles
                r_dict = push_news_by_date(article)
                print(f"Push Result: {r_dict.get('errmsg')}")
                (_, _, transcript, *_) = article
                if transcript:
                    # upload weixin official account
                    asset_name = f"pbs_newswrap_{date.strftime('%Y%m%d')}.jpg"
                    asset_path = f"{os.getcwd()}/static/image/{asset_name}"
                    _, wx_message = add_material(article, asset_path)
                    print(f"Add WX Materal: {wx_message}")
                    # publish ghost
                    g_msg = publish_blog(article)
                    print(f"publish ghost:", g_msg)
            else:
                print("No Articles!")
    except Exception as e:
        print(f"Final Error: {e}")


if __name__ == "__main__":
    today = datetime.now(tz).date()
    crawl_by_date(today)