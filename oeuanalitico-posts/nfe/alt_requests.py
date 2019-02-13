from lxml import html
from lxml.cssselect import CSSSelector
from requests import get
from requests import Session
import re
from time import sleep

# identificação da chave da nfe
pattern = re.compile(r'=[0-9]{44}&')

with open("./data/url_list.csv", "r") as f:
    urls = f.readlines()


BASE_URL = "http://dec.fazenda.df.gov.br/"
s = Session()
# create a css selector to identify a button
check_for_button_css_sel = CSSSelector("a.botoes:nth-child(2)")
for url in urls:
    url = url.replace("\n", "")
    chave = pattern.search(url).group(0)[1:-1]
    # faz o request
    sleep(1)
    req = s.get(url)
    tree = html.fromstring(req.text)
    button = [btn for btn in check_for_button_css_sel(tree)]
    if button:
        # print(button[0].attrib['href'])
        final_part = button[0].attrib['href'][2:]
        # make a url to complete data
        url_to_new_section = f"{BASE_URL}{final_part}"
        print(f"get para {url_to_new_section}")
        req2 = s.get(url_to_new_section)
        if req2.status_code == 200:
            print(req2.text)
        else:
            print(req2.status_code)
            req2
# PORTAL_NFE_IMPRESSORA > a:nth-child(1) > img:nth-child(1)

# PORTAL_NFE_IMPRESSORA > a:nth-child(1) > img:nth-child(1)
