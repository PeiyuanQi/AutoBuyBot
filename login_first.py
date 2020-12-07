import selenium, os, logging, time, re, random
from selenium.common.exceptions import NoSuchElementException
from os.path import join, dirname
from selenium import webdriver
from dotenv import load_dotenv

from utils.customized_exception import *
from utils.utils import *


if __name__ == '__main__':
    load_dotenv(verbose=True)
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    # Logging Config
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    LOGIN_MAIL = os.environ.get("MAIL_ADDRESS")
    LOGIN_PASSWORD = os.environ.get("PASSWORD")
    # ITEM_URL = os.environ.get("ITEM_URL")
    ITEM_URL = os.environ.get("TEST_URL")
    ACCEPT_SHOP = 'Amazon.com'
    LIMIT_MAX_VALUE = 570.0

    try:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1200x600')
        # driver = selenium.webdriver.Chrome('./chromedriver', options=options)
        driver = selenium.webdriver.Chrome('./chromedriver')
        driver.get("https://www.amazon.com")
    except Exception as e:
        logger.error(e)
        exit()

    time.sleep(2)

    # first try to login
    try:
        login_url = driver.find_element_by_xpath("//div[@id='nav-flyout-ya-signin']/a").get_attribute("href");
        driver.get(login_url)
        driver.find_element_by_id('ap_email').send_keys(LOGIN_MAIL)
        driver.find_element_by_id('continue').click()
        driver.find_element_by_id('ap_password').send_keys(LOGIN_PASSWORD)
        driver.find_element_by_id('signInSubmit').click()
        if "cvf/approval" in driver.current_url:
            time.sleep(5)
    except Exception as e:
        logger.error(e)
        logger.error('login failed')
        exit(1)

    driver.get(ITEM_URL)
    while True:
        # if in stock?
        while True:
            try:
                # buy now instead of adding to cart
                driver.find_element_by_id('buy-now-button').click()
                time.sleep(1)
                decline_warranty(driver, logger)
                place_order_btn = None
                while place_order_btn is None:
                    try:
                        place_order_btn = driver.find_element_by_partial_link_text("turbo-checkout-pyo-button")
                    except NoSuchElementException:
                        logger.warning('Place Order Button Not Loaded Yet!')
                        time.sleep(1)
                p = driver.find_element_by_id('turbo-checkout-panel-container').text
                logger.debug(p)
                r = re.search("\$([0-9]+\.[0-9]+)", p)
                price_str = r.group(1) if r else ""
                if float(price_str) > LIMIT_MAX_VALUE:
                    logger.warning("Price %s is too large", price_str)
                    continue
                break
                place_order_btn.click()
                break
            except NotAmazonSellerError:
                logger.warning("In Stock from other Sellers...")
                time.sleep(18 + random.randint(0, 13))
                driver.refresh()
            except Exception as e:
                logger.debug(e)
                logger.info("Add to Cart Button not found, might not in stock...")
                time.sleep(18 + random.randint(0, 13))
                driver.refresh()

    logger.info('ALL DONE.')
