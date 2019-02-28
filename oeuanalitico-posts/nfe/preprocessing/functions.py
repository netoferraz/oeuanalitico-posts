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
                #armazena o index da primeira ocorrência da string ponto
                slice_index = num.index('.')
                #faz um slice baseado na localizacao desse index
                new_str = num[0:slice_index] + num[slice_index+1:]
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
        encoding='utf8'
        with open(filename, "r", encoding=encoding) as file:
            _ = file.readlines()
    except UnicodeDecodeError:
        encoding='latin1'
        with open(filename, "r", encoding=encoding) as file:
            _ = file.readlines()
    finally:
        return encoding