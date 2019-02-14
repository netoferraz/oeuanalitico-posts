def convert_to_numeric(num):
    """
    Converte strings que representam valores monetários em Reais (R$) para
    o padrão americano.
    """
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