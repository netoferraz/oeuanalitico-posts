import pandas as pd
from pathlib import Path
from collections import Counter
import datetime
from collections import defaultdict
from faker import Factory
import faker
from preprocessing.nfeProvider import Invoice
import csv


def convert_to_numeric(num):
    """
    Converte strings que representam valores monetários em Reais (R$) para
    o padrão americano.
    """
    num = num.strip()
    if num != "":
        num = num.replace(',', '.')
        count_dot = num.count('.')
        if count_dot >= 2:
            while count_dot >= 2:
                # armazena o index da primeira ocorrência da string ponto
                slice_index = num.index('.')
                # faz um slice baseado na localizacao desse index
                new_str = num[0:slice_index] + num[slice_index + 1:]
                num = new_str
                count_dot = num.count('.')
            return float(num)
        else:
            return float(num)
    else:
        return 0.0


def identify_encoding(filename: str) -> str:
    """
    Identifica o encoding do arquivo filename retornando uma string com o nome do encoding.

    Atributos:
        filename: é o path (full ou relativo) do arquivo a ser analisado.
    """
    try:
        encoding = 'utf8'
        with open(filename, "r", encoding=encoding) as file:
            _ = file.readlines()
    except UnicodeDecodeError:
        encoding = 'latin1'
        with open(filename, "r", encoding=encoding) as file:
            _ = file.readlines()
    finally:
        return encoding


def report_pkl_into_csv(filename, foldername, logger):
    """
    Produz um relatório do status do arquivo tabular gerado a partir dos arquivos .pkl

    Atributos:
        filename: é o nome do arquivo .csv que será analisado.
        foldername: é o nome da sub pasta dos arquivos pkl dentro de ./data-storage/validacao/
    """
    # VERIFICA SE ALGUM ARQUIVO .pkl NÃO FORAM PROCESSADOS.
    df = pd.read_csv(f"./tabular-data/{filename}.csv", sep=';', encoding='latin1')
    lista_chaves_processadas = set(df['nf_chave'].unique())
    pkl_folder = Path(f"./data-storage/validacao/{foldername}")
    pkl_folder = set(pkl_folder.rglob("*.pkl"))
    pkl_folder = set([f.name[:-4][-44:] for f in pkl_folder])
    num_arquivos_diff = lista_chaves_processadas.difference(pkl_folder)
    if len(num_arquivos_diff) == 0:
        logger.debug(f"Todos os arquivos .pkl foram processados. Ao todo foram processados {df['nf_chave'].nunique()} notas fiscais.\n")
    else:
        logger.critical(f"Não foram processados {len(num_arquivos_diff)} arquivos.\n")
        for f in num_arquivos_diff:
            logger.critical(f"Arquivo {f} não foi processado.\n")
    # VALIDAÇÃO SE HÁ ARQUIVOS DUPLICADOS
    files_check = Path(f"./data-storage/validacao/{foldername}")
    files_check = list(files_check.rglob("*.pkl"))
    files_check = [f.name[:-4][-44:] for f in files_check]
    a = Counter()
    for f in files_check:
        a[f] += 1
    for chave, count in a.items():
        if count > 1:
            logger.critical(f"CHAVE REPETIDA: {chave} # {count}")
    # VERIFICA SE HÁ ALGUMA INCONSISTÊNCIA NOS VALORES DOS PRODUTOS E DA NOTA FISCAL
    df['prod_valor_liquido'] = df.apply(lambda x: x['prod_valor'] - x['prod_valor_desconto'], axis='columns')
    check_valor_nota_valores = df.groupby("nf_chave")['prod_valor_liquido'].sum().sort_values(ascending=False)
    inconsistencia_count = 0
    container = {}
    for chave, valor in zip(check_valor_nota_valores.index, check_valor_nota_valores.values):
        validacao = df.loc[df['nf_chave'] == chave, 'nf_valor'].values[0]
        valor = round(valor, 2)
        chave = chave.replace("-", "").replace(".", "").replace("/", "")
        if validacao != valor:
            inconsistencia_count += 1
            diff_produtos = round(valor - validacao, 2)
            container[chave] = diff_produtos
            logger.critical(f"{chave} => Valor Nota: R${validacao} @ Valor Produtos: R${valor} @ Diferença: R${diff_produtos}\n")


