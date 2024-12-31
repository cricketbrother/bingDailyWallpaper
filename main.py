from datetime import datetime
import json
import os
import requests


# 图片信息类，4k: &w=3840&h=2160, 2k: &w=2560&h=1440, 1k: &w=1920&h=1080
class Image:
    def __init__(self) -> None:
        self.Date = ""
        self.Year = ""
        self.Month = ""
        self.Day = ""
        self.Description = ""
        self.Headline = ""
        self.Title = ""
        self.Copyright = ""
        self.MainText = ""
        self.UrlBase = ""

    def json(self) -> dict:
        return {
            "Date": self.Date,
            "Year": self.Year,
            "Month": self.Month,
            "Day": self.Day,
            "Description": self.Description,
            "Headline": self.Headline,
            "Title": self.Title,
            "Copyright": self.Copyright,
            "MainText": self.MainText,
            "UrlBase": self.UrlBase,
        }


def get_last_image_info() -> Image:
    """
    获取上一张图片的信息

    返回: Image
    """
    resp = requests.get(
        url="https://cn.bing.com/hp/api/model",
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        },
    )
    if resp.status_code == 200 and resp.json().get("MediaContents"):
        last_media = resp.json().get("MediaContents")[0]
        image = Image()
        date = datetime.strptime(last_media["FullDateString"], "%Y %m月 %d")
        image.Date = date.strftime("%Y-%m-%d")
        image.Year = date.strftime("%Y")
        image.Month = date.strftime("%m")
        image.Day = date.strftime("%d")
        image.Description = last_media["ImageContent"]["Description"]
        image.Headline = last_media["ImageContent"]["Headline"]
        image.Title = last_media["ImageContent"]["Title"]
        image.Copyright = last_media["ImageContent"]["Copyright"]
        image.MainText = last_media["ImageContent"]["QuickFact"]["MainText"]
        image.UrlBase = "https://cn.bing.com" + last_media["ImageContent"]["Image"][
            "Wallpaper"
        ].replace("_1920x1200.jpg&rf=LaDigue_1920x1200.jpg", "_UHD.jpg")
        return image
    else:
        return None


def save_image_info(image: Image, dst: str) -> None:
    """
    保存图片信息

    参数:
        image: Image
        dst: str
    返回: None
    """
    os.makedirs(dst, exist_ok=True)
    json_filepath = os.path.join(dst, image.Date + ".json")
    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(image.json(), f, indent=2, ensure_ascii=False)


def save_image(url: str, image_filepath: str) -> None:
    """
    保存图片

    参数:
        url: str
        image_filepath: str
    返回: None
    """
    resp = requests.get(
        url,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        },
    )
    if resp.status_code == 200 and resp.content:
        os.makedirs(os.path.dirname(image_filepath), exist_ok=True)
        with open(image_filepath, "wb") as f:
            f.write(resp.content)


if __name__ == "__main__":
    image = get_last_image_info()
    base_dir = os.path.join("images", image.Year, image.Month)
    # 保存图片信息
    save_image_info(image, base_dir)
    # 保存4K图片
    url4k = image.UrlBase + "&w=3840&h=2160"
    save_image(url4k, os.path.join(base_dir, image.Date + "_4k.jpg"))
    # 保存2K图片
    url2k = image.UrlBase + "&w=2560&h=1440"
    save_image(url2k, os.path.join(base_dir, image.Date + "_2k.jpg"))
    # 保存1K图片
    url1k = image.UrlBase + "&w=1920&h=1080"
    save_image(url1k, os.path.join(base_dir, image.Date + "_1k.jpg"))
