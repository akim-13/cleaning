import logging
import inspect

# Logging configuration
lvl = logging.DEBUG 
fmt = '%(lineno)s: [%(levelname)s] %(msg)s'
logging.basicConfig(level = lvl, format = fmt)

def d(log):
    frame = inspect.currentframe().f_back
    logging.getLogger().debug(log, stacklevel=2)

def i(log):
    frame = inspect.currentframe().f_back
    logging.getLogger().info(log, stacklevel=2)

def w(log):
    frame = inspect.currentframe().f_back
    logging.getLogger().warning(log, stacklevel=2)

def e(log):
    frame = inspect.currentframe().f_back
    logging.getLogger().error(log, stacklevel=2)