def normalize_ncm(ncm: str) -> str:
    """
    Normaliza a string que representa o código NCM

    Atributos:
        ncm : string que representa o código NCM
    """
    if len(ncm) != 8:
        ncm = "0" + ncm
    return ncm


def get_ncm_values():
    """
    Função que retorna um dicionário contendo uma lista de macro categorias e os codigos
    NCM associados a cada um deles.
    """
    sheet_names = [
        'CARNES E OVOS',
        'HORTIFRUTI',
        'LIMPEZA',
        'HIGIENE',
        'LATICINIOS E DERIVADOS',
        'BEBIDAS',
        'PET',
        'PADARIA',
        'CEREAIS_GRAOS_SEMENTES',
        'DOCES',
        'VESTUARIO',
        'FARINACEOS',
        'MASSAS',
        'TEMPEROS_MOLHOS',
        'OUTROS'
    ]
    categorias_ncm = {}
    for sheet in sheet_names:
        df = pd.read_excel("./data/others/compilado_ncm_mercado_mod.xlsx", sheet_name=sheet, dtype={'cod_ncm': str})
        df['cod_ncm'] = df['cod_ncm'].astype(str)
        df['cod_ncm'] = df['cod_ncm'].apply(normalize_ncm)
        categorias_ncm[sheet] = df['cod_ncm'].unique().tolist()
    return categorias_ncm


def get_weekday(value: int):
    """
    Recebe um INT representando um datetime e retorna uma string com o dia da semana.

    Atributos:
        value: Inteiro representando um timestamp
    """
    convert_int_to_day = {
        0: 'Segunda-Feira',
        1: 'Terça-Feira',
        2: 'Quarta-Feira',
        3: 'Quinta-Feira',
        4: 'Sexta-Feira',
        5: 'Sábado',
        6: 'Domingo'
    }
    weekday = datetime.datetime.utcfromtimestamp(value / 1e9).weekday()
    return convert_int_to_day[weekday]


def logging_report(report, list_required_fields, logger):
    f = Path(report['tables'][0]['source'])
    map_columns_to_number = report['tables'][0]['headers']
    map_columns_to_number = {i: col for col, i in zip(map_columns_to_number, range(1, len(map_columns_to_number)))}
    fields_required_error = {f: False for f in list_required_fields}
    num_errors = report['error-count']
    if report['valid']:
        logger.debug(f"Arquivo: {f.name} válido pelo schema.\n")
        return True, num_errors
    else:
        lista_errors = report['tables'][0]['errors']
        if 0 < num_errors < 1000:
            logger.debug(f"Arquivo {f.name} não validado com {num_errors} erros.")
            for erro in lista_errors:
                for feature, valor in erro.items():
                    if feature == 'code':
                        if valor == 'required-constraint':
                            # identify which column is null
                            col = map_columns_to_number[erro['column-number']]
                            # change validation status of this feature
                            if not fields_required_error[col]:
                                fields_required_error[col] = True
                            line = erro['row-number']
                            logger.critical(f"{f.name} @ Linha {line} possui {col} sem valor atribuído.")
                        elif valor == 'enumerable-constraint':
                            col = map_columns_to_number[erro['column-number']]
                            line = erro['row-number']
                            logger.critical(f"{f.name} @ Linha {line} e Coluna {col} erro: {erro['message']} ")
                        else:
                            try:
                                col = map_columns_to_number[erro['column-number']]
                            except:  # o erro associado não é referente a uma coluna
                                try:
                                    line = erro['row-number']
                                    logger.critical(f"{f.name} @ Linha {line} : {erro['message']}")
                                except KeyError:
                                    logger.critical(f"{f.name} @ {erro['message']}")
        return False, num_errors


