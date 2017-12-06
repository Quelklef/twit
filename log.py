import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('log.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


# Annotation
def watch_time(threhshold):
    """ Returns an annotation which will log a warning if function call
    takes longer than `threhshold` seconds."""
    def annot(func):
        def wrapper(*args, **kwargs):
            start = time.time()

            val = func(*args, **kwargs)

            elapsed = time.time() - start
            if elapsed > threhshold:
                logger.warning(f"{func.__name__} took {elapsed}s to run.")

            return val
        return wrapper
    return annot