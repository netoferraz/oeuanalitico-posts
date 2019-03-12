from faker.providers import BaseProvider
import string
import random
import re
class InvoiceNumber(BaseProvider):
    """
    Provider for Eletronic Invoicing Number for Consumer (NFC-e)
    https://www.edicomgroup.com/en_US/news/5891-electronic-invoicing-in-brazil-nf-e-nfs-e-and-ct-e.html
    https://www.ibm.com/support/knowledgecenter/en/SSRJDU/einvoicing/SCN_eINV_Brazil_Definitions.htm
    """

    __provider__ = 'invoice'
    __lang__ = "pt_BR"
    uf_cod = {
        'RO' : 11,
        'AC' : 12,
        'AM' : 13,
        'RR' : 14,
        'PA' : 15,
        'AP' : 16,
        'TO' : 17,
        'MA' : 21,
        'PI' : 22,
        'CE' : 23,
        'RN' : 24,
        'PB' : 25,
        'PE' : 26,
        'AL' : 27,
        'SE' : 28,
        'BA' : 29,
        'MG' : 31,
        'ES' : 32,
        'RJ' : 33,
        'SP' : 35,
        'PR' : 41,
        'SC' : 42,
        'RS' : 43,
        'MS' : 50,
        'MT' : 51,
        'GO' : 52,
        'DF' : 53
    }

    def nfce(self, invoice_cod: str) -> str:
        if not isinstance(invoice_cod, str):
            raise TypeError("Convert invoice code to string type")
        else:
            validate_invoice = invoice_cod.isdigit()
            if validate_invoice:
                assert len(invoice_cod) == 44, "Invalid length of invoice code."
            else:
                pattern = r'[0-9]{2}-[0-9]{4}-[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}-[0-9]{3}.[0-9]{3}\.[0-9]{3}'\
                          r'-[0-9]{3}.[0-9]{3}\.[0-9]{3}-[0-9]{1}'
                regex = re.compile(pattern)
                check_pattern = regex.match(invoice_cod)
                if check_pattern:
                    pass
                else:
                    raise ValueError("The invoice code does not match the validation.")
        cod_digits = ''.join([random.choice(string.digits) for n in range(44)])
        nfce_cod = f"{cod_digits[:2]}-{cod_digits[2:6]}-{cod_digits[6:8]}.{cod_digits[8:11]}.{cod_digits[11:14]}/{cod_digits[14:18]}-{cod_digits[18:20]}"\
            f"-{cod_digits[20:22]}-{cod_digits[22:25]}-{cod_digits[25:28]}.{cod_digits[28:31]}.{cod_digits[31:34]}-{cod_digits[34:37]}.{cod_digits[37:40]}."\
            f"{cod_digits[40:43]}-{cod_digits[43]}"
        return nfce_cod