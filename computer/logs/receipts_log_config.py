import logging


form = logging.Formatter("%(asctime)s : %(levelname)-5.5s : %(message)s")
connection_logger = logging.getLogger('receipts_logger')



connFile = logging.FileHandler('logs/receipts_logs.log')


connFile.setFormatter(form)


connection_logger.addHandler(connFile)



consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(form)


connection_logger.addHandler(consoleHandler)


connection_logger.setLevel(logging.DEBUG)

