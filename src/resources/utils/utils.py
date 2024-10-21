# just for fun
import logging
def log_header(message: str):
    logging.info('*' * 60)
    logging.info('*' + ' ' * 58 + '*')
    logging.info('*' + ('>>> ' + message + ' <<<').center(58) + '*')
    logging.info('*' + ' ' * 58 + '*')
    logging.info('*' * 60)
