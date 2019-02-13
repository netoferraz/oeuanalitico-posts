from selenium import webdriver
import time
from time import sleep
import datetime
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import argparse
import re
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

from dotenv import load_dotenv
parser = argparse.ArgumentParser(description='Scraper NFe')
parser.add_argument("pathname", help="Diretório para salvar os arquivos .html", type=str)
args = parser.parse_args()


def downloadNfe(pathtosave):
    load_dotenv(verbose=True)
    start_time = time.time()
    listpath = os.listdir(os.path.join(os.getcwd(), 'nfe-html'))
    if pathtosave in listpath:
        pass
    else:
        os.mkdir(os.path.join(os.getcwd(), 'nfe-html', pathtosave))
    webdriver_path = os.getenv("WEBDRIVER")
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Firefox(executable_path=webdriver_path, options=options)
    pattern = re.compile(r'=[0-9]{44}&')
    with open("./data/url_list.csv", "r") as f:
        urls = f.readlines()

    for index, url in enumerate(urls):
        sleep(5)
        url = url.replace("\n", "")
        # coleta a chave da nfe a partir da url
        try:
            chave = pattern.search(url).group(0)[1:-1]
            print(f"Iniciando parser da chave {chave}")
        except AttributeError:
            with open('./logs/download_status.csv', 'a') as w:
                w.write(f"{url}, ERROR, AttributeError on get key in URL\n")
            continue
        # acessa o link
        if len(driver.window_handles) > 1:
            driver.switch_to_window(driver.window_handles[-1])
            driver.close()
        driver.get(url)
        try:
            driver.find_element_by_css_selector("a.botoes:nth-child(2)").click()
        except NoSuchElementException:
            print(f"Não encontrado botão para chave {chave}.")
            if len(driver.window_handles) > 1:
                driver.switch_to_window(driver.window_handles[-1])
                driver.close()
            with open('./logs/download_status.csv', 'a') as w:
                w.write(f"{chave}, ERROR, NoSuchElementException\n")
            continue
        new_window = driver.window_handles[1]
        # change window
        sleep(5)
        driver.switch_to_window(new_window)
        """
        frame = driver.find_element_by_xpath("//iframe[@id='fundoif']")
        driver.switch_to_frame(element)
        """
        try:
            element = WebDriverWait(driver, 20).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@id='fundoif']")))
        except:
            print(f"Abortando chave {chave} por ausencia de iframe.")
            continue
        else:
            sleep(5)
            #driver.switch_to_frame(element)
        try:
            driver.find_element_by_css_selector("#PORTAL_NFE_IMPRESSORA > a:nth-child(1) > img:nth-child(1)").click()
        except NoSuchElementException:
            with open('./logs/download_status.csv', 'a') as w:
                w.write(f"{chave}, ERROR, NoSuchElementException\n")
            continue
        else:
            driver.switch_to_window(driver.window_handles[-1])
        # PORTAL_NFE_IMPRESSORA > a:nth-child(1) > img:nth-child(1)
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
        with open(filepath + "/" + filename, 'w') as f:
            f.write(page_source)

        with open('./logs/download_status.csv', 'a') as b:
            b.write(f"{chave}, OK, NA\n")

        print(f"NFe: {chave} ----> {index+1}/{len(lista_nfe)} @ {round((index+1)/len(lista_nfe)*100,2)}% concluído.")
        print('Download concluído:', time.strftime("%H:%M:%S"), '\n')
        drive.close()
        driver.switch_to_window(driver.window_handles[-1])
        drive.close()
    timeM = round((time.time() - start_time) / 60, 3)
    print(f"Tempo de execução foi de {timeM} minutos")


if __name__ == "__main__":
    downloadNfe(args.pathname)
