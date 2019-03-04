import pandas as pd
from pathlib import Path
from collections import Counter
import datetime


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


def report_tabular_data(filename, foldername):
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
        print(f"Todos os arquivos .pkl foram processados. Ao todo foram processados {df['nf_chave'].nunique()} notas fiscais.\n")
    else:
        print(f"Não foram processados {len(num_arquivos_diff)} arquivos.\n")
        for f in num_arquivos_diff:
            print(f"Arquivo {f} não foi processado.\n")
    # VALIDAÇÃO SE HÁ ARQUIVOS DUPLICADOS
    files_check = Path(f"./data-storage/validacao/{foldername}")
    files_check = list(files_check.rglob("*.pkl"))
    files_check = [f.name[:-4][-44:] for f in files_check]
    a = Counter()
    for f in files_check:
        a[f] += 1
    for chave, count in a.items():
        if count > 1:
            print(f"CHAVE: {chave} # {count}")
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
            print(f"{chave} => Valor Nota: R${validacao} @ Valor Produtos: R${valor} @ Diferença: R${diff_produtos}\n")


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