def anonymize_rows(rows):
    """
    Rows is an iterable of dictionaries that contain name and
    email fields that need to be anonymized.

    """
    # Load the faker and its providers
    faker = Factory.create("pt_BR")
    faker.add_provider(Invoice)

    # Create mappings of names & emails to faked names & emails.
    # https://stackoverflow.com/questions/18066837/passing-a-parameter-to-objects-created-by-defaultdict
    nfecod = defaultdict(lambda: faker.nfce(**{'uf_code': 'DF'}))
    cpf = defaultdict(faker.cpf)
    nome = defaultdict(faker.name)
    endereco = defaultdict(faker.address)
    bairro = defaultdict(faker.bairro)
    municipio = defaultdict(faker.city)
    telefone = defaultdict(faker.phone_number)
    uf = defaultdict(faker.state_abbr)
    pais = defaultdict(faker.country)
    email = defaultdict(faker.email)

    # Iterate over the rows and yield anonymized rows.
    for row in rows:
        # Replace the name and email fields with faked fields.
        row['nf_chave'] = nfecod[row['nf_chave']]
        row['dest_cpf'] = cpf[row['dest_cpf']]
        row['dest_rz'] = nome[row['dest_rz']]
        row['dest_endereco'] = endereco[row['dest_endereco']]
        row['dest_bairro'] = bairro[row['dest_bairro']]
        row['dest_municipio'] = municipio[row['dest_municipio']]
        row['dest_telefone'] = telefone[row['dest_telefone']]
        row['dest_uf'] = uf[row['dest_uf']]
        row['dest_pais'] = pais[row['dest_pais']]
        row['dest_email'] = email[row['dest_email']]

        # Yield the row back to the caller
        yield row


def anonymize(source, target):
    """
    The source argument is a path to a CSV file containing data to anonymize,
    while target is a path to write the anonymized CSV data to.
    """
    # https://pymotw.com/2/csv/
    PARTIAL_SOURCE_DATA = Path("./tabular-data/") / f"{source}"
    PARTIAL_DEST_DATA = Path("./tabular-data/") / f"{target}"
    csv.register_dialect('semicolon', delimiter=';')
    with open(PARTIAL_SOURCE_DATA, 'r') as f:
        with open(PARTIAL_DEST_DATA, 'w') as o:
            # Use the DictReader to easily extract fields
            reader = csv.DictReader(f, dialect='semicolon')
            writer = csv.DictWriter(o, reader.fieldnames, dialect='semicolon')
            # write col names
            writer.writeheader()
            # Read and anonymize data, writing to target file.
            for row in anonymize_rows(reader):
                writer.writerow(row)


def subseting_data(dataframe: pd.core.frame.DataFrame, rootname: str):
    """
    Salva um arquivo .csv com um subset das features originais
    """
    dataframe = dataframe[['nf_dia_semana', 'nf_chave', 'nf_valor', 'em_rz',
                           'em_nomeFantasia', 'em_cnpj', 'em_endereco', 'em_bairro', 'em_cep', 'em_municipio',
                           'em_telefone', 'em_uf', 'em_pais', 'em_inscricao_estadual', 'em_inscricao_municipal',
                           'em_cnae_fiscal', 'dest_rz', 'dest_cpf', 'dest_endereco', 'dest_bairro', 'dest_municipio',
                           'dest_telefone', 'dest_uf', 'dest_pais', 'dest_inscricao_estadual', 'dest_email', 'prod_nome',
                           'prod_quantidade', 'prod_unidade', 'prod_valor', 'prod_codigo_produto', 'prod_codigo_ncm',
                           'prod_categoria_ncm', 'prod_cfop', 'prod_valor_desconto', 'prod_valor_tributos',
                           'prod_codigo_ean_cmc', 'prod_valor_unitario_cmc', 'prod_valor_unitario_trib', 'prod_unidade_trib']]
    dataframe.to_csv(f"./tabular-data/PRE_ANONY_{rootname}.csv", sep=';', encoding='latin1', index=True)
