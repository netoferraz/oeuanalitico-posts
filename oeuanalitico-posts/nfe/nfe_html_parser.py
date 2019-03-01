from preprocessing.functions import convert_to_numeric, identify_encoding
from preprocessing.dataClass import NotaFiscal, Emitente, Destinatario, Produto
from preprocessing.schema import v_nfe, v_em, v_dest, v_prod
import lxml.html as lh
from logs.logger import logger_parser
import pickle
import os
import datetime
import time
import argparse
import re

parser = argparse.ArgumentParser(description='Parser de arquivos .html em .pkl')
parser.add_argument("pathname", help="Diretório onde estão localizados os arquivos .html", type=str)
args = parser.parse_args()
#filtrar a lista de arquivos .html no diretorio
def parserNfeHtmlFiles(pathname):
    start_time = time.time()
    #diretorio onde estão localizados os arquivos html
    fullpath = os.path.join(os.getcwd(), 'nfe-html', pathname)
    #lista todos os arquivos localizados no diretorio
    list_folder = os.listdir(fullpath)
    #filtra apenas os arquivos com extensão .html
    list_files = [html for html in list_folder if '.html' in html]
    list_files = [{'chave': chave, 'encoding': identify_encoding(os.path.join(fullpath, chave))} for chave in list_files]
    for index_file, file_data in enumerate(list_files):
        filename = file_data['chave']
        encoding = file_data['encoding']
        with open(os.path.join(fullpath, filename), 'r', encoding=encoding) as f:
            pgsrc = f.readlines()
            html = lh.fromstring("".join(pgsrc))
            filename_chave = filename[:-5]
            percentual = round((index_file+1)/len(list_files)*100,2)
            logger_parser.debug(f"Iniciando o parser do arquivo {filename} @ status: {percentual}%")
            #COLETAR DADOS DA NOTA FISCAL
            for feature in html.xpath('//span[contains(@class, "TextoFundoBrancoNegrito")]'):
                if feature.text_content().strip() == 'Chave de Acesso:':
                    checkPointNfe = feature

            tabelaNfe = checkPointNfe.getparent().getparent().getparent().getparent()

            for dadoNfe in tabelaNfe:
                for desc in dadoNfe.iterdescendants():
                    if 'TextoFundoBrancoNegrito' in desc.classes:
                        #CHAVE DA NOTA FISCAL
                        if desc.text_content().strip() == 'Chave de Acesso:':
                            chaveNfe = desc.getnext()
                            if not 'br' in chaveNfe.tag:
                                inputDataNfe = NotaFiscal(chaveNfe.text_content().strip())
                            else:
                                inputDataNfe = NotaFiscal(chaveNfe.getnext().text_content().strip())
                            try:
                                assert len(inputDataNfe.chave) == 59
                            except AssertionError as error:
                                logger_parser.critical(f"{filename_chave};{error};elemento não possui 59 caracteres")
                                continue
                            try:
                                chave_html = inputDataNfe.chave.replace("-","").replace(".", "").replace("/","").strip()
                                assert filename_chave[-44:].strip() == chave_html
                            except AssertionError as error:
                                logger_parser.critical(f"chave da url: {filename_chave[-44:]} != chave do html: {chave_html}.")
                                continue
                    #NÚMERO DA NOTA FISCAL
                    elif desc.text_content().strip() == 'Número NF-e:':
                        numeroNfe = desc.getnext()
                        if not 'br' in numeroNfe.tag:
                            try:
                                inputDataNfe.numero = int(numeroNfe.text_content().strip())
                            except ValueError as error:
                                logger_parser.critical(f"{filename_chave};{error};feature coletada não é INT;")
                        else:
                            try:
                                inputDataNfe.numero = int(numeroNfe.getnext().text_content().strip())
                            except ValueError as error:
                                logger_parser.critical(f"{filename_chave};{error};feature coletada não é INT;")

            #nfe_data_element = html.xpath('//*[@id="NFe"]')[0]
            try:
                nfe_data_element = html.xpath("/html/body/table/tbody/tr/td/table[3]")[0]
            except IndexError as error:
                logger_parser.critical(f"{filename_chave};{error};Não foi possível encontrar tabela com dados da NFE.")
                continue
            for dadoNfe in nfe_data_element:
                for desc in dadoNfe.iterdescendants():
                    if desc.text_content().strip() == 'Data de Emissão':
                        datetimeNfe = desc.getnext()
                        if not 'br' in datetimeNfe.tag:
                            dataNfe = datetimeNfe.text_content().strip()[:10]
                            horaNfe = datetimeNfe.text_content().strip()[11:19]
                            inputDataNfe.data = dataNfe
                            inputDataNfe.hora = horaNfe
                        else:
                            dataNfe = datetimeNfe.getnext().text_content().strip()[:10]
                            horaNfe = datetimeNfe.getnext().text_content().strip()[11:19]
                            inputDataNfe.data = dataNfe
                            inputDataNfe.hora = horaNfe
                    elif desc.text_content().strip() == 'Modelo':
                        dadoNota = desc.getnext()
                        if not 'br' in dadoNota.tag:
                            inputDataNfe.modelo = int(dadoNota.text_content().strip())
                        else:
                            inputDataNfe.modelo = int(dadoNota.getnext().text_content().strip())
                    elif desc.text_content().strip() == 'Série':
                        serieNfe = desc.getnext()
                        if not 'br' in serieNfe.tag:
                            inputDataNfe.serie = int(serieNfe.text_content().strip())
                        else:
                            inputDataNfe.serie = int(serieNfe.getnext().text_content().strip())
                    elif desc.text_content().strip() == 'Número':
                        numeroNfe = desc.getnext()
                        if not 'br' in numeroNfe.tag:
                            inputDataNfe.numero = int(numeroNfe.text_content().strip())
                        else:
                            inputDataNfe.numero = int(numeroNfe.getnext().text_content().strip())
                    elif desc.text_content().strip() == "Valor Total da Nota Fiscal":
                        valorNfe = desc.getnext()
                        if not 'br' in valorNfe.tag:
                            inputDataNfe.valor = convert_to_numeric(valorNfe.text_content().strip())
                        else:
                            try:
                                inputDataNfe.valor = convert_to_numeric(valorNfe.getnext().text_content().strip())
                            except AttributeError:
                                inputDataNfe.valor = convert_to_numeric(valorNfe.text_content().strip())

            #DADOS DO EMISSOR DA NOTA FISCAL ELETRÔNICA
            #emitente_data_element = html.xpath('//*[@id="Emitente"]')[0]
            emitente_data_element = html.xpath("/html/body/table/tbody/tr/td/table[11]")[0]
            for dadoEm in emitente_data_element:
                for desc in dadoEm.iterdescendants():
                    if desc.text_content().strip() == 'Nome / Razão Social':
                        rz = desc.getnext()
                        if not 'br' in rz.tag:
                            vendor = Emitente(rz.text_content().strip())
                        else:
                            vendor = Emitente(rz.getnext().text_content().strip())
                    elif desc.text_content() == 'Nome Fantasia':
                        nome_fantasia = desc.getnext()
                        if not 'br' in nome_fantasia.tag:
                            vendor.nome_fantasia = nome_fantasia.text_content().strip()
                        else:
                            vendor.nome_fantasia = nome_fantasia.getnext().text_content().strip()
                    elif desc.text_content() == 'CNPJ':
                        cnpj = desc.getnext()
                        if not 'br' in cnpj.tag:
                            vendor.cnpj = cnpj.text_content().strip()
                        else:
                            vendor.cnpj = cnpj.getnext().text_content().strip()
                    elif desc.text_content() == 'Endereço':
                        endereco = desc.getnext()
                        if not 'br' in endereco.tag:
                            vendor.endereco = endereco.text_content().rstrip().replace("  ","").replace('\n',"")
                        else:
                            vendor.endereco = endereco.getnext().text_content().rstrip().replace("  ","").replace('\n',"")
                    elif desc.text_content() == 'Bairro / Distrito':
                        bairro = desc.getnext()
                        if not 'br' in bairro.tag:
                            vendor.bairro = bairro.text_content().strip()
                        else:
                            vendor.bairro = bairro.getnext().text_content().strip()
                    elif desc.text_content() == 'CEP':
                        cep = desc.getnext()
                        if not 'br' in cep.tag:
                            vendor.cep = cep.text_content().strip()
                        else:
                            vendor.cep = cep.getnext().text_content().strip()
                    elif desc.text_content() == 'Município':
                        municipio = desc.getnext()
                        if not 'br' in municipio.tag:
                            vendor.municipio = municipio.text_content().rstrip().replace("  ","").replace('\n',"")
                        else:
                            vendor.municipio = municipio.getnext().text_content().rstrip().replace("  ","").replace('\n',"")
                    elif desc.text_content() == 'Telefone':
                        telefone = desc.getnext()
                        if not 'br' in telefone.tag:
                            vendor.telefone = telefone.text_content().rstrip()
                        else:
                            vendor.telefone = telefone.getnext().text_content().rstrip()
                    elif desc.text_content() == 'UF':
                        uf = desc.getnext()
                        if not 'br' in uf.tag:
                            vendor.uf = uf.text_content().rstrip()
                        else:
                            vendor.uf = uf.getnext().text_content().rstrip()
                    elif desc.text_content() == 'País':
                        pais = desc.getnext()
                        if not 'br' in pais.tag:
                            vendor.pais = pais.text_content().rstrip().replace("  ","").replace('\n',"")
                        else:
                            vendor.pais = pais.getnext().text_content().rstrip().replace("  ","").replace('\n',"")
                    elif desc.text_content() == 'Inscrição Estadual':
                        inscricao_estadual = desc.getnext()
                        if not 'br' in inscricao_estadual.tag:
                            vendor.inscricao_estadual = inscricao_estadual.text_content().rstrip()
                        else:
                            vendor.inscricao_estadual = inscricao_estadual.getnext().text_content().rstrip()
                    elif desc.text_content() == 'Inscrição Municipal':
                        inscricao_municipal = desc.getnext()
                        if not 'br' in inscricao_municipal.tag:
                            vendor.inscricao_municipal = inscricao_municipal.text_content().rstrip()
                        else:
                            vendor.inscricao_municipal = inscricao_municipal.getnext().text_content().rstrip()
                    elif desc.text_content() == 'CNAE Fiscal':
                        cnae_fiscal = desc.getnext()
                        if not 'br' in cnae_fiscal.tag:
                            vendor.cnae_fiscal = cnae_fiscal.text_content().rstrip()
                        else:
                            vendor.cnae_fiscal = cnae_fiscal.getnext().text_content().rstrip()
            #dest_data_element = html.xpath('//*[@id="DestRem"]')[0]
            dest_data_element = html.xpath('/html/body/table/tbody/tr/td/table[13]')[0]
            for dadoEm in dest_data_element:
                for desc in dadoEm.iterdescendants():
                    if desc.text_content().strip() == 'Nome / Razão Social':
                        rz = desc.getnext()
                        try:
                            if not 'br' in rz.tag:
                                dest = Destinatario(rz.text_content().strip())
                            else:
                                dest = Destinatario(rz.getnext().text_content().strip())
                        except AttributeError as error:
                            logger_parser.debug(f"{filename_chave};{error};Nome Destinatario")
                            continue
                    elif desc.text_content() == 'CPF':
                        cpf = desc.getnext()
                        if not 'br' in cpf.tag:
                            dest.cpf = cpf.text_content().strip()
                        else:
                            dest.cpf = cpf.getnext().text_content().strip()
                    elif desc.text_content() == 'Endereço':
                        endereco = desc.getnext()
                        if not 'br' in endereco.tag:
                            dest.endereco = endereco.text_content().rstrip().replace("  ","").replace('\n',"")
                        else:
                            dest.endereco = endereco.getnext().text_content().rstrip().replace("  ","").replace('\n',"")
                    elif desc.text_content() == 'Bairro / Distrito':
                        bairro = desc.getnext()
                        if not 'br' in bairro.tag:
                            dest.bairro = bairro.text_content().strip()
                        else:
                            dest.bairro = bairro.getnext().text_content().strip()
                    elif desc.text_content() == 'CEP':
                        cep = desc.getnext()
                        if not 'br' in cep.tag:
                            dest.cep = cep.text_content().strip()
                        else:
                            dest.cep = cep.getnext().text_content().strip()
                    elif desc.text_content() == 'Município':
                        municipio = desc.getnext()
                        if not 'br' in municipio.tag:
                            dest.municipio = municipio.text_content().rstrip().replace("  ","").replace('\n',"")
                        else:
                            dest.municipio = municipio.getnext().text_content().rstrip().replace("  ","").replace('\n',"")
                    elif desc.text_content() == 'Telefone':
                        telefone = desc.getnext()
                        if not 'br' in telefone.tag:
                            dest.telefone = telefone.text_content().rstrip()
                        else:
                            dest.telefone = telefone.getnext().text_content().rstrip()
                    elif desc.text_content() == 'UF':
                        uf = desc.getnext()
                        if not 'br' in uf.tag:
                            dest.uf = uf.text_content().rstrip()
                        else:
                            dest.uf = uf.getnext().text_content().rstrip()
                    elif desc.text_content() == 'País':
                        pais = desc.getnext()
                        if not 'br' in pais.tag:
                            dest.pais = pais.text_content().rstrip().replace("  ","").replace('\n',"")
                        else:
                            dest.pais = pais.getnext().text_content().rstrip().replace("  ","").replace('\n',"")
                    elif desc.text_content() == 'Inscrição Estadual':
                        inscricao_estadual = desc.getnext()
                        if not 'br' in inscricao_estadual.tag:
                            dest.inscricao_estadual = inscricao_estadual.text_content().rstrip()
                        else:
                            dest.inscricao_estadual = inscricao_estadual.getnext().text_content().rstrip()
                    elif desc.text_content() == 'E-mail':
                        email = desc.getnext()
                        if not 'br' in email.tag:
                            dest.email = email.text_content().rstrip()
                        else:
                            dest.email = email.getnext().text_content().rstrip()
            #PRODUTOS
            source_code = "".join(pgsrc)
            pattern = r'<div id="[0-9]+"'
            #COLETA TODOS OS DIVS QUE POSSUEM ID NUMÉRICO
            product_list = re.findall(pattern, source_code)
            #REALIZA UM FILTRO PARA SELECIONAR APENAS O ID NÚMERICO DAS STRINGS
            getID = [re.sub(r'\D',"", div) for div in product_list]
            #COLETA UMA LISTA DE WEB ELEMENTS (DIVS) QUE ESTÃO OS DADOS DOS PRODUTOS
            get_product_element = [html.get_element_by_id(idNum) for idNum in getID]

            num_produtos = len(get_product_element)

            lista_produtos = [Produto("") for i in range(num_produtos)]

            for featureProd, prod in zip(get_product_element, lista_produtos):
                ## Descrição
                ## Quantidade
                ## Unidade Comercial
                ## Valor(R$)
                headerProd = featureProd.getprevious()
                ##CÓDIGO DO PRODUTO
                #CÓDIGO NCM
                #CÓDIGO CFOP
                #CÓDIGO EAN COMERCIAL
                #VALOR UNITÁRIO DE COMERCIALIZAÇÃO
                #VALOR UNITÁRIO DE TRIBUTAÇÃO
                #UNIDADE
                nextTable = featureProd.getchildren()
                for dadofeature in headerProd:
                    try:
                        for desc in dadofeature.iterdescendants():
                            if 'span' in desc.tag:
                                ##desc.items() retorna uma lista com os atributos do webelement
                                ##inclusive a classe.
                                if "TextoFundoBrancoNegrito" in desc.items()[0][1]:
                                    if desc.text == "Descrição":
                                        value = desc.getnext()
                                        if "br" in value.tag:
                                            nome = value.getnext().text_content().strip().upper()
                                            prod.nome = nome
                                    elif desc.text == "Quantidade":
                                        value = desc.getnext()
                                        if "br" in value.tag:
                                            quantidade = value.getnext().text_content().strip()
                                            prod.quantidade = convert_to_numeric(quantidade)
                                    elif desc.text == "Unidade Comercial":
                                        value = desc.getnext()
                                        if "br" in value.tag:
                                            unidade = value.getnext().text_content().strip()
                                            prod.unidade = unidade
                                    elif desc.text == "Valor(R$)":
                                        value = desc.getnext()
                                        if "br" in value.tag:
                                            valor = value.getnext().text_content().strip()
                                            prod.valor = convert_to_numeric(valor)
                    except TypeError as error:
                        #logger_parser.debug(f"{filename_chave};{error};Dados Produto;")
                        pass
                for morefeature in nextTable:
                    try:
                        for desc in morefeature.iterdescendants():
                            if 'span' in desc.tag:
                                if desc.text_content().strip() == 'Código do produto':
                                    codProduto = desc.getnext()
                                    cod_produto = codProduto.text_content().strip()
                                    prod.codigo_produto = cod_produto
                                elif desc.text_content().strip() == 'Código NCM':
                                    codNCM = desc.getnext()
                                    cod_ncm = int(codNCM.text_content().strip())
                                    prod.codigo_ncm = cod_ncm
                                elif desc.text_content().strip() == 'CFOP':
                                    cfop = desc.getnext()
                                    cfop_data = int(cfop.text_content().strip())
                                    prod.cfop = cfop_data
                                elif desc.text_content().strip() == 'Código EAN Comercial':
                                    cd_ean_cmc = desc.getnext()
                                    try:
                                        ean_cmc = int(cd_ean_cmc.text_content().strip())
                                        prod.codigo_ean_comercial = ean_cmc
                                    except ValueError as error:
                                        logger_parser.debug(f"{filename_chave};{error};Dados Produto - {cd_ean_cmc.text_content().strip()} - {type(cd_ean_cmc.text_content().strip())}")
                                        pass
                                elif desc.text_content().strip() == 'Valor Unitário de Comercialização':
                                    valor_unit_cmc = desc.getnext()
                                    valor_unit = valor_unit_cmc.text_content().strip()
                                    prod.valor_unitario_cmc = convert_to_numeric(valor_unit)
                                elif desc.text_content().strip() == 'Valor Unitário de Tributação':
                                    valor_unit_trib = desc.getnext()
                                    valor_un_trib = valor_unit_trib.text_content().strip()
                                    prod.valor_unitario_trib = convert_to_numeric(valor_un_trib)
                                elif desc.text_content().strip() == "Unidade Tributável":
                                    unidade_trib = desc.getnext()
                                    unidade_tributavel = unidade_trib.text_content().strip()
                                    prod.unidade_trib = unidade_tributavel
                                elif desc.text_content().strip() == "Valor do Desconto":
                                    get_desconto = desc.getnext()
                                    valor_desconto = get_desconto.text_content().strip()
                                    prod.desconto = convert_to_numeric(valor_desconto)
                    except TypeError as error:
                        #logger_parser.debug(f"{filename_chave};{error};Dados Produto;")
                        pass

            dataAgg = {
                'nfe_data' : inputDataNfe,
                'produtos' :lista_produtos,
                'emissor' : vendor,
                'dest' : dest
                }

            #VALIDAÇÃO DADOS NOTA FISCAL
            nfe_data_validate = {
                'chave' : inputDataNfe.chave,
                'numero' : inputDataNfe.numero,
                'data' : inputDataNfe.data,
                'hora' : inputDataNfe.hora,
                'modelo' : inputDataNfe.modelo,
                'serie' : inputDataNfe.serie,
                'valor' : inputDataNfe.valor
            }

            if not v_nfe.validate(nfe_data_validate):
                for feature, error in v_nfe.errors.items():
                        logger_parser.error(f"{nfe_data_validate['chave']}; \"nfe\"; {feature}; {nfe_data_validate[feature]};{error}")
            else:
                #ADICIONA OS DADOS DO OBJETO VALIDADO
                dataAgg['nfe_data'] = nfe_data_validate

            #VALIDAÇÃO DADOS EMISSOR NOTA FISCAL
            em_data_validate = {
                'razaoSocial' : vendor.razaoSocial,
                'nome_fantasia' : vendor.nome_fantasia,
                'cnpj' : vendor.cnpj,
                'endereco' : vendor.endereco,
                'bairro' : vendor.bairro,
                'cep' : vendor.cep,
                'municipio' : vendor.municipio,
                'telefone' : vendor.telefone,
                'uf' : vendor.uf,
                'pais' : vendor.pais,
                'inscricao_estadual' : vendor.inscricao_estadual,
                'inscricao_municipal' : vendor.inscricao_municipal,
                'cnae_fiscal' : vendor.cnae_fiscal
            }

            if not v_em.validate(em_data_validate):
                for feature, error in v_em.errors.items():
                        logger_parser.error(f"{inputDataNfe.chave};\"emissor\";{feature};{em_data_validate[feature]};{error}")
            else:
                #ADICIONA OS DADOS DO OBJETO VALIDADO
                dataAgg['emissor'] = em_data_validate

            #VALIDAÇÃO DADOS DO DESTINATARIO DA NOTA FISCAL
            dest_data_validate = {
                'razaoSocial' : dest.razaoSocial,
                'cpf' : dest.cpf,
                'endereco' : dest.endereco,
                'bairro' : dest.bairro,
                'cep' : dest.cep,
                'municipio' : dest.municipio,
                'telefone' : dest.telefone,
                'uf' : dest.uf,
                'pais' : dest.pais,
                'inscricao_estadual' : dest.inscricao_estadual,
                'email' : dest.email
            }

            if not v_dest.validate(dest_data_validate):
                for feature, error in v_dest.errors.items():
                    logger_parser.error(f"{inputDataNfe.chave};\"destinatario\";{feature}; {dest_data_validate[feature]};{error}")
            else:
                #ADICIONA OS DADOS DO OBJETO VALIDADO
                dataAgg['dest'] = dest_data_validate

            #CRIA UMA LISTA PARA RECEBER OS OBJETOS VALIDADOS
            validate_prod_list = []
            for produto in lista_produtos:
                prod_data_validate = {
                    'nome' : produto.nome,
                    "quantidade" : produto.quantidade,
                    "unidade" : produto.unidade,
                    "valor" : produto.valor,
                    "codigo_produto" : produto.codigo_produto,
                    "codigo_ncm" : produto.codigo_ncm,
                    "cfop" : produto.cfop,
                    "valor_desconto" : produto.desconto,
                    "codigo_ean_comercial" : produto.codigo_ean_comercial,
                    "valor_unitario_cmc" : produto.valor_unitario_cmc,
                    "valor_unitario_trib" : produto.valor_unitario_trib,
                    "unidade_trib" : produto.unidade_trib
                }
                #VERIFICA SE HÁ ERRO NA VALIDAÇÃO DO OBJETO
                v_prod.validate(prod_data_validate)
                if not v_prod.validate(prod_data_validate):
                    for feature, error in v_prod.errors.items():
                        logger_parser.error(f"{inputDataNfe.chave};\"produto\";{feature};{prod_data_validate[feature]};{error}")
                else:
                    #NA NEGATIVA DE ERRO, COLETA O OBJETO
                    validate_prod_list.append(prod_data_validate)

            #ADICIONA A LISTA DE PRODUTOS VALIDADA

            valor_produtos=round(sum([(produto['valor']-produto['valor_desconto']) for produto in validate_prod_list]),2)
            try:
                assert valor_produtos == round(float(dataAgg['nfe_data']['valor']),2)
            except AssertionError:
                logger_parser.critical(f"{filename_chave};AssertionError;Valor produtos: {valor_produtos} != Valor Total NFE: {dataAgg['nfe_data']['valor']}")
            finally:
                dataAgg['produtos'] = validate_prod_list

            timestamp = datetime.datetime.now()
            str_date = timestamp.strftime("%Y_%m_%d")
            file_tr_name = filename.replace(".html", "")
            filename = f"{file_tr_name}.pkl"
            #LISTAR TODOS OS DIRETÓRIOS
            list_folders = [folder for folder in os.listdir("./data-storage/validacao/") if ".pkl" not in folder]
            if str_date not in list_folders:
                os.mkdir(f"./data-storage/validacao/{str_date}")
            filepath = os.path.join(os.getcwd(), 'data-storage', 'validacao', str_date)
            with open(filepath+"/"+filename, 'wb') as f:
                pickle.dump(dataAgg, f)

    timeM = round((time.time() - start_time)/60,3)
    print(f"Tempo de execução foi de {timeM} minutos")

if __name__ == "__main__":
    parserNfeHtmlFiles(args.pathname)
