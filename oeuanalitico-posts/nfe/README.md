# INSTRUÇÕES DE USO

As urls das notas fiscais eletrônicas (Nfe) são armazenadas no Google Drive e utilizaremos a biblioteca [PyDrive](https://pythonhosted.org/PyDrive/index.html) para acessar os endereços.

Para isso é necessário acessar o [API Console](https://console.developers.google.com/
) do Google e seguir as instruções contidas nessa postagem do [stackoverflow](https://stackoverflow.com/a/33426759).

## authentication/gdrive-download.py
O script deve ser executado para realizar o download dos arquivos contendo as urls das NFe.

## db-manager.py
Cria o banco de dados.

## nfe_download.py
Acessa as urls coletadas pelo script gdrive-download.py e realiza o download dos arquivos .html

## nfe_html_paser.py
Script para realizar o parser dos arquivos .html

## nfe_pkl_to_csv.py
Script para converter arquivos .pkl em .csv

