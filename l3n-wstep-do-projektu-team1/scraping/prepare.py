import json
import pickle
from tqdm import tqdm

# non_character_re = re.compile(r"[^\w\s]")
# newline_re = re.compile("\n")
# multi_whitespace_re = re.compile(r"\s+")

# def strip_html(s):
#     return str(html.fromstring(s).text_content())

# def parse_description(description):
#     ret_desc = list()
#     for sent in description:
#         if sent != '':
#             try:
#                 stripped_line = strip_html(sent).strip()
#                 decoded_line = unicodedata.normalize('NFKC', stripped_line)
#                 ret_desc.append(decoded_line)
#             except ParserError:
#                 continue
#     if (concat_desc := " ".join(ret_desc)) and ret_desc:
#         concat_desc = non_character_re.sub(' ', concat_desc)
#         concat_desc = newline_re.sub(" \n ", concat_desc)
#         concat_desc = multi_whitespace_re.sub(" ", concat_desc)
#         return concat_desc.strip()
#     return None

# def parse_title(title):
#     if not title:
#         return None
#     title = non_character_re.sub(' ', title)
#     title = newline_re.sub(" \n ", title)
#     title = multi_whitespace_re.sub(" ", title)
#     if title == '':
#         return None
#     try:
#         title = strip_html(title).strip()
#         title = unicodedata.normalize('NFKC', title)
#     except ParserError:
#         return None
#     return title.strip()

wanted_category = "cardigan"

if __name__ == "__main__":
    items_dict = dict()

    with open("Clothing_Shoes_and_Jewelry_5.json", 'r') as fp:
        for line in tqdm(fp.readlines()):
            data_line = json.loads(line)
            items_dict.setdefault(data_line['asin'], list())
            items_dict[data_line['asin']].append(data_line)

    products_metadata = dict()
    with open("meta_Clothing_Shoes_and_Jewelry.json", 'r') as fp:
        for line in tqdm(fp.readlines()):
            meta_line = json.loads(line)
            if meta_line['asin'] in items_dict and meta_line.get('description'):
                products_metadata.setdefault(meta_line['asin'], meta_line)
    
    items_to_scrape = dict()
    for item_id, item_dict in tqdm(products_metadata.items()):
        if wanted_category in map(str.lower, item_dict['category']):
            if urls_list := item_dict.get('imageURLHighRes'):
                items_to_scrape.setdefault(item_id, urls_list)

    with open("items_urls_to_scrape.pkl", 'wb') as fp:
        pickle.dump(items_to_scrape, fp)
