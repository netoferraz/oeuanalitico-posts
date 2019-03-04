from functions import report_tabular_data
import argparse

parser = argparse.ArgumentParser(description='Scraper NFe')
parser.add_argument("filename", help="Nome do arquivo .csv em ./tabular-data/", type=str)
parser.add_argument("foldername", help="Nome da pasta em ./data-storage/validacao/", type=str)
args = parser.parse_args()


def analisa_dados_tabulares(filename, foldername):
    """
        Atributos:
            filename: é o nome do arquivo .csv que será analisado.
            foldername: é o nome da sub pasta dos arquivos pkl dentro de ./data-storage/validacao/
    """
    report_tabular_data(filename, foldername)

if __name__ == '__main__':
    analisa_dados_tabulares(args.filename, args.foldername)
