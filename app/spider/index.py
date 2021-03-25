import os
from datetime import datetime
from pathlib import Path

import pytz
import requests
from lxml import etree

from app.setting import PROXY, TARGET_URL
from app.libs.helper import exec_sql, query_size, head
from app.robot.index import send_message
from app.qiniu.index import save_file_2_qiniu
from app.weixin.index import upload_material, add_material
from app.ghost.index import Blog

tz = pytz.timezone("America/New_York")

# set retries number
requests.adapters.DEFAULT_RETRIES = 15
s = requests.session()
# close useless connect
s.keep_alive = False
s.headers.update({"cache-control": "no-cache"})


class Spider:
    def __init__(self, date) -> None:
        self.date = self.__format_date(date)
        self.title = ""
        self.source = ""
        self.image_from = ""

    def run(self):
        self.__get_latest_article(TARGET_URL)
        if not self.title:
            return "News is still on the way!"

        article = self.__has_base_article()

        if article:
            transcript = self.__head(article)
            return "News Exists" if transcript else self.__get_transcript()

        image_url = self.save_assets(self.image_from, self.date, file_type="image")
        audio_from, audio_url = self.__get_audio()

        insert_article = (
            "INSERT INTO news (title, audio_url, image_url, source, audio_from, image_from, date)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        return exec_sql(
            insert_article,
            (
                self.title,
                audio_url,
                image_url,
                self.source,
                audio_from,
                self.image_from,
                self.date,
            ),
        )

    def __get_latest_article(self, url):
        article_list_rule = '//div[@class="latest__wrapper"]/article/div[@class="card-timeline__col-right"]'
        article_rule = '//a[@class="card-timeline__title"]'
        title_rule = '//a[@class="card-timeline__title"]/span'
        image_rule = '//a[@class="card-timeline__img-link"]/img'
        find_sections = etree.HTML(self.fetch(url)).xpath(article_list_rule)
        for item in find_sections:
            html = etree.HTML(etree.tostring(item).decode())
            find_titles = html.xpath(title_rule)
            title = self.__head(find_titles).text.replace("\n", "").strip()
            if title and title.lower().find("news wrap") != -1:
                find_articles = html.xpath(article_rule)
                find_images = html.xpath(image_rule)
                article_from = self.__head(find_articles).get("href")
                image_from = self.__head(find_images).get("src")
                self.title = title
                self.source = article_from
                self.image_from = image_from
                break

    def __get_audio(self):
        root = etree.HTML(self.fetch(self.source))
        find_audios = root.xpath("//audio/source/@src")
        if find_audios:
            audio_from = self.__head(find_audios)
            return audio_from, self.save_assets(audio_from, self.date)

    def __get_transcript(self):
        root = etree.HTML(self.fetch(self.source))
        transcript_rule = '//div[@id="transcript"]/ul[@class="video-transcript"]'
        summary_rule = (
            '//div[@id="transcript"]/div[@class="vt__excerpt body-text"]/p/text()'
        )
        find_transcripts = root.xpath(transcript_rule)
        find_summarys = root.xpath(summary_rule)

        transcript = None
        text_list = []

        if find_transcripts:
            transcript = etree.tostring(self.__head(find_transcripts)).decode()
            text_list = etree.HTML(transcript).xpath("//li/div/p/text()")

        summary = self.__head(find_summarys or text_list)

        if summary and transcript:
            sql = "UPDATE news SET summary = %s,transcript = %s WHERE title = %s"
            return exec_sql(sql, (summary, transcript, self.title))
        return "No Transcript"

    # it had audio,but transcript may be not
    def __has_base_article(self):
        query = "SELECT transcript, source, title FROM news WHERE title = %s"
        articles = query_size(query, self.title)
        return self.__head(articles)

    def fetch(url, type="text"):
        try:
            proxies = PROXY if type != "text" else None
            r = requests.get(url, proxies=proxies, timeout=60)
            return r.text if type == "text" else r.content
        except Exception as e:
            raise Exception(f"Fetch Fail: {e}")

    def save_assets(self, url, date, file_type="audio"):
        cur_dir = os.getcwd()
        ext_name = "mp3" if file_type == "audio" else "jpg"
        asset_name = f"pbs_newswrap_{date.strftime('%Y%m%d')}.{ext_name}"
        asset_path = os.path.join(cur_dir, f"static/{file_type}", f"{asset_name}")

        if not Path(asset_path).exists():
            f = open(asset_path, "wb")
            f.write(self.fetch_content(url, "byte"))
            f.close()

        try:
            # save qiniu
            save_file_2_qiniu(asset_path, f"{file_type}/{asset_name}")

            # save weixin
            if file_type == "audio":
                new_filename = f"{date.strftime('%d-%m-%Y')}.{ext_name}"
                dstFile = os.path.join(
                    cur_dir, f"static/{file_type}", f"{new_filename}"
                )
                os.rename(asset_path, dstFile)
                upload_material(dstFile, "voice")
        except Exception as e:
            print("Save Assets Err: ", e)

        return asset_name

    def __head(self, list):
        return head(list)

    def __format_date(self, date):
        if type(date) == str:
            return datetime.strptime(date, "%Y-%m-%d")
        return date

class Platfform:
    pass

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
        spider = Spider(today)
        s_date = spider.date.strftime("%Y-%m-%d")
        print(f"[{s_date}]:Start Crawl...")
        result = spider.run()
        print(f"Crawl Result: {result}")
        if result == "Ok":
            query = (
                "SELECT id, title, transcript, image_url, date, source, summary FROM news"
                "WHERE date = %s"
            )
            articles = query_size(query, date)
            article = head(articles)
            if article:
                r_dict = push_news_by_date(article)
                print(f"Push Result: {r_dict.get('errmsg')}")
                if article[2]:
                    # upload weixin official account
                    asset_name = f"pbs_newswrap_{date.strftime('%Y%m%d')}.jpg"
                    asset_path = f"{os.getcwd()}/static/image/{asset_name}"
                    _, wx_message = add_material(article, asset_path)
                    print(f"Add WX Materal: {wx_message}")
                    # publish ghost
                    blog = Blog(article)
                    g_msg = blog.publish()
                    print(f"publish ghost:", g_msg)
            else:
                print("No Articles!")
    except Exception as e:
        print(f"Final Error: {e}")


if __name__ == "__main__":
    today = datetime.now(tz).date()
    crawl_by_date(today)