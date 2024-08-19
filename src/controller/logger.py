import os
import sys
import logging
import datetime

class LoggerWriter:
    """
    Classe para redirecionar a saída padrão e de erro para o logger.
    """
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message.strip():
            self.level(message.strip())

    def flush(self):
        pass  

class Logger:
    """
    Classe responsável por configurar e gerenciar o registro de logs.
    """
    def __init__(self, name, date=datetime.datetime.now().strftime("%d_%m_%Y")):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.log_dir = os.path.join(os.getcwd(), 'src\\logs')
        self.log_file = os.path.join(self.log_dir, f'{name}_{date}.txt') 
        self._create_log_directory()
        self._add_console_handler()
        self._add_file_handler()
        sys.stdout = LoggerWriter(self.info)
        sys.stderr = LoggerWriter(self.error)

    def _create_log_directory(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _add_file_handler(self):
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def _add_console_handler(self):
       console_handler = logging.StreamHandler()
       console_handler.setLevel(logging.INFO)
       formatter = logging.Formatter('%(levelname)s - %(message)s')
       console_handler.setFormatter(formatter)
       self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)