import os
import logging
from datetime import datetime
from pathlib import Path
from os import environ as env

import pytz
import requests
from lxml import etree

from app.core.article import Article
from app.libs.db import db_helper
from app.libs.util import head
from app.sdk.weixin import Weixin
from app.sdk.dingding import Bot
from app.sdk.qiniu import Qiniu
from app.sdk.ghost import Ghost
from app.setting import WEB_APP_URL, FILE_SERVER_URL

tz = pytz.timezone("America/New_York")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# set retries number
requests.adapters.DEFAULT_RETRIES = 15
s = requests.session()
# close useless connect
s.keep_alive = False
s.headers.update({"cache-control": "no-cache"})

TARGET_URL = env.get("TARGET_URL") or "https://www.pbs.org/newshour/latest"
HTTP_PROXY = env.get("HTTP_PROXY")
HTTPS_PROXY = env.get("HTTPS_PROXY")


class PBSArticle(Article):
    def __init__(self, **kw) -> None:
        Article.__init__(self, **kw)
        self.date = self.format_date(self.date)

    def run(self):
        self.__get_latest_article(TARGET_URL)
        if not self.title:
            return "News is still on the way!"

        article = self.__has_base_article()

        if article:
            transcript = head(article)
            return "News Exists" if transcript else self.__get_transcript()

        image_url = self.save_assets(self.image_from, self.date, file_type="image")
        audio_from, audio_url = self.__get_audio()
        self.image_url = image_url
        self.audio_url = audio_url

        insert_article = (
            "INSERT INTO news (title, audio_url, image_url, source, audio_from, image_from, date) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        values = (
            self.title,
            audio_url,
            image_url,
            self.source,
            audio_from,
            self.image_from,
            self.date,
        )
        article_id = db_helper.execute_commit(insert_article, values)
        self.id = article_id
        return self.title

    def __get_latest_article(self, url):
        article_list_rule = '//div[@class="latest__wrapper"]/article/div[@class="card-timeline__col-right"]'
        article_rule = '//a[@class="card-timeline__title"]'
        title_rule = '//a[@class="card-timeline__title"]/span'
        image_rule = '//a[@class="card-timeline__img-link"]/img'
        find_sections = etree.HTML(PBSArticle.fetch(url)).xpath(article_list_rule)
        for item in find_sections:
            html = etree.HTML(etree.tostring(item).decode())
            find_titles = html.xpath(title_rule)
            title = head(find_titles).text.replace("\n", "").strip()
            if title and title.lower().find("news wrap") != -1:
                find_articles = html.xpath(article_rule)
                find_images = html.xpath(image_rule)
                article_from = head(find_articles).get("href")
                image_from = head(find_images).get("src")
                self.title = title
                self.source = article_from
                self.image_from = image_from
                break

    def __get_audio(self):
        root = etree.HTML(PBSArticle.fetch(self.source))
        find_audios = root.xpath("//audio/source/@src")
        if find_audios:
            audio_from = head(find_audios)
            self.audio_from = audio_from
            return audio_from, self.save_assets(audio_from, self.date)

    def __get_transcript(self):
        root = etree.HTML(PBSArticle.fetch(self.source))
        transcript_rule = '//div[@id="transcript"]/ul[@class="video-transcript"]'
        summary_rule = (
            '//div[@id="transcript"]/div[@class="vt__excerpt body-text"]/p/text()'
        )
        find_transcripts = root.xpath(transcript_rule)
        find_summarys = root.xpath(summary_rule)

        transcript = None
        text_list = []

        if find_transcripts:
            transcript = etree.tostring(head(find_transcripts)).decode()
            text_list = etree.HTML(transcript).xpath("//li/div/p/text()")

        summary = head(find_summarys or text_list)

        if summary and transcript:
            sql = "UPDATE news SET summary = %s, transcript = %s WHERE title = %s"
            db_helper.execute_commit(sql, (summary, transcript, self.title))
            return "Fetch Transcript Success"
        return "No Transcript"

    # it had audio,but transcript may be not
    def __has_base_article(self):
        query = "SELECT transcript FROM news WHERE title = %s"
        return db_helper.fetchone(query, self.title)

    @staticmethod
    def save_assets(url, date, file_type="audio"):
        asset_path, asset_name = PBSArticle.get_asset_path(date, file_type)
        if not Path(asset_path).exists():
            with open(asset_path, "wb") as f:
                f.write(PBSArticle.fetch(url, "byte"))
                f.close()

        try:
            # save qiniu
            qiniu = Qiniu(f"{file_type}/{asset_name}", asset_path)
            qiniu.save()

            # save weixin
            if file_type == "audio":
                dstFile = PBSArticle.rename_filename(date, asset_path, file_type)
                wx = Weixin()
                wx.upload_material(dstFile, "voice")
        except Exception as e:
            print("Save Assets Err: ", e)

        return asset_name

    @staticmethod
    def rename_filename(date, asset_path, file_type):
        new_filename = f"{date.strftime('%d-%m-%Y')}.mp3"
        dstFile = PBSArticle.resolve_path(new_filename, file_type)
        os.rename(asset_path, dstFile)
        return dstFile

    @staticmethod
    def get_asset_path(date, file_type):
        asset_name = PBSArticle.get_asset_name(date, file_type)
        asset_path = PBSArticle.resolve_path(asset_name, file_type)
        return asset_path, asset_name

    @staticmethod
    def get_asset_name(date, file_type):
        ext_name = "mp3" if file_type == "audio" else "jpg"
        return f"pbs_newswrap_{date.strftime('%Y%m%d')}.{ext_name}"

    @staticmethod
    def resolve_path(name, file_type):
        cur_dir = os.getcwd()
        return os.path.join(cur_dir, f"static/{file_type}", f"{name}")

    @staticmethod
    def fetch(url, type="text"):
        try:
            PROXY = None
            if HTTP_PROXY and HTTPS_PROXY:
                PROXY = {"http": HTTPS_PROXY, "https": HTTPS_PROXY}
            proxies = PROXY if type != "text" else None
            data = requests.get(url, proxies=proxies, timeout=60)
            return data.text if type == "text" else data.content
        except Exception as e:
            raise Exception(f"Fetch Fail: {e}")

    @staticmethod
    def format_date(date):
        if type(date) == str:
            return datetime.strptime(date, "%Y-%m-%d")
        return date


