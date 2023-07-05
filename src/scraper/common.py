import logging
from contextlib import contextmanager

import geckodriver_autoinstaller
from selenium import webdriver


@contextmanager
def get_webdriver() -> webdriver.Firefox:
    try:
        logging.debug("Initiliasing Firefox webdriver")
        options = webdriver.FirefoxOptions()
        options.headless = True
        geckodriver_autoinstaller.install()
        driver = webdriver.Firefox(options=options)
        yield driver
    except Exception as e:
        logging.exception(e)
    finally:
        logging.debug("Closing driver")
        driver.quit()
