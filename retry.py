import time
import math
import logging

# Retry decorator with exponential backoff
def retry(tries, delay=3, backoff=2, test_f=lambda x: bool(x)):
    '''Retries a function or method until function test_f on its return returns True.

    test_f initially returns true when the functions return value is truthy

    delay sets the initial delay in seconds, and backoff sets the factor by which
    the delay should lengthen after each failure. backoff must be greater than 1,
    or else it isn't really a backoff. tries must be at least 0, and delay
    greater than 0.'''

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    tries = math.floor(tries)
    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay # make mutable

            rv = f(*args, **kwargs) # first attempt
            logging.info('Try 1 complete')
            while mtries > 0:
                if test_f(rv) is True: # Done on success
                    return rv

                mtries -= 1            # consume an attempt
                time.sleep(mdelay) # wait...
                mdelay *= backoff    # make future wait longer

                rv = f(*args, **kwargs) # Try again
                logging.info('Try %d complete' % (tries - mtries + 1))

            return rv # Ran out of tries :-(

        return f_retry # true decorator -> decorated function
    return deco_retry    # @retry(arg[, ...]) -> true decorator
    