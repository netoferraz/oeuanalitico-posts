import logging
# logger para download dos arquivos html
logger_get_html = logging.getLogger("download_html")

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('./logs/logger_download_html.log')

# Create formatters and add it to handlers
c_format = logging.Formatter("%(asctime)s;%(name)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")
f_format = logging.Formatter("%(asctime)s;%(name)s;%(levelname)s;%(lineno)d;%(message)s", "%Y-%m-%d %H:%M:%S")
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger_get_html.addHandler(c_handler)
logger_get_html.addHandler(f_handler)

logger_get_html.setLevel(10)
logger_get_html.handlers[0].setLevel(10)
logger_get_html.handlers[1].setLevel(20)

# logger para parser dos arquivos html
logger_parser = logging.getLogger("parser_html")
# Create handlers
pstr_handler = logging.StreamHandler()
pfh_handler = logging.FileHandler('./logs/logger_parser_html.log')

pstr_format = logging.Formatter("%(asctime)s;%(name)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")
pfh_format = logging.Formatter("%(asctime)s;%(name)s;%(levelname)s;%(lineno)d;%(message)s", "%Y-%m-%d %H:%M:%S")
pstr_handler.setFormatter(pstr_format)
pfh_handler.setFormatter(pfh_format)

# Add handlers to the logger
logger_parser.addHandler(pstr_handler)
logger_parser.addHandler(pfh_handler)

logger_parser.setLevel(10)
logger_parser.handlers[0].setLevel(10)
logger_parser.handlers[1].setLevel(20)

# logger da conversão de pkl em csv

logger_tabular = logging.getLogger("parser_tocsv")
# Create handlers
tstr_handler = logging.StreamHandler()
tfh_handler = logging.FileHandler('./logs/logger_tabular.log')

tstr_format = logging.Formatter("%(asctime)s;%(name)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")
tfh_format = logging.Formatter("%(asctime)s;%(name)s;%(levelname)s;%(lineno)d;%(message)s", "%Y-%m-%d %H:%M:%S")
tstr_handler.setFormatter(tstr_format)
tfh_handler.setFormatter(tfh_format)

# Add handlers to the logger
logger_tabular.addHandler(tstr_handler)
logger_tabular.addHandler(tfh_handler)

logger_tabular.setLevel(10)
logger_tabular.handlers[0].setLevel(10)
logger_tabular.handlers[1].setLevel(20)
