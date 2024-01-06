import cmakeutils.logging as logging
from os.path import join
from os import getcwd

def test_logging():
    logging.loginit(join(getcwd(), 'sample.log'))

    logging.log('This is a example log.')