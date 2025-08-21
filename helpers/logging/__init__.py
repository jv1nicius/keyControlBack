import traceback
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

fileHandler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

def log_exception(mensagem: str):
    formatted_tb = traceback.format_exc().replace('\n', '\n\t')
    logger.error(f"{mensagem}:\n\t{formatted_tb}")