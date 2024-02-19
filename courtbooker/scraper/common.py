import logging
from contextlib import contextmanager

from selenium import webdriver


@contextmanager
def get_webdriver() -> webdriver.Firefox:
    try:
        logging.debug("Initiliasing Firefox webdriver")
        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        yield driver
    except Exception as e:
        logging.exception(e)
    finally:
        logging.debug("Closing driver")
        driver.quit()
