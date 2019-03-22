import os
import pickle
import argparse
import time
import pandas as pd
from dotenv import load_dotenv
from goodtables import validate
from logs.logger import logger_tabular
from preprocessing.functions import normalize_ncm, get_ncm_values, get_weekday, logging_report, report_pkl_into_csv, subseting_data
parser = argparse.ArgumentParser(description='Parser de arquivos .pkl e retorna um csv')
parser.add_argument("pathname", help="Diretório onde estão localizados os arquivos .pkl", type=str)
parser.add_argument("filename", help="nome que será dado ao arquivo .csv")
args = parser.parse_args()


def pklParserToCsV(pathname, filename):
    load_dotenv(verbose=True)
    start_time = time.time()
    # list os arquivos para realizar o parser
    path = os.path.join(os.getcwd(), "data-storage/validacao", pathname)
    listdir = os.listdir(path)
    pklFiles = [f for f in listdir if '.pkl' in f]
    cols = [
        'nf_chave',
        'nf_numero',
        'nf_data',
        'nf_hora',
        'nf_modelo',
        'nf_serie',
        'nf_valor',
        'em_rz',
        'em_nomeFantasia',
        'em_cnpj',
        'em_endereco',
        'em_bairro',
        'em_cep',
        'em_municipio',
        'em_telefone',
        'em_uf',
        'em_pais',
        'em_inscricao_estadual',
        'em_inscricao_municipal',
        'em_cnae_fiscal',
        'dest_rz',
        'dest_cpf',
        'dest_endereco',
        'dest_bairro',
        'dest_cep',
        'dest_municipio',
        'dest_telefone',
        'dest_uf',
        'dest_pais',
        'dest_inscricao_estadual',
        'dest_email',
        'prod_nome',
        'prod_quantidade',
        'prod_unidade',
        'prod_valor',
        'prod_codigo_produto',
        'prod_codigo_ncm',
        'prod_cfop',
        'prod_valor_desconto',
        'prod_valor_tributos',
        'prod_codigo_ean_cmc',
        'prod_valor_unitario_cmc',
        'prod_valor_unitario_trib',
        'prod_unidade_trib'
    ]
    # começar escrita do arquivo .csv
    with open(f"./tabular-data/{filename}.csv", 'w', encoding='ISO-8859-15') as csv:
        string_cols = ""
        for col in cols:
            if col != "prod_unidade_trib":
                string_cols += f"{col};"
            else:
                string_cols += f"{col}"
        csv.write(string_cols + "\n")
        for index_file, file in enumerate(pklFiles):
            with open(os.path.join(path, file), 'rb') as filedata:
                percentual = round((index_file + 1) / len(pklFiles) * 100, 2)
                data = pickle.load(filedata)
                validate_data = {
                    "container": False,
                    "nfe": False,
                    "vendor": False,
                    "dest": False,
                    "produto": False
                }
                try:
                    assert isinstance(data, dict)
                    validate_data['container'] = True
                except AssertionError as error:
                    logger_tabular.critical(f"{file};{error};ausência de arquivo .pkl")
                    continue
                # nota fiscal
                nfe = data['nfe_data']
                nfe['chave'] = nfe['chave'].replace("/", "").replace("-", "").replace(".", "")
                try:
                    assert isinstance(nfe, dict)
                    validate_data['nfe'] = True
                except AssertionError as error:
                    logger_tabular.critical(f"{file};{error};ausência de chave {nfe['chave']}.")
                    pass
                # emissor
                vendor = data['emissor']
                try:
                    assert isinstance(vendor, dict)
                    validate_data['vendor'] = True
                except AssertionError as error:
                    logger_tabular.critical(f"{file};{error};ausência de rz {vendor['razaoSocial']}.")
                    pass
                # destinatario
                dest = data['dest']
                try:
                    assert isinstance(dest, dict)
                    validate_data['dest'] = True
                except AssertionError as error:
                    logger_tabular.warning(f"{file};{error};ausência de {dest['cpf']}")
                    pass
                # produtos
                produto = data['produtos']
                if len(produto) == 1:
                    try:
                        assert isinstance(produto[0], dict)
                        validate_data['produto'] = True
                    except AssertionError as error:
                        logger_tabular.critical(f"{file};{error};ausência de nome de produto {produto[0]['nome']}")
                        pass
                    if validate_data['nfe']:
                        # DADOS NOTA FISCAL
                        dados_nfe = f"{nfe['chave']}; {nfe['numero']}; {nfe['data']}; {nfe['hora']}; {nfe['modelo']}; {nfe['serie']}; {nfe['valor']};"
                    if validate_data['vendor']:
                        # DADOS EMISSOR DA NOTA FISCAL
                        dados_emissor_p1 = f"{vendor['razaoSocial']}; {vendor['nome_fantasia']}; {vendor['cnpj']}; {vendor['endereco']}; {vendor['bairro']};"
                        dados_emissor_p2 = f"{vendor['cep']}; {vendor['municipio']}; {vendor['telefone']}; {vendor['uf']}; {vendor['pais']}; {vendor['inscricao_estadual']};"
                        dados_emissor_p3 = f"{vendor['inscricao_municipal']}; {vendor['cnae_fiscal']};"
                    if validate_data['dest']:
                        # DADOS DO DESTINATÁRIO DA NOTA FISCAL
                        dados_dest_p1 = f"{dest['razaoSocial']}; {dest['cpf']}; {dest['endereco']}; {dest['bairro']}; {dest['cep']}; {dest['municipio']}; {dest['telefone']};"
                        dados_dest_p2 = f"{dest['uf']}; {dest['pais']}; {dest['inscricao_estadual']}; {dest['email']};"
                    if validate_data['produto']:
                        # DADOS DO PRODUTO
                        dados_prod_p1 = f"{produto[0]['nome']};{produto[0]['quantidade']};{produto[0]['unidade']};{produto[0]['valor']};{produto[0]['codigo_produto']};{produto[0]['codigo_ncm']};{produto[0]['cfop']};{produto[0]['valor_desconto']};{produto[0]['valor_tributos']};"
                        dados_prod_p2 = f"{produto[0]['codigo_ean_comercial']};{produto[0]['valor_unitario_cmc']};{produto[0]['valor_unitario_trib']};{produto[0]['unidade_trib']}"
                    full_line = dados_nfe + dados_emissor_p1 + dados_emissor_p2 + dados_emissor_p3 + dados_dest_p1 + dados_dest_p2 + dados_prod_p1 + dados_prod_p2
                    csv.write(full_line + '\n')
                    validate_data['produto'] = False
                elif len(produto) > 1:
                    for pdt in produto:
                        try:
                            assert isinstance(pdt, dict)
                            validate_data['produto'] = True
                        except AssertionError as error:
                            logger_tabular.critical(f"{file};{error};ausência de nome de produto {produto[0]['nome']}")
                            pass
                        if validate_data['nfe']:
                            # DADOS NOTA FISCAL
                            dados_nfe = f"{nfe['chave']}; {nfe['numero']}; {nfe['data']}; {nfe['hora']}; {nfe['modelo']}; {nfe['serie']}; {nfe['valor']};"
                        if validate_data['vendor']:
                            # DADOS EMISSOR DA NOTA FISCAL
                            dados_emissor_p1 = f"{vendor['razaoSocial']}; {vendor['nome_fantasia']}; {vendor['cnpj']}; {vendor['endereco']}; {vendor['bairro']};"
                            dados_emissor_p2 = f"{vendor['cep']}; {vendor['municipio']}; {vendor['telefone']}; {vendor['uf']}; {vendor['pais']}; {vendor['inscricao_estadual']};"
                            dados_emissor_p3 = f"{vendor['inscricao_municipal']}; {vendor['cnae_fiscal']};"
                        if validate_data['dest']:
                            # DADOS DO DESTINATÁRIO DA NOTA FISCAL
                            dados_dest_p1 = f"{dest['razaoSocial']}; {dest['cpf']}; {dest['endereco']}; {dest['bairro']}; {dest['cep']}; {dest['municipio']}; {dest['telefone']};"
                            dados_dest_p2 = f"{dest['uf']}; {dest['pais']}; {dest['inscricao_estadual']}; {dest['email']};"
                        if validate_data['produto']:
                            # DADOS DO PRODUTO
                            dados_prod_p1 = f"{pdt['nome']};{pdt['quantidade']};{pdt['unidade']};{pdt['valor']};{pdt['codigo_produto']};{pdt['codigo_ncm']};{pdt['cfop']};{pdt['valor_desconto']};{pdt['valor_tributos']};"
                            dados_prod_p2 = f"{pdt['codigo_ean_comercial']}; {pdt['valor_unitario_cmc']}; {pdt['valor_unitario_trib']}; {pdt['unidade_trib']}"

                        full_line = dados_nfe + dados_emissor_p1 + dados_emissor_p2 + dados_emissor_p3 + dados_dest_p1 + dados_dest_p2 + dados_prod_p1 + dados_prod_p2
                        csv.write(full_line + '\n')
                        validate_data['produto'] = False
                    print(f"Escrita do arquivo {file} @ status: {percentual}%")
                else:
                    print(f"Nfe {file} não validada para escrita.")
    # INPUTA DADOS DE CATEGORIA NCM
    df = pd.read_csv(f"./tabular-data/{args.filename}.csv", sep=';', encoding='latin1')
    ncm = pd.read_csv("./data/others/NCM.csv", sep=';', encoding='latin1', dtype={'CO_NCM': str})
    df['prod_codigo_ncm'] = df['prod_codigo_ncm'].astype(str)
    df['prod_codigo_ncm'] = df['prod_codigo_ncm'].apply(normalize_ncm)
    seleciona_codigo_ncm = get_ncm_values()
    merge_cnm_codes = []
    [merge_cnm_codes.extend(codigos) for codigos in seleciona_codigo_ncm.values()]
    df['prod_categoria_ncm'] = ""
    for cat, lista_ncm in seleciona_codigo_ncm.items():
        for ncmcod in lista_ncm:
            df.loc[df['prod_codigo_ncm'] == ncmcod, 'prod_categoria_ncm'] = cat
    df['nf_datetime'] = df.apply(lambda x: x['nf_data'] + " " + x['nf_hora'], axis='columns')
    df['nf_datetime'] = df['nf_datetime'].apply(lambda x: x.strip())
    df['nf_datetime'] = pd.to_datetime(df['nf_datetime'], format="%d/%m/%Y %H:%M:%S")
    df.set_index(df['nf_datetime'], inplace=True)
    df = df.sort_index()
    del df['nf_datetime']
    df.index = pd.to_datetime(df.index)
    df['datetime'] = df.index.values.tolist()
    df['nf_dia_semana'] = df['datetime'].apply(lambda x: get_weekday(x))
    del df['datetime']
    df = df[['nf_dia_semana', 'nf_chave', 'nf_numero', 'nf_modelo', 'nf_serie',
             'nf_valor', 'em_rz', 'em_nomeFantasia', 'em_cnpj', 'em_endereco',
             'em_bairro', 'em_cep', 'em_municipio', 'em_telefone', 'em_uf',
             'em_pais', 'em_inscricao_estadual', 'em_inscricao_municipal',
             'em_cnae_fiscal', 'dest_rz', 'dest_cpf', 'dest_endereco', 'dest_bairro',
             'dest_cep', 'dest_municipio', 'dest_telefone', 'dest_uf', 'dest_pais',
             'dest_inscricao_estadual', 'dest_email', 'prod_nome', 'prod_quantidade',
             'prod_unidade', 'prod_valor', 'prod_codigo_produto', 'prod_codigo_ncm',
             'prod_categoria_ncm', 'prod_cfop', 'prod_valor_desconto', 'prod_valor_tributos',
             'prod_codigo_ean_cmc', 'prod_valor_unitario_cmc', 'prod_valor_unitario_trib',
             'prod_unidade_trib']]
    df['em_cnpj'] = df['em_cnpj'].str.strip()
    df['em_uf'] = df['em_uf'].str.strip()
    df['dest_uf'] = df['dest_uf'].str.strip()
    subseting_data(df, args.filename)
    df.to_csv(f"./tabular-data/{args.filename}.csv", sep=';', encoding='latin1')
    # validate data against schema
    report = validate(f"./tabular-data/{args.filename}.csv",
                      schema=os.getenv("TABULAR_SCHEMA"),
                      row_limit=-1,
                      skip_checks=['duplicate-row']
                      )

    is_valid, num_errors = logging_report(report,
                                         [
                                            'nf_datetime',
                                            'nf_dia_semana',
                                            'nf_chave',
                                            'nf_numero',
                                            'nf_modelo',
                                            'nf_serie',
                                            'nf_valor',
                                            'em_cnpj',
                                            'em_uf',
                                            'prod_nome',
                                            'prod_valor',
                                            'prod_codigo_ncm',
                                            'prod_cfop',
                                            'prod_valor_desconto',
                                            'prod_valor_tributos',
                                            'prod_codigo_ean_cmc',
                                            'prod_valor_unitario_cmc',
                                            'prod_valor_unitario_trib'
                                         ],
                                         logger_tabular)
    timeM = round((time.time() - start_time) / 60, 3)
    if is_valid:
        report_pkl_into_csv(args.filename, args.pathname, logger_tabular)
    else:
        logging_report.debug("Verique os erros de validação e rode o programa novamente.")
    print(f"Tempo de execução foi de {timeM} minutos")


if __name__ == "__main__":
    pklParserToCsV(args.pathname, args.filename)
