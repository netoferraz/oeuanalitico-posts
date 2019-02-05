from bs4 import BeautifulSoup
import re
import requests
from modules.funcs import post_request
from dotenv import load_dotenv
import os
load_dotenv(verbose=True)

sections = [
    'abastecimento',
    'biodiesel',
    'dados_tecnicos',
    'bloco',
    'producao',
    'exploracao',
    'fiscalizacao',
    'gas',
    'importacao',
    'meioambiente',
    'oleoduto',
    'gov',
    'qualidade',
    'refino'
]


[post_request(categoria) for categoria in sections]

"""
for categoria in sections:
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
    parse_leg(post)
"""
