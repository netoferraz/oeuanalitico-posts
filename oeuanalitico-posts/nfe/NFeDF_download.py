from selenium import webdriver
import time
from time import sleep
import datetime
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import argparse
from parser_input_data import lista_nfe
import re
from selenium.common.exceptions import NoSuchElementException

parser = argparse.ArgumentParser(description='Scraper NFe')
parser.add_argument("pathname", help="Diretório para salvar os arquivos .html", type=str)
args = parser.parse_args()

def downloadNfe(pathtosave):
    start_time = time.time()
    listpath = os.listdir(os.path.join(os.getcwd(), 'nfe-html'))
    if pathtosave in listpath:
        pass
    else:
        os.mkdir(os.path.join(os.getcwd(), 'nfe-html', pathtosave))
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(chrome_options=options)
    pattern = re.compile(r'=[0-9]{44}&')
    for index, url in enumerate(lista_nfe):
        #coleta a chave da nfe a partir da url
        try:
            chave = pattern.search(url).group(0)[1:-1]
        except AttributeError:
            with open('./logs/download_status.csv', 'a') as w:
                w.write(f"{url}, ERROR, AttributeError on get key in URL\n")
            continue
        #acessa o link
        driver.get(url)

        try:
            driver.find_element_by_xpath("//*[@id=\"4\"]/a[2]/img").click()
        except NoSuchElementException:
            with open('./logs/download_status.csv', 'a') as w:
                w.write(f"{chave}, ERROR, NoSuchElementException\n")
            continue

        page_source = driver.page_source
        timestamp = datetime.datetime.now()
        year = timestamp.year
        month = timestamp.month
        day = timestamp.day
        hour = timestamp.hour
        minute = timestamp.minute
        second = timestamp.second
        filename = f"{year}_{month}_{day}_{hour}_{minute}_{second}_NFE_{chave}.html"

        filepath = os.path.join(os.getcwd(), 'nfe-html', pathtosave)
        with open(filepath+"/"+filename, 'w') as f:
            f.write(page_source)
        
        with open('./logs/download_status.csv', 'a') as b:
            b.write(f"{chave}, OK, NA\n")

        print(f"NFe: {chave} ----> {index+1}/{len(lista_nfe)} @ {round((index+1)/len(lista_nfe)*100,2)}% concluído.")
        print('Download concluído:', time.strftime("%H:%M:%S"),'\n')
    timeM = round((time.time() - start_time)/60,3)
    print(f"Tempo de execução foi de {timeM} minutos")

if __name__ == "__main__":
    downloadNfe(args.pathname)
