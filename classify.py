from pathlib import Path
import shutil

# 创建文件夹
Path("wallpapers/4k").mkdir(parents=True, exist_ok=True)
Path("wallpapers/2k").mkdir(parents=True, exist_ok=True)
Path("wallpapers/1k").mkdir(parents=True, exist_ok=True)


# 归类图片
folder = Path("images")
for f in folder.rglob("*"):
    if f.is_file():
        if f.name.endswith("4k.jpg"):
            shutil.copyfile(f, Path("wallpapers/4k") / f.name)
        if f.name.endswith("2k.jpg"):
            shutil.copyfile(f, Path("wallpapers/2k") / f.name)
        if f.name.endswith("1k.jpg"):
            shutil.copyfile(f, Path("wallpapers/1k") / f.name)