class Automation(PBSArticle):
    def __init__(self, date) -> None:
        PBSArticle.__init__(self, date=date)

    def start(self):
        s_date = self.date.strftime("%Y-%m-%d")
        logger.info(f"[{s_date}]:Start Crawl...")
        result = self.run()
        logger.info(f"Crawl Result: {result}")
        if self.id:
            r_dict = self.send()
            logger.info(f"Push Result : {r_dict.get('errmsg')}")
            if self.transcript:
                # upload weixin official account
                asset_path = self.get_asset_path(self.date, "image")
                wx = Weixin()
                wx_message = wx.add_material(asset_path, **self.__compose_article())
                logger.info(f"Add WX Materal : {wx_message}")
                # publish ghost
                blog = Ghost()
                g_message = blog.publish(**self.__compose_article())
                logger.info(f"publish ghost : {g_message}")
        else:
            print("No Articles!")

    def send(self):
        # 05-12-2020
        f_date = self.date.strftime("%d-%m-%Y")
        tip_text = "Here comes the transcript ⬆️"
        msg_type = "link"
        content = self.title
        if self.transcript:
            msg_type = "text"
            content = tip_text
        bot = Bot()
        pic_url = f"{FILE_SERVER_URL}/image/{self.image_url}"
        msg_url = f"{WEB_APP_URL}/detail/{self.id}" if id else WEB_APP_URL
        template = Bot.get_template(
            msg_type, title=f_date, content=content, pic_url=pic_url, msg_url=msg_url
        )
        return bot.send(template)

    def __compose_article(self):
        return dict(
            article_id=self.id,
            title=self.title,
            transcript=self.transcript,
            image_url=self.image_url,
            date=self.date,
            source=self.source,
            summary=self.summary,
        )

today = datetime.now(tz).date()
automation = Automation(today)
if __name__ == "__main__":
    # automation = Automation(today)
    automation.start()
