"""Decorators (CONCEPT: functions that wrap other functions)."""
import functools
import time

from invoiceguard.logger_setup import get_logger

log = get_logger()


def timed(func):
    """Log how long a function took."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        log.info("%s finished in %.3f sec", func.__name__, time.time() - start)
        return result
    return wrapper


def retry(times=3, delay=0.1, exceptions=(Exception,)):
    """Try again if the function fails. A decorator that takes arguments."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    log.warning("%s failed (attempt %d/%d): %s",
                                func.__name__, attempt, times, error)
                    if attempt == times:
                        raise                    # give up, pass the error on
                    time.sleep(delay)
        return wrapper
    return decorator
