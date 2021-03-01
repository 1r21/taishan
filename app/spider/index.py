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
from app.weixin.index import upload_material, add_material

tz = pytz.timezone("America/New_York")

base_url = "https://www.pbs.org/newshour/latest/page/3"

# set retries number
requests.adapters.DEFAULT_RETRIES = 15
s = requests.session()
# close useless connect
s.keep_alive = False


def fetch_content(url, type="text"):
    try:
        r = requests.get(url, proxies=PROXY if type != "text" else None, timeout=60)
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
        print("Save Err: ", e)

    return asset_name


def parse_list(url=base_url, date=""):
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
            image_url = save_assets(image_from, date, file_type="image")

            news_wrap["title"] = title
            news_wrap["source"] = article_from
            news_wrap["image_url"] = image_url
            news_wrap["image_from"] = image_from
            break
    return news_wrap


def parse_transcript_audio():
    # check database
    today = datetime.datetime.now(tz).date()
    news_wrap = parse_list(date=today)
    title = news_wrap.get("title")
    err_msg = "News is still on the way!"

    if not news_wrap:
        return err_msg

    sql = f"SELECT `transcript` FROM `news` WHERE `title`=%s"
    articles = query_size(sql, title)
    if articles:
        (article,) = articles
        (transcript,) = article

        if transcript:
            return "News Exists"
        else:
            return parse_transcript(title)
    else:
        source = news_wrap.get("source")
        article_html = etree.HTML(fetch_content(source))
        audioEl = article_html.xpath("//audio/source/@src")

        audio_from = ""
        audio_url = ""

        if audioEl:
            (audio_from,) = audioEl
            audio_url = save_assets(audio_from, today)

        sql = "INSERT INTO `news` \
            (`title`,`audio_url`,`image_url`,`source`,`audio_from`,`image_from`,`date`) \
            VALUES (%s,%s,%s,%s,%s,%s,%s)"
        values = (
            title,
            audio_url,
            news_wrap.get("image_url"),
            source,
            audio_from,
            news_wrap.get("image_from"),
            today,
        )
        return exec_sql(sql, values)


def parse_transcript(title):
    q_sql = f"SELECT `source` FROM `news` WHERE `title`=%s"
    articles = query_size(q_sql, title)
    if not articles:
        return "No Article"

    (article,) = articles
    (source,) = article
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


def push_news_by_date(date):
    q_sql = f"SELECT `id`,`title`,`summary`,`image_url` FROM `news` WHERE `date`=%s"
    articles = query_size(q_sql, date)
    err_msg = {"errmsg": "Push Fail!"}
    if articles:
        (article,) = articles
        article_id, title, summary, image_url = article
        # 05-12-2020
        f_date = date.strftime("%d-%m-%Y")
        tip_text = "Here comes the transcript ⬆️"
        err_msg = send_message(
            m_type="text" if summary else "link",
            id=article_id,
            title=f"{f_date}",
            content=tip_text if summary else title,
            picUrl=f"image/{image_url}",
        )
    return err_msg, bool(summary)


if __name__ == "__main__":
    try:
        print("Start Crawl...")
        result = parse_transcript_audio()
        print(f"Crawl Result: {result}")
        if result == "Ok":
            today = datetime.datetime.now(tz).date()
            r_dict, has_transcript = push_news_by_date(today)
            print(f"Push Result: {r_dict.get('errmsg')}")
            if has_transcript:
                asset_name = f"pbs_newswrap_{today.strftime('%Y%m%d')}.jpg"
                asset_path = f"{os.getcwd()}/static/image/{asset_name}"
                wx_dict = add_material(today, asset_path)
                print(f"Add WX Materal: {wx_dict.get('media_id')}")
    except Exception as e:
        print(f"Final Error: {e}")
