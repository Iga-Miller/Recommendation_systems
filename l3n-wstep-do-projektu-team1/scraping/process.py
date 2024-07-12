import json
import unicodedata
import re
from lxml import html
from lxml.etree import ParserError
from tqdm import tqdm

non_character_re = re.compile(r"[^\w\s]")
newline_re = re.compile("\n")
multi_whitespace_re = re.compile(r"\s+")

def strip_html(s):
    return str(html.fromstring(s).text_content())

def parse_description(description):
    ret_desc = list()
    # parse descriptions
    for sent in description:
        if sent != '':
            try:
                stripped_line = strip_html(sent).strip()
                decoded_line = unicodedata.normalize('NFKC', stripped_line)
                ret_desc.append(decoded_line)
            except ParserError:
                continue
    # join lines of description and substitute unwanted characters
    if (concat_desc := " ".join(ret_desc)) and ret_desc:
        concat_desc = non_character_re.sub(' ', concat_desc)
        concat_desc = newline_re.sub(" \n ", concat_desc)
        concat_desc = multi_whitespace_re.sub(" ", concat_desc)
        return concat_desc.strip()
    return None

def parse_title(title):
    if not title:
        return None
    title = non_character_re.sub(' ', title)
    title = newline_re.sub(" \n ", title)
    title = multi_whitespace_re.sub(" ", title)
    if title == '':
        return None
    try:
        title = strip_html(title).strip()
        title = unicodedata.normalize('NFKC', title)
    except ParserError:
        return None
    return title.strip()


if __name__ == "__main__":
    # load k-core dataset
    items_dict = dict()
    with open("Clothing_Shoes_and_Jewelry_5.json", 'r') as fp:
        for i, line in enumerate(tqdm(fp.readlines())):
            data_line = json.loads(line)
            items_dict.setdefault(data_line['asin'], list())
            items_dict[data_line['asin']].append(data_line)
    # load descriptions and titles
    descriptions_dict = dict()
    titles_dict = dict()
    with open("meta_Clothing_Shoes_and_Jewelry.json", 'r') as fp:
        for i, line in enumerate(tqdm(fp.readlines())):
            meta_line = json.loads(line)
            # see if item in k-core and description present
            if meta_line['asin'] in items_dict and meta_line.get('description'):
                description = parse_description(meta_line['description'])
                title = parse_title(meta_line.get('title'))
                if description:
                    descriptions_dict.setdefault(meta_line['asin'], description)
                if title:
                    titles_dict.setdefault(meta_line['asin'], title)
    print(len(items_dict))
    print(len(descriptions_dict))
    print(len(titles_dict))