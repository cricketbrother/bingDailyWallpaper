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


def get_image_info(n=0) -> Image:
    """
    获取图片的信息, 默认为最新

    参数:
        n: int 0为最新, 1为前一天, 2为前两天, 以此类推, 最大值为6

    返回: Image
    """
    resp = requests.get(
        url="https://cn.bing.com/hp/api/model",
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        },
    )

    if resp.status_code == 200 and resp.json().get("MediaContents"):
        last_media = resp.json().get("MediaContents")[max(0, min(6, n))]
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


def save_image_info(image: Image, json_filepath: str) -> None:
    """
    保存图片信息

    参数:
        image: Image
        dst: str
    返回: None
    """
    os.makedirs(os.path.dirname(json_filepath), exist_ok=True)
    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(image.json(), f, indent=2, ensure_ascii=False)


def add_image_info(image: Image, json_filepath: str) -> None:
    """
    追加保存图片信息

    参数:
        image: Image
        dst: str
    返回: None
    """
    if os.path.exists(json_filepath):
        with open(json_filepath, "r", encoding="utf-8") as f:
            tmp = json.load(f)
    else:
        os.makedirs(os.path.dirname(json_filepath), exist_ok=True)
        tmp = []

    tmp = [image.json()] + tmp

    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(tmp, f, indent=2, ensure_ascii=False)


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


def save_markdown(image: Image, md_filepath: str) -> None:
    """
    保存markdown

    参数:
        image: Image
        md_filepath: str
    返回: None
    """
    os.makedirs(os.path.dirname(md_filepath), exist_ok=True)
    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write(
            f"# {image.Headline}\n\n"
            f"{image.Date}\n\n"
            f'![]({image.UrlBase} "{image.Copyright}")\n\n'
            f"{image.Title}\n\n"
            f"{image.Description}\n\n"
            f"{image.MainText}\n\n"
        )


if __name__ == "__main__":
    image = get_image_info(n=0)
    base_dir = os.path.join("images", image.Year, image.Month, image.Day)

    # 保存当日图片信息
    save_image_info(
        image,
        os.path.join(
            "images",
            image.Year,
            image.Month,
            image.Day,
            f"{image.Year}-{image.Month}-{image.Day}.json",
        ),
    )
    # 保存当日4K图片
    url4k = image.UrlBase + "&w=3840&h=2160"
    save_image(url4k, os.path.join(base_dir, image.Date + "_4k.jpg"))
    # 保存当日2K图片
    url2k = image.UrlBase + "&w=2560&h=1440"
    save_image(url2k, os.path.join(base_dir, image.Date + "_2k.jpg"))
    # 保存当日1K图片
    url1k = image.UrlBase + "&w=1920&h=1080"
    save_image(url1k, os.path.join(base_dir, image.Date + "_1k.jpg"))
    # 保存当日readme
    save_markdown(image, os.path.join(base_dir, "README.md"))

    # 保存readme
    save_markdown(image, "./README.md")

    # 追加保存当月图片信息
    add_image_info(
        image,
        os.path.join(
            "images", image.Year, image.Month, f"{image.Year}-{image.Month}.json"
        ),
    )

    # 追加保存当年图片信息
    add_image_info(
        image,
        os.path.join("images", image.Year, f"{image.Year}.json"),
    )
