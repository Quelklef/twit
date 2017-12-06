import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('log.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
