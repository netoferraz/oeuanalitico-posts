import lxml.html as lh
import sys
sys.path.append("./pre-processing")
from functions import convert_to_numeric
import pickle
from dataClass import NotaFiscal, Emitente, Destinatario, Produto
import os
import datetime
import time
from schema import v_nfe, v_em, v_dest, v_prod
import argparse

parser = argparse.ArgumentParser(description='Parser de arquivos .html em .pkl')
parser.add_argument("pathname", help="Diretório onde estão localizados os arquivos .html", type=str)
args = parser.parse_args()
#filtrar a lista de arquivos .html no diretorio
def Validation(pathname):
    start_time = time.time()
    list_folder = os.listdir(os.path.join(os.getcwd(), pathname))
    list_files = [x for x in list_folder if '.html' in x]
    for index_file, filename in enumerate(list_files):
        with open(f"{pathname}/{filename}", 'r', encoding='utf-8') as f:
            percentual = round((index_file+1)/len(list_files)*100,2)
            print(f"Iniciando o parser do arquivo {filename} @ status: {percentual}%")
            pgsrc = f.readlines()
            html = lh.fromstring("".join(pgsrc))
            #COLETAR DADOS DA NOTA FISCAL
            if html.find(".//title").text == '\n\tPortal da Nota Fiscal Eletrônica\n':
            #if html.find(".//title").text.strip() == 'Portal da Nota Fiscal Eletrônica':
                for feature in html.xpath('//span[contains(@class, "TextoFundoBrancoNegrito")]'):
                    if feature.text_content().strip() == 'Chave de Acesso':
                        checkPointNfe = feature

            tabelaNfe = checkPointNfe.getparent().getparent().getparent().getparent()

            for dadoNfe in tabelaNfe:
                for desc in dadoNfe.iterdescendants():
                    if 'TextoFundoBrancoNegrito' in desc.classes:
                        #CHAVE
                        if desc.text_content().strip() == 'Chave de Acesso':
                            chaveNfe = desc.getnext()
                            if not 'br' in chaveNfe.tag:
                                inputDataNfe = NotaFiscal(chaveNfe.text_content().strip())
                            else:
                                inputDataNfe = NotaFiscal(chaveNfe.getnext().text_content().strip())
                        #NÚMERO DA NOTA FISCAL
                        elif desc.text_content().strip() == 'Número NF-e':
                            numeroNfe = desc.getnext()
                            if not 'br' in numeroNfe.tag:
                                inputDataNfe.numero = numeroNfe.text_content().strip()
                            else:
                                inputDataNfe.numero = numeroNfe.getnext().text_content().strip()
                        #VERSÃO
                        elif desc.text_content().strip() == 'Versão':
                            numeroNfe = desc.getnext()
                            if not 'br' in numeroNfe.tag:
                                inputDataNfe.versao = numeroNfe.text_content().strip()
                            else:
                                inputDataNfe.versao = numeroNfe.getnext().text_content().strip()
            nfe_data_element = html.xpath('//*[@id="NFe"]')[0]

            for dadoNfe in nfe_data_element:
                for desc in dadoNfe.iterdescendants():
                    #DATA DE EMISSÃO
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
                    #MODELO
                    elif desc.text_content().strip() == 'Modelo':
                        dadoNota = desc.getnext()
                        if not 'br' in dadoNota.tag:
                            inputDataNfe.modelo = int(dadoNota.text_content().strip())
                        else:
                            inputDataNfe.modelo = int(dadoNota.getnext().text_content().strip())
                    #SÉRIE
                    elif desc.text_content().strip() == 'Série':
                        serieNfe = desc.getnext()
                        if not 'br' in serieNfe.tag:
                            inputDataNfe.serie = int(serieNfe.text_content().strip())
                        else:
                            inputDataNfe.serie = int(serieNfe.getnext().text_content().strip())
                    #NÚMERO
                    elif desc.text_content().strip() == 'Número':
                        numeroNfe = desc.getnext()
                        if not 'br' in numeroNfe.tag:
                            inputDataNfe.numero = int(numeroNfe.text_content().strip())
                        else:
                            inputDataNfe.numero = int(numeroNfe.getnext().text_content().strip())
                    #VALOR
                    elif desc.text_content() == "Valor\xa0Total\xa0da\xa0Nota\xa0Fiscal\xa0\xa0":
                        valorNfe = desc.getnext()
                        if not 'br' in valorNfe.tag:
                            inputDataNfe.valor = convert_to_numeric(valorNfe.text_content().strip())
                        else:      
                            inputDataNfe.valor = convert_to_numeric(valorNfe.getnext().text_content().strip())

            #DADOS DO EMISSOR

            emitente_data_element = html.xpath('//*[@id="Emitente"]')[0]

            for dadoEm in emitente_data_element:
                for desc in dadoEm.iterdescendants():
                    #RAZÃO SOCIAL
                    if desc.text_content().strip() == 'Nome / Razão Social':
                        rz = desc.getnext()
                        if not 'br' in rz.tag:
                            vendor = Emitente(rz.text_content().strip().replace(";", ""))
                        else:
                            vendor = Emitente(rz.getnext().text_content().strip().replace(";", ""))
                    #NOME FANTASIA
                    elif desc.text_content() == 'Nome Fantasia': 
                        nome_fantasia = desc.getnext()
                        if not 'br' in nome_fantasia.tag:
                            vendor.nome_fantasia = nome_fantasia.text_content().strip().replace(";", "")
                        else:
                            vendor.nome_fantasia = nome_fantasia.getnext().text_content().strip().replace(";", "")
                    #CNPJ
                    elif desc.text_content() == 'CNPJ': 
                        cnpj = desc.getnext()
                        if not 'br' in cnpj.tag:
                            vendor.cnpj = cnpj.text_content().strip()
                        else: 
                            vendor.cnpj = cnpj.getnext().text_content().strip()
                    #ENDEREÇO
                    elif desc.text_content() == 'Endereço':
                        endereco = desc.getnext()
                        if not 'br' in endereco.tag:
                            vendor.endereco = endereco.text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                        else:
                            vendor.endereco = endereco.getnext().text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                    #BAIRRO
                    elif desc.text_content() == 'Bairro / Distrito':
                        bairro = desc.getnext()
                        if not 'br' in bairro.tag:
                            vendor.bairro = bairro.text_content().strip().replace(";", "")
                        else:
                            vendor.bairro = bairro.getnext().text_content().strip().replace(";", "")
                    #CEP
                    elif desc.text_content() == 'CEP':
                        cep = desc.getnext()
                        if not 'br' in cep.tag:
                            vendor.cep = cep.text_content().strip().replace(";", "")
                        else:
                            vendor.cep = cep.getnext().text_content().strip().replace(";", "")
                    #MUNICIPIO
                    elif desc.text_content() == 'Município':
                        municipio = desc.getnext()
                        if not 'br' in municipio.tag:
                            vendor.municipio = municipio.text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                        else:
                            vendor.municipio = municipio.getnext().text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                    #TELEFONE
                    elif desc.text_content() == 'Telefone':
                        telefone = desc.getnext()
                        if not 'br' in telefone.tag:
                            vendor.telefone = telefone.text_content().rstrip().replace(";", "")
                        else:
                            vendor.telefone = telefone.getnext().text_content().rstrip().replace(";", "")
                    #UF
                    elif desc.text_content() == 'UF':
                        uf = desc.getnext()
                        if not 'br' in uf.tag:
                            vendor.uf = uf.text_content().rstrip().replace(";", "")
                        else:
                            vendor.uf = uf.getnext().text_content().rstrip().replace(";", "")
                    #PAÍS
                    elif desc.text_content() == 'País':
                        pais = desc.getnext()
                        if not 'br' in pais.tag:
                            vendor.pais = pais.text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                        else:
                            vendor.pais = pais.getnext().text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                    #INSCRIÇÃO ESTADUAL
                    elif desc.text_content() == 'Inscrição Estadual':
                        inscricao_estadual = desc.getnext()
                        if not 'br' in inscricao_estadual.tag:
                            vendor.inscricao_estadual = inscricao_estadual.text_content().rstrip().replace(";", "")
                        else:
                            vendor.inscricao_estadual = inscricao_estadual.getnext().text_content().rstrip().replace(";", "")
                    #INSCRIÇÃO MUNICIPAL
                    elif desc.text_content() == 'Inscrição Municipal':
                        inscricao_municipal = desc.getnext()
                        if not 'br' in inscricao_municipal.tag:
                            if inscricao_municipal.text_content().rstrip() != "":
                                vendor.inscricao_municipal = inscricao_municipal.text_content().rstrip().replace(";", "")
                        else:
                            if inscricao_municipal.getnext().text_content().rstrip() != "":
                                vendor.inscricao_municipal = inscricao_municipal.getnext().text_content().rstrip().replace(";", "")
                    #CNAE
                    elif desc.text_content() == 'CNAE Fiscal':
                        cnae_fiscal = desc.getnext()
                        if not 'br' in cnae_fiscal.tag:
                            vendor.cnae_fiscal = cnae_fiscal.text_content().rstrip().replace(";", "")
                        else:
                            vendor.cnae_fiscal = cnae_fiscal.getnext().text_content().rstrip().replace(";", "")

            dest_data_element = html.xpath('//*[@id="DestRem"]')[0]
            for dadoEm in dest_data_element:
                for desc in dadoEm.iterdescendants():
                    #RAZÃO SOCIAL
                    if desc.text_content().strip() == 'Nome / Razão Social':
                        rz = desc.getnext()
                        if not 'br' in rz.tag:
                            dest = Destinatario(rz.text_content().strip().replace(";", ""))
                        else:
                            dest = Destinatario(rz.getnext().text_content().strip().replace(";", ""))
                    #CNPJ
                    elif desc.text_content() == 'CNPJ': 
                        cnpj = desc.getnext()
                        if not 'br' in cnpj.tag:
                            dest.cnpj = cnpj.text_content().strip().replace(";", "")
                        else: 
                            dest.cnpj = cnpj.getnext().text_content().strip().replace(";", "")
                    #ENDEREÇO
                    elif desc.text_content() == 'Endereço':
                        endereco = desc.getnext()
                        if not 'br' in endereco.tag:
                            dest.endereco = endereco.text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                        else:
                            dest.endereco = endereco.getnext().text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                    #BAIRRO
                    elif desc.text_content() == 'Bairro / Distrito':
                        bairro = desc.getnext()
                        if not 'br' in bairro.tag:
                            dest.bairro = bairro.text_content().strip().replace(";", "")
                        else:
                            dest.bairro = bairro.getnext().text_content().strip().replace(";", "")
                    #CEP
                    elif desc.text_content() == 'CEP':
                        cep = desc.getnext()
                        if not 'br' in cep.tag:
                            dest.cep = cep.text_content().strip().replace(";", "")
                        else:
                            dest.cep = cep.getnext().text_content().strip().replace(";", "")
                    #MUNICIPIO
                    elif desc.text_content() == 'Município':
                        municipio = desc.getnext()
                        if not 'br' in municipio.tag:
                            dest.municipio = municipio.text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                        else:
                            dest.municipio = municipio.getnext().text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                    #TELEFONE
                    elif desc.text_content() == 'Telefone':
                        telefone = desc.getnext()
                        if not 'br' in telefone.tag:
                            dest.telefone = telefone.text_content().rstrip().replace(";", "")
                        else:
                            dest.telefone = telefone.getnext().text_content().rstrip().replace(";", "")
                    #UF
                    elif desc.text_content() == 'UF':
                        uf = desc.getnext()
                        if not 'br' in uf.tag:
                            dest.uf = uf.text_content().rstrip().replace(";", "")
                        else:
                            dest.uf = uf.getnext().text_content().rstrip().replace(";", "")
                    #PAIS
                    elif desc.text_content() == 'País':
                        pais = desc.getnext()
                        if not 'br' in pais.tag:
                            dest.pais = pais.text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                        else:
                            dest.pais = pais.getnext().text_content().rstrip().replace("  ","").replace('\n',"").replace(";", "")
                    #INSCRICAO ESTADUAL
                    elif desc.text_content() == 'Inscrição Estadual':
                        inscricao_estadual = desc.getnext()
                        if not 'br' in inscricao_estadual.tag:
                            dest.inscricao_estadual = inscricao_estadual.text_content().rstrip().replace(";", "")
                        else:
                            dest.inscricao_estadual = inscricao_estadual.getnext().text_content().rstrip().replace(";", "")
                    #EMAIL
                    elif desc.text_content() == 'E-mail':
                        email = desc.getnext()
                        if not 'br' in email.tag:
                            dest.email = email.text_content().rstrip().replace(";", "")
                        else:
                            dest.email = email.getnext().text_content().rstrip().replace(";", "")
            prod_data_element_p1 = html.xpath('//table[contains(@class, "toggle box")]')

            prod_data_element_p2 = html.xpath('//table[contains(@class, "toggable box")]')

            num_produtos = len(prod_data_element_p1)

            lista_produtos = [Produto("") for i in range(num_produtos)]

            lista_caracteristicas_produtos = []
            for dt in prod_data_element_p1:
                features = []
                #descrição
                descricao = dt.find_class("fixo-prod-serv-descricao")[0].text_content().strip()
                features.append(descricao)
                #quantidade
                quantidade = dt.find_class("fixo-prod-serv-qtd")[0].text_content().strip()
                features.append(quantidade)
                #unidade
                unidade = dt.find_class("fixo-prod-serv-uc")[0].text_content().strip()
                features.append(unidade)
                #valor
                valor = dt.find_class("fixo-prod-serv-vb")[0].text_content().strip()
                features.append(valor)
                lista_caracteristicas_produtos.append(features)

            for prod, lista_fts in zip(lista_produtos, lista_caracteristicas_produtos):
                try:
                    #nome
                    prod.nome = lista_fts[0].replace(";", "")
                except IndexError:
                    pass
                try:
                    #quantidade
                    prod.quantidade = convert_to_numeric(lista_fts[1])
                except IndexError:
                    pass
                try:
                    #unidade 
                    prod.unidade = lista_fts[2].replace(";", "")
                except IndexError:
                    pass
                try:
                    #VALOR
                    prod.valor = convert_to_numeric(lista_fts[3])
                except IndexError:
                    pass

            lista_caracteristicas_produtos = []
            for elem in prod_data_element_p2:
                features = {
                    'codProduto' : "", #Código do Produto
                    'cod_ncm' : "", #Código NCM
                    'cod_cfop' : "", #Código NCM
                    'cod_cest' : "", #Código CEST,
                    "cod_ean_cmc" : "", #Código EAN Comercial,
                    "valor_unit_cmc" : "", #Valor unitário de comercialização
                    "valor_unit_trib" : "", #Valor unitário de tributação
                    "cod_anp" : "", #Código do Produto da ANP
                }
                for desc in elem.iterdescendants():
                    if 'label' in desc.tag:
                        if desc.text_content().strip() == 'Código do Produto':
                            codProduto = desc.getnext()
                            if not 'br' in codProduto.tag:
                                features['codProduto'] = codProduto.text_content().strip().replace(";", "")
                            else:
                                features['codProduto'] = codProduto.getnext().text_content().strip().replace(";", "")
                        elif desc.text_content().strip() == 'Código NCM':
                            codncm = desc.getnext()
                            if not 'br' in codncm.tag:
                                features['cod_ncm'] = int(codncm.text_content().strip())
                            else:
                                features['cod_ncm'] = int(codncm.getnext().text_content().strip())
                        elif desc.text_content().strip() == 'CFOP':
                            codcfop = desc.getnext()
                            if not 'br' in codcfop.tag:
                                features['cod_cfop'] = int(codcfop.text_content().strip())
                            else:
                                features['cod_cfop'] = int(codcfop.getnext().text_content().strip())
                        elif desc.text_content().strip() == 'Código CEST':
                            codcest = desc.getnext()
                            if not 'br' in codcest.tag:
                                features['cod_cest'] = codcest.text_content().strip().replace(";", "")
                            else:
                                features['cod_cest'] = codcest.getnext().text_content().strip().replace(";", "")
                        elif desc.text_content().strip() == 'Código EAN Comercial':
                            codean_cmc = desc.getnext()
                            if not 'br' in codean_cmc.tag:
                                features['cod_ean_cmc'] = codean_cmc.text_content().strip().replace(";", "")
                            else:
                                features['cod_ean_cmc'] = codean_cmc.getnext().text_content().strip().replace(";", "")
                        elif desc.text_content().strip() == 'Valor unitário de comercialização':
                            valor_unit_comerc = desc.getnext()
                            if not 'br' in valor_unit_comerc.tag:
                                features['valor_unit_cmc'] = convert_to_numeric(valor_unit_comerc.text_content().strip())
                            else:
                                features['valor_unit_cmc'] = convert_to_numeric(valor_unit_comerc.getnext().text_content().strip())
                        elif desc.text_content().strip() == 'Valor unitário de tributação':
                            valor_unit_trib = desc.getnext()
                            if not 'br' in valor_unit_trib.tag:
                                features['valor_unit_trib'] = convert_to_numeric(valor_unit_trib.text_content().strip())
                            else:
                                features['valor_unit_trib'] = convert_to_numeric(valor_unit_trib.getnext().text_content().strip())
                        elif desc.text_content().strip() == 'Código do Produto da ANP':
                            codANP = desc.getnext()
                            if not 'br' in codANP.tag:
                                features['cod_anp'] = codANP.text_content().strip().replace(";", "")
                            else:
                                features['cod_anp'] = codANP.getnext().text_content().strip().replace(";", "")
                
                lista_caracteristicas_produtos.append(features)

            for prod, lista_fts in zip(lista_produtos, lista_caracteristicas_produtos):
                    try:
                        #Código do produto
                        prod.codigo_produto = lista_fts['codProduto']
                    except KeyError:
                        pass
                    try:
                        #Código NCM
                        prod.codigo_ncm = lista_fts['cod_ncm']
                    except KeyError:
                        pass
                    try:
                        #CFOP
                        prod.cfop = lista_fts['cod_cfop']
                    except KeyError:
                        pass
                    try:
                        #Código CEST
                        prod.cest = lista_fts['cod_cest']
                    except KeyError:
                        pass
                    try:
                        #Código EAN Comercial
                        prod.codigo_ean_comercial = lista_fts['cod_ean_cmc']
                    except KeyError:
                        pass
                    try:
                        #Valor unitário de comercialização
                        prod.valor_unitario_cmc = lista_fts['valor_unit_cmc']
                    except KeyError:
                        pass
                    try:
                        #Valor unitário de tributação
                        prod.valor_unitario_trib = lista_fts['valor_unit_trib']
                    except KeyError:
                        pass
                    try:
                        #Código do Produto da ANP
                        prod.codANP = lista_fts['cod_anp']
                    except KeyError:
                        pass
            #CRIA UM OBJETO PARA RECEBER OS DADOS VALIDADOS
            dataAgg = {
                'nfe_data' : "",
                'produtos' :"",
                'emissor' : "",
                'dest' : ""
                }
            #VALIDAÇÃO DADOS NOTA FISCAL
            nfe_data_validate = {
                'chave' : inputDataNfe.chave,
                'numero' : inputDataNfe.numero,
                'versao' : inputDataNfe.versao,
                'data' : inputDataNfe.data,
                'hora' : inputDataNfe.hora,
                'modelo' : inputDataNfe.modelo,
                'serie' : inputDataNfe.serie,
                'valor' : inputDataNfe.valor
            }

            if not v_nfe.validate(nfe_data_validate):
                with open("./logs/validation_log.txt", "a", encoding="ISO-8859-15") as f:
                    for feature, error in v_nfe.errors.items():
                            f.write(f"{nfe_data_validate['chave']}; \"nfe\"; {feature}; {nfe_data_validate[feature]}; {error}; {datetime.datetime.now()}\n")
                #print(v_nfe.errors)
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
                with open('./logs/validation_log.txt', 'a', encoding='ISO-8859-15') as f:
                    for feature, error in v_em.errors.items():
                            f.write(f"{inputDataNfe.chave}; \"emissor\"; {feature}; {em_data_validate[feature]}; {error}; {datetime.datetime.now()}\n")
                #print(v_em.errors)
            else:
                #ADICIONA OS DADOS DO OBJETO VALIDADO
                dataAgg['emissor'] = em_data_validate

            #VALIDAÇÃO DADOS DO DESTINATARIO DA NOTA FISCAL
            dest_data_validate = {
                'razaoSocial' : dest.razaoSocial,
                'cnpj' : dest.cnpj,
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
                with open('./logs/validation_log.txt', 'a', encoding='ISO-8859-15') as f:
                    for feature, error in v_dest.errors.items():
                        f.write(f"{inputDataNfe.chave}; \"destinatario\"; {feature}; {dest_data_validate[feature]}; {error}; {datetime.datetime.now()}\n")
                #print(v_dest.errors)
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
                    "cest" : produto.cest,
                    "codigo_ean_comercial" : produto.codigo_ean_comercial,
                    "valor_unitario_cmc" : produto.valor_unitario_cmc,
                    "valor_unitario_trib" : produto.valor_unitario_trib,
                    "unidade_trib" : produto.unidade_trib
                }
                #VERIFICA SE HÁ ERRO NA VALIDAÇÃO DO OBJETO
                v_prod.validate(prod_data_validate)
                if not v_prod.validate(prod_data_validate):
                    with open('./logs/validation_log.txt', 'a', encoding='ISO-8859-15') as f:
                        for feature, error in v_prod.errors.items():
                            f.write(f"{inputDataNfe.chave}; \"produto\"; {feature}; {prod_data_validate[feature]}; {error}; {datetime.datetime.now()}\n")        
                        #print(v_prod.errors)
                else:
                    #NA NEGATIVA DE ERRO, COLETA O OBJETO
                    validate_prod_list.append(prod_data_validate)

            #ADICIONA A LISTA DE PRODUTOS VALIDADA
            dataAgg['produtos'] = validate_prod_list

            timestamp = datetime.datetime.now()
            str_date = timestamp.strftime("%Y_%m_%d")
            year = timestamp.year
            month = timestamp.month
            day = timestamp.day
            hour = timestamp.hour
            minute = timestamp.minute
            second = timestamp.second
            file_tr_name = filename.replace(".html", "")
            filename = f"{year}_{month}_{day}_{hour}_{minute}_{second}_{file_tr_name}.pkl"
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
    Validation(args.pathname)