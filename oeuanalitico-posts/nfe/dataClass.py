class NotaFiscal(object):
    def __init__(self, chave):
        #Chave de Acesso:
        self.chave = chave
    #Número NF-e:
    numero = int()
    #Data de Emissão:
    data = str()
    #Hora
    hora = str()
    #Modelo
    modelo = int()
    #Série
    serie = int()
    #Valor Total da Nota Fiscal
    valor = float()

class Emitente(object):
    def __init__(self, razaoSocial):
        #Nome / Razão Social
        self.razaoSocial = razaoSocial
    #Nome Fantasia
    nome_fantasia = str()
    #CNPJ
    cnpj = str()
    #Endereço
    endereco = str()
    #Bairro / Distrito
    bairro = str()
    #CEP
    cep = str()
    #Município
    municipio = str()
    #Telefone
    telefone = str()
    #UF
    uf = str()
    #País
    pais = str()
    #Inscrição Estadual
    inscricao_estadual = str()
    #Inscrição Municipal
    inscricao_municipal = str()
    #CNAE Fiscal
    cnae_fiscal = str()

class Destinatario(object):
    def __init__(self, razaoSocial):
        #Nome / Razão Social
        self.razaoSocial = razaoSocial
    #CPF
    cpf = str()
    #Endereço
    endereco = str()
    #Bairro / Distrito
    bairro = str()
    #CEP
    cep = str()
    #Município
    municipio = str()
    #Telefone
    telefone = str()
    #UF
    uf = str()
    #País
    pais = str()
    #Inscrição Estadual
    inscricao_estadual = str()
    #email
    email = str()

class Produto(object):
    def __init__(self, nome):
        self.nome = nome
    #QUANTIDADE
    quantidade = float()
    #Unidade Comercial
    unidade = str()
    #VALOR
    valor = float()
    #Código do produto
    codigo_produto = str()
    #Código NCM
    codigo_ncm = int()
    #CFOP
    cfop = int()
    #Código EAN Comercial
    codigo_ean_comercial = int()
    #Valor Unitário de Comercialização
    valor_unitario_cmc = float()
    #Valor Unitário de Tributação
    valor_unitario_trib = float()
    #unidade tributável
    unidade_trib = str()