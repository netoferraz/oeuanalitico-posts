import loggging

logger_get_html = loggging.getLogger("download_html")

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('logger_download_html.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.WARNING)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger_get_html.addHandler(c_handler)
logger_get_html.addHandler(f_handler)
