
from cerberus import Validator
nfe_schema_data = {
    'chave' : {
        'required' : True,
        'type' : 'string', 
        'minlength': 59, 
        'maxlength': 59 
        },
    'numero' : {
        'required' : True,
        'type' : 'integer',
    },
    'data' : {
        'required' : True,
        'regex' : r'[0-9]{2}/[0-9]{2}/[0-9]{4}',
        'type' : 'string',
    },
    'hora' :  {
        'required' : True,
        'regex' :r'[0-9]{2}:[0-9]{2}:[0-9]{2}',
        'type' : 'string',
    },
    'modelo' : {
        'required' : True,
        'type' : 'integer'
    },
    'serie' : {
        'required' : True,
        'type' : 'integer'
    },
    'valor' : {
        'required' : True,
        'type' : 'float'
    }
}
v_nfe = Validator(nfe_schema_data)

em_schema_data = {
    'razaoSocial' : {
        'required' : True,
        'type' : 'string'
    },
    
    'nome_fantasia' : {
        'type' : 'string'
    },
    
    'cnpj' : {
        'required' : True,
        'type' : 'string',
        'minlength': 18, 
        'maxlength': 18 
    },
    
    'endereco' : {
        'type' : 'string'
    },
    
    'bairro' : {
        'type' : 'string'
    },
    
    'cep' : {
        'type' : 'string',
        'regex' :r'[0-9]{5}-[0-9]{3}',       
    },
    
    'municipio' : {
        'type' : 'string',
    },
    
    'telefone' : {
        'type' : 'string'
    },

    'uf' : {
        'type' : 'string',
        'regex' : r'[A-Z]{2}',
        'required' : True,  
    },

    'pais' : {
        'type' : 'string'
    },

    'inscricao_estadual' : {
        'type' : 'string',
        'required' : True,
    },

    'inscricao_municipal' : {
        'type' : 'string'
    },

    'cnae_fiscal' : {
        'type' : 'string',
    }

}

v_em = Validator(em_schema_data)

dest_schema_data = {

    'razaoSocial' : {
        'type' : 'string'
    },
        
    'cpf' : {
        'type' : 'string',
        'maxlength': 14 
    },
    
    'endereco' : {
        'type' : 'string'
    },
    
    'bairro' : {
        'type' : 'string'
    },
    
    'cep' : {
        'type' : 'string',    
    },
    
    'municipio' : {
        'type' : 'string',
    },
    
    'telefone' : {
        'type' : 'string'
    },

    'uf' : {
        'type' : 'string',  
    },

    'pais' : {
        'type' : 'string'
    },

    'inscricao_estadual' : {
        'type' : 'string',
    },

    'email' : {
        'type' : 'string',
        'regex' : '.*@.*|',
        'default' : ""

    }
}

v_dest = Validator(dest_schema_data)

prod_schema_data = {
    'nome' : {
        'type' : 'string',
        'required' : True
    },

    'quantidade' : {
        'type' : 'float',
        'required' : True,
    },

    'unidade' : {
        'type' : 'string',
        'maxlength': 6
    },

    'valor' : {
        'type' : 'float'
    },

    'codigo_produto' : {
        'type' : 'string',
        'required' : True
    },
    
    'codigo_ncm' : {
        'type' : 'integer',
        'required' : True
    },

    'cfop' : {
        'type' : 'integer',
        'required' : True
    },

    'codigo_ean_comercial' : {
        'type' : 'integer'
    },

    'valor_unitario_cmc' : {
        'type' : 'float'
    },

    'valor_unitario_trib' : {
        'type' : 'float'
    },
    'unidade_trib' :{
        'type' : 'string'
    }
}

v_prod = Validator(prod_schema_data)