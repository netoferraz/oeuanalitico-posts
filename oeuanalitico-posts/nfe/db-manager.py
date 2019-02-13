from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, Float, String, Boolean, insert, Numeric, Integer
from sqlalchemy.schema import ForeignKey
import os
host = os.path.join(os.getcwd(), 'db', 'nfe.db')

engine = create_engine(f"sqlite:///{host}")
conn = engine.connect()

#metadata instance
metadata = MetaData(engine)
check_tables = ['nfe', 'emissor', 'dest', 'produto', 'storage']

# http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html

# nfe <-> Emissor (One-to-One)
# nfe <-> Destinatario (One-to-One)
# nfe <-> Produto (One-to-Many)


#check if the tables exists in database
if all([tabela in metadata.tables.keys() for tabela in check_tables]):
    pass
else:
    #nfe table
    nfe = Table('nfe', metadata,
        Column('id', Integer, primary_key=True),
        Column('chave', String),
        Column('numero', Integer),
        Column('data', String),
        Column('hora', String),
        Column('modelo', Integer),
        Column('serie', Integer),
        Column('valor', Integer)

    )
    #emissor table
    emissor = Table('emissor', metadata,
        Column('id', Integer, primary_key=True),
        Column('cnpj', String(18)),
        Column('razaosocial', String),
        Column('nomefantasia', String),
        Column('endereco', String),
        Column('bairro', String),
        Column('cep', String),
        Column('municipio', String),
        Column('telefone', String),
        Column('uf', String(2)),
        Column('pais', String),
        Column('inscricao_estadual', String),
        Column('inscricao_municipal', String),
        Column('cnae_fiscal', String)

    )
    #destinatario table
    dest = Table('dest', metadata,
        Column('id', Integer, primary_key=True),
        Column('cpf_cnpj', String(18)),
        Column('razaosocial', String),
        Column('endereco', String),
        Column('bairro', String),
        Column('cep', String),
        Column('municipio', String),
        Column('telefone', String),
        Column('uf', String(2)),
        Column('pais', String),
        Column('inscricao_estadual', String),
        Column('email', String)
    )
    #produto table
    produto = Table('produto', metadata,
        Column('id', Integer, primary_key=True),
        Column('nfe_id', String, ForeignKey("nfe.id"), nullable=False),
        Column('emissor_id', Integer, ForeignKey("emissor.id"), nullable=False),
        Column('dest_id', Integer, ForeignKey("dest.id"), nullable=False),
        Column('nome', String),
        Column('quantidade', Float),
        Column('unidade', String),
        Column('valor', Float),
        Column('codigo_produto', String),
        Column('codigo_ncm', Integer),
        Column('cfop', Integer),
        Column('codigo_ean_comercial', Integer),
        Column('valor_unitario_cmc', Float),
        Column('valor_unitario_trib', Float),
        Column('unidade_trib', String)
    )
    #storage table
    storage = Table('storage', metadata,
        Column('id', String, primary_key=True),
        Column('created_date', String),
        Column('chave_nfe', String, ForeignKey("nfe.chave")),
        Column('download_status', Boolean, default=False, nullable=False),
        Column('download_date', String),
        Column('error', Boolean, default=False, nullable=False),
        Column('type_error', String)
    )
    # Create all tables
    metadata.create_all()

    for _t in metadata.tables:
        print(f"{_t} table was created successfully.")


conn.close()




