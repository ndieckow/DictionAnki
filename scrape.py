from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, element

DEBUG = False

# ===== Dictionary Links =====
MERRIAM_WEBSTER = 'https://www.merriam-webster.com/dictionary/'
CAMBRIDGE = 'https://dictionary.cambridge.org/dictionary/english/'
DICT_CC = 'https://en-de.dict.cc/?s='
# ============================

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

def trim_numbers(string):
    for i,ch in enumerate(string):
        if not ch.isnumeric():
            return string[i:]
    return string

async def scrape_merriam_webster(search_string: str):
    search_string = search_string.replace(' ', '+')

    if search_string.startswith('to+'):
        search_string = search_string[3:]

    url = MERRIAM_WEBSTER + search_string
    html = urlopen(url).read().decode('utf-8') if not DEBUG else open('test_merriam.txt').read()
    soup = BeautifulSoup(html)
    entries = soup.find_all("div", id=lambda v: v and v.startswith("dictionary-entry-"))
    
    ret = []

    for entry in entries:
        # 1. Extract part-of-speech
        contents = entry.find(class_="parts-of-speech").contents
        assert len(contents) == 1
        pos = contents[0]
        if type(pos) == element.Tag:
            pos = pos.contents[0]

        # 2. Extract list of meanings
        meanings = entry.find_all("span", class_="dtText")
        meanings = [x.text[2:] for x in meanings]
        ret.append((pos, meanings))
    return ret

async def scrape_dict_cc(search_string: str):
    search_string = search_string.replace(' ', '+')

    url = DICT_CC + search_string
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0')
    html = urlopen(req).read().decode('utf-8') if not DEBUG else open('test_dict_cc.txt').read()
    soup = BeautifulSoup(html)
    entries = soup.find_all("tr", id=lambda v: v and v.startswith("tr"))

    ret = []

    for entry in entries:
        words = entry.find_all("td", class_=lambda v: v and v.endswith("nl"))
        assert len(words) == 2
        words = [words[0].text, trim_numbers(words[1].text)]
        eng, ger = [x.strip().replace(u'\xa0', u' ') for x in words]
        ret.append((eng, ger))
    
    return ret