from PIL import Image
from pathlib import Path
from tqdm import tqdm
import requests
import io
import time
import warnings
import pickle
import random


save_path = Path(__file__).parent.parent / "cardigan_pics" # path to save images
items_urls_path = "items_urls_to_scrape.pkl"
max_imgs = float('inf') # max number of images for each item. Best to set it to 1 or 2 
shuffle_urls_lists = True # if true shuffle the list of urls before retrieving images
long_wait_period = 20 # every long_wait_period of items the algorithm will wait for longer before resuming donwload
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}


def get_and_store_image(src, dest):
    # make target dir
    dest.parent.mkdir(parents=True, exist_ok=True)
    # get img from src url
    image_content = requests.get(src, headers=headers).content
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
    # create directory if it does not exist
    if not save_path.exists():
        save_path.mkdir()
    # load dict with urls to scrape
    with open(items_urls_path, "rb") as fp:
        items_urls_to_scrape = pickle.load(fp)
    # read what we have already stored and skip those ids
    ids_to_skip = set()
    # see how many items left to scrape
    for item_dir_path in tqdm(save_path.iterdir()):
        num_pics = len(list(item_dir_path.iterdir()))
        if num_pics >= max_imgs or num_pics >= len(items_urls_to_scrape.get(item_dir_path.stem, [])):
            ids_to_skip.add(item_dir_path.stem)
    for i, item_id in enumerate(tqdm(sorted(set(items_urls_to_scrape.keys()).difference(ids_to_skip))), 1):
        if i % long_wait_period == 0:
            # sleep for 4 seconds every count_long_wait items
            time.sleep(4)
        # get game url
        imgs_urls = items_urls_to_scrape[item_id]
        # open game url (steam game page)
        if shuffle_urls_lists:
            random.shuffle(imgs_urls)
        # count how many items successfully scraped
        src_count = 0
        for src in imgs_urls:
            # if successful
            if get_and_store_image(src, save_path / item_id / f"{item_id}_{src_count}.jpg"):
                src_count += 1
            # if we have all images we want for 1 item
            if src_count >= max_imgs:
                break
            # sleep for 0.2s between imgs
            time.sleep(0.2)
        # sleep for 0.5s between items
        time.sleep(0.5)


if __name__ == "__main__":
    while True:
        try:
            main()
            break
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print("An error occured: ", exc)
            print("Retrying in 90 seconds.")
            time.sleep(90)
            continue