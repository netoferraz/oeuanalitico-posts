# INSTRUÇÕES DE USO

As urls das notas fiscais eletrônicas (Nfe) são armazenadas no Google Drive e utilizaremos a biblioteca [PyDrive](https://pythonhosted.org/PyDrive/index.html) para acessar os endereços.

Para isso é necessário acessar o [API Console](https://console.developers.google.com/
) do Google e seguir as instruções contidas nessa postagem do [stackoverflow](https://stackoverflow.com/a/33426759).

## authentication/gdrive-download.py
O script deve ser executado para realizar o download dos arquivos contendo as urls das NFe.

## db-manager.py
Cria o banco de dados.

## pre-processing/parser_url_files.py
Cria o arquivo /data/url_list.csv contendo todos as urls armazenadas nos arquivos localizados em `/data/nfe-url`
