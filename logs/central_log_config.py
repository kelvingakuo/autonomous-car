import logging


form = logging.Formatter("%(asctime)s : %(levelname)-5.5s : %(message)s")
central_logger = logging.getLogger('central_logger')



centralFile = logging.FileHandler('logs/central_logs.log')




centralFile.setFormatter(form)

central_logger.addHandler(centralFile)



consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(form)


central_logger.addHandler(consoleHandler)


central_logger.setLevel(logging.DEBUG)

