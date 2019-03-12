from faker.providers import BaseProvider
import string
import random
class InvoiceNumber(BaseProvider):
    """
    Provider for Eletronic Invoicing Number for Consumer (NFC-e)
    https://www.edicomgroup.com/en_US/news/5891-electronic-invoicing-in-brazil-nf-e-nfs-e-and-ct-e.html
    https://www.ibm.com/support/knowledgecenter/en/SSRJDU/einvoicing/SCN_eINV_Brazil_Definitions.htm
    """

    __provider__ = 'invoice'
    __lang__ = "pt_BR"

    def nfce(self):
        cod_digits = ''.join([random.choice(string.digits) for n in range(44)])
        nfce_cod = f"{cod_digits[:2]}-{cod_digits[2:6]}-{cod_digits[6:8]}.{cod_digits[8:11]}.{cod_digits[11:14]}/{cod_digits[14:18]}-{cod_digits[18:20]}"\
            f"-{cod_digits[20:22]}-{cod_digits[22:25]}-{cod_digits[25:28]}.{cod_digits[28:31]}.{cod_digits[31:34]}-{cod_digits[34:37]}.{cod_digits[37:40]}."\
            f"{cod_digits[40:43]}-{cod_digits[43]}"
        return nfce_cod