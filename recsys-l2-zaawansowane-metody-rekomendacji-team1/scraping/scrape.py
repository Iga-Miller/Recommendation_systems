from urllib.request import urlopen 
from bs4 import BeautifulSoup 
from PIL import Image
from pathlib import Path
from tqdm import tqdm
import contextlib
import re
import requests
import io
import time
import warnings
import json
import random


sub_pattern = r"\.\d+x\d+\." # pattern for finding resolution in image 
save_path = Path("steam_pics/") # path to save images


def get_and_store_image(src, dest):
    # make target dir
    dest.parent.mkdir(parents=True, exist_ok=True)
    # get img from src url
    image_content = requests.get(src).content
    try:
        # read img
        image_file = io.BytesIO(image_content)
        # open as img with PIL
        image = Image.open(image_file).convert("RGB")
    except:
        warnings.warn(f"Cannot read image {src}: {image_content}")
        # return false so we know that this img wasn't saved
        return False
    # save to disk
    image.save(dest)
    # return true so we know everything went ok
    return True


def main():
    # load the set of items with both player and review
    with open('items_with_players_and_reviews.txt', 'r') as fp:
        items_with_players_and_reviews = set(line.strip() for line in fp.readlines())
    # load dict mapping game_id -> url
    with open('games_urls.json', 'r') as fp:
        games_urls = json.load(fp)
    # read what we have already stored and skip those ids
    ids_to_skip = set(map(lambda x: x.stem, save_path.iterdir()))
    # scrape steam
    for game_id in tqdm(sorted(items_with_players_and_reviews.difference(ids_to_skip))):
        # get game url
        game_url = games_urls[game_id]
        # open game url (steam game page)
        with contextlib.closing(urlopen(game_url)) as htmldata:
            # make soup
            soup = BeautifulSoup(htmldata, 'lxml')
        # find all objects pointing on game's .jpg files
        header_url = None
        imgs_urls = list()
        all_urls = soup.find_all("img", src = re.compile(rf'.*steam/apps/{game_id}.*\.jpg.*'))
        if len(all_urls) == 0:
            continue
        for img_url in all_urls:
            img_cls = img_url.attrs.get('class')
            # get url
            src = img_url.attrs.get('src')
            # substitute img resolution in url, so we get nice, big picture
            src = re.sub(sub_pattern, ".", src)
            # check if header img
            if img_cls is not None and "game_header_image_full" in img_cls:
                header_url = src
            elif "header" in src: continue # omit header img
            else:
                imgs_urls.append(src)
        random.shuffle(imgs_urls)
        get_and_store_image(header_url, save_path / game_id / f"{game_id}_header.jpg")
        # save non-header img
        nonheader_img_count = 0
        for src in imgs_urls:
            if nonheader_img_count >= 5:
                break
            elif get_and_store_image(src, save_path / game_id / f"{game_id}_{nonheader_img_count}.jpg"):
                nonheader_img_count += 1
            # sleep for 0.2s between imgs
            time.sleep(0.5)
        time.sleep(5)


if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print("An error occured: ", exc)
            print("Retrying in 90 seconds.")
            time.sleep(90)
            continue
