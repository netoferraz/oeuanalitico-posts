from selenium import webdriver
from logs.logger import logger_get_html
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
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from pathlib import Path
parser = argparse.ArgumentParser(description='Scraper NFe')
parser.add_argument("pathname", help="Diretório para salvar os arquivos .html", type=str)
args = parser.parse_args()


def downloadNfe(pathtosave):
    load_dotenv(verbose=True)
    start_time = time.time()
    BASE_PATH = Path(os.path.join(os.getcwd(), 'nfe-html'))
    VALID_DOWNLOAD_PATH = Path("./data/processed/valid/")
    VALID_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)
    INVALID_DOWNLOAD_PATH = Path("./data/processed/invalid/")
    INVALID_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)
    DUPLICATED_DOWNLOAD_PATH = Path("./data/processed/duplicated")
    DUPLICATED_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)
    listpath = os.listdir(BASE_PATH)
    if pathtosave in listpath:
        pass
    else:
        os.mkdir(os.path.join(BASE_PATH, pathtosave))
    webdriver_path = os.getenv("WEBDRIVER_FIREFOX")
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0")
    driver = webdriver.Firefox(executable_path=webdriver_path,
                               options=options,
                               service_log_path='./logs/geckodriver.log')
    pattern = re.compile(r'=[0-9]{44}&')
    url_list = list(Path("./data/nfe-url/").rglob("*.txt"))
    num_files = range(0, len(url_list))
    for index, fname in zip(num_files, url_list):
        if index != 0:
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0")
            driver = webdriver.Firefox(executable_path=webdriver_path,
                                       options=options,
                                       service_log_path='./logs/geckodriver.log')
        sleep(2)
        with open(fname, 'r') as urlf:
            url = urlf.readlines()[0].replace("\n", "")
        # coleta a chave da nfe a partir da url
        try:
            chave = pattern.search(url).group(0)[1:-1]
            file_chave = BASE_PATH / pathtosave / f"{chave}.html"
            if file_chave.is_file():
                logger_get_html.debug(f"Arquivo {chave}.html já foi parseado.")
                for window in driver.window_handles:
                    driver.switch_to.window(window)
                    driver.close()
                os.rename(fname, DUPLICATED_DOWNLOAD_PATH / fname.name)
                continue
            else:
                logger_get_html.debug(f"Iniciando parser da chave {chave}")
        except AttributeError as error:
            driver.close()
            logger_get_html.critical(f"{error};{chave};{url};Não foi possível identificar chave.")
            # move to invalid directory
            os.rename(fname, INVALID_DOWNLOAD_PATH / fname.name)
            continue
        # acessa o link
        try:
            driver.get(url)
        except TimeoutException as error:
            logger_get_html.error(f"{error};{chave};{url};ERRO NO GET.")
            os.rename(fname, INVALID_DOWNLOAD_PATH / fname.name)
            continue
        try:
            driver.find_element_by_css_selector("a.botoes:nth-child(2)").click()
        except NoSuchElementException as error:
            logger_get_html.error(f"{error};{chave};{url};Item ausente.")
            os.rename(fname, INVALID_DOWNLOAD_PATH / fname.name)
            driver.close()
            continue
        else:
            num_windows = len(driver.window_handles)
            while num_windows == 1:
                print(f"Numero de janelas é de {num_windows}.")
                num_windows = len(driver.window_handles)
            new_window = driver.window_handles[1]
        # change window
        sleep(2)
        driver.switch_to.window(new_window)
        try:
            WebDriverWait(driver, 2).until(EC.alert_is_present(), "Verifica se há algum alerta.")
            alert = driver.switch_to.alert
            alert.accept()
        except TimeoutException:
            driver.switch_to.default_content()
        else:
            for window in driver.window_handles:
                driver.switch_to.window(window)
                driver.close()
            logger_get_html.error(f"POPUP;{chave};{url};Janela com Alerta.")
            os.rename(fname, INVALID_DOWNLOAD_PATH / fname.name)
            continue
        sleep(2)
        try:
            element = WebDriverWait(driver, 20).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id=\"fundoif\"]")))
        except:
            if len(driver.window_handles) > 1:
                for window in driver.window_handles:
                    driver.switch_to.window(window)
                    driver.close()
            logger_get_html.error(f"IFRAME;{chave};{url};Iframe não encontrado.")
            os.rename(fname, INVALID_DOWNLOAD_PATH / fname.name)
            continue
        else:
            sleep(5)
        try:
            driver.find_element_by_css_selector("#PORTAL_NFE_IMPRESSORA > a:nth-child(1) > img:nth-child(1)").click()
        except NoSuchElementException as error:
            driver.close()
            logger_get_html.error(f"{error};{chave};{url};Item não clicável.")
            os.rename(fname, INVALID_DOWNLOAD_PATH / fname.name)
            continue
        else:
            driver.switch_to.window(driver.window_handles[-1])
            sleep(5)
        page_source = driver.page_source
        filename = f"{chave}.html"

        filepath = os.path.join(BASE_PATH, pathtosave)
        with open(filepath + "/" + filename, 'w') as f:
            f.write(page_source)
        logger_get_html.info(f"NA;{chave};{url};Download concluído.")
        logger_get_html.debug(f"NFe: {chave} ----> {index+1}/{len(url_list)} @ {round((index+1)/len(url_list)*100,2)}% concluído.")
        logger_get_html.debug(f"Download concluído: {time.strftime('%H:%M:%S')}.\n")
        for window in driver.window_handles:
            driver.switch_to.window(window)
            driver.close()
            fname_target = fname.name
            try:
                fname.replace(VALID_DOWNLOAD_PATH / fname_target)
            except FileNotFoundError:
                pass
    timeM = round((time.time() - start_time) / 60, 3)
    logger_get_html.debug(f"Tempo de execução foi de {timeM} minutos")


if __name__ == "__main__":
    downloadNfe(args.pathname)
