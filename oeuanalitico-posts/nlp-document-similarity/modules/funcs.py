from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re
import requests
from time import sleep
import os
import pathlib
from pathlib import Path

load_dotenv(verbose=True)


def parse_leg(post_request: requests.models.Response, categoria: str):
    """
    Função recebe a reposta de um POST request que retorna a 
    primeira página de legislações de uma dada categoria e verifica se há paginação
    para a referida categoria.
    """
    soup = BeautifulSoup(post_request.text)
    parse_html_from_lists(soup, categoria)
    #verifica se há páginação 
    check_pgs =  soup.findAll('div', {'class' : 'paginacao'})
    if check_pgs:
        num_pgs = check_pgs[0].findAll('a', {'data-pg' : re.compile(r'[0-9]')})
        for pg in num_pgs:
            numpg = pg.text
            BASE_URL = os.getenv("BASE_URL")
            new_url = f"{BASE_URL}/?tema={categoria}&cmbMes=&cmbAno=&buscageral=1&view=default&pg={numpg}"
            get_data = get_request(new_url)
            if get_data[0]:
                soup = BeautifulSoup(get_data[1].text)
                parse_html_from_lists(soup, categoria)


def get_text_from_html(text: str):
    """
    Receba uma string com o conteúdo textual do html a ser parseado.
    """
    #iniatilize a string to receive the data
    content = ""
    soup = BeautifulSoup(text)
    get_content = soup.findAll('div', {'class' : 'tile-list-1'})
    if get_content:
        #print(get_content[0].text)
        content += get_content[0].text
        anexo = soup.findAll('anexo')
        if anexo:
            content += "\n"
            table_content = soup.findAll('p', {'class' : 'Tabela-Texto'})
            for t in table_content:
                #print(t.text)
                content += t.text
        #print("\n\n")
    return content


def parse_html_from_lists(soup: BeautifulSoup, categoria: str):
    """
    Recebe um objeto BeautifulSoup oriundo de uma paginação listando os normativos e
    uma string representando a categoria do normativo e filtra todos os links contidos 
    na página e coleta o conteúdo destes.
    """
    BASE_URL = os.getenv("BASE_URL")
    content = soup.findAll('a', {'class' : 'linkArticle'})
    makepath = set_path_to_file(categoria)
    for tag in content:
        print(f"Processando o documento {tag.text}.\n")
        fpath = makepath / f"{tag.text}.txt"
        with open(fpath, "w") as file_:
            url = f"{BASE_URL}{tag['href']}"
            get_data = get_request(url)
            if get_data[0]:
                #get_text_from_html(get_data[1].text)
                bodytext = get_text_from_html(get_data[1].text)
                file_.write(bodytext)

def set_path_to_file(categoria: str) -> pathlib.PosixPath:
    """
    Receba uma string com o nome da categoria da lesgilação e retorna
    um objeto pathlib.PosixPath
    """
    fpath = Path(f"./data/{categoria}")
    fpath.mkdir(parents=True, exist_ok=True)
    return fpath


def get_request(url: str) -> (bool, requests.models.Response):
    """
    Recebe uma string representando um link para ser realizado um GET request
    e retorna uma tupla com um booleano e um reposta do request.
    """
    sleep(1)
    r = requests.get(url)
    if r.status_code == 200:
        print(url)
        return True, r
    else:
        return False, r

def post_request(categoria: str):
    """
    Recebe uma string representando uma categoria de normativo e realiza um POST request.
    """
    BASE_URL = os.getenv("BASE_URL")
    HEADERS = {'User-Agent': 'Mozilla/5.0'}

    payload = {
        'tema': f"{categoria}",
        "cmbMes": "" ,
        "cmbAno" : "",
        "buscageral" : "1"
        }
    session = requests.Session()
    post = session.post(BASE_URL, 
                        headers=HEADERS, 
                        data=payload, 
                        allow_redirects=True)
    parse_leg(post, categoria)






