import selenium, os, logging, time, re, random
from selenium.common.exceptions import NoSuchElementException
from os.path import join, dirname
from selenium import webdriver
from dotenv import load_dotenv

from utils.customized_exception import *


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
    logger.setLevel(logging.INFO)

    LOGIN_MAIL = os.environ.get("MAIL_ADDRESS")
    LOGIN_PASSWORD = os.environ.get("PASSWORD")
    ITEM_URL = os.environ.get("ITEM_URL")
    # ITEM_URL = os.environ.get("TEST_URL")
    ACCEPT_SHOP = 'Amazon.com'
    LIMIT_MAX_VALUE = 570.0

    try:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1200x600')
        # driver = selenium.webdriver.Chrome('./chromedriver', options=options)
        driver = selenium.webdriver.Chrome('./chromedriver')
        driver.get(ITEM_URL)
    except Exception as e:
        logger.error(e)
        exit()

    time.sleep(2)

    while True:
        # if in stock?
        while True:
            try:
                amazon_info_table = driver.find_element_by_id('tabular-buybox-container').text
                match_result = re.search("Sold by\s+([a-zA-z.]+)", amazon_info_table).group(1)
                if ACCEPT_SHOP != match_result:
                    raise NotAmazonSellerError
                # add to cart
                driver.find_element_by_id('add-to-cart-button').click()
                break
                # buy now instead of adding to cart
                # driver.find_element_by_id('buy-now-button').click()
                # time.sleep(1)
                # place_order_btn = None
                # while place_order_btn is None:
                #     try:
                #         place_order_btn = driver.find_element_by_partial_link_text("turbo-checkout-pyo-button")
                #     except NoSuchElementException:
                #         logger.warning('Place Order Button Not Loaded Yet!')
                #         time.sleep(1)
                # place_order_btn.click()
                # break
            except NotAmazonSellerError:
                logger.warning("In Stock from other Sellers...")
                time.sleep(18 + random.randint(0, 13))
                driver.refresh()
            except Exception as e:
                logger.debug(e)
                logger.info("Add to Cart Button not found, might not in stock...")
                time.sleep(18 + random.randint(0, 13))
                driver.refresh()
        try:
            driver.find_element_by_id('siNoCoverage-announce').click()
        except:
            logger.info("try to get warranty decline btn failed, might warranty ad not shown.")

        driver.get('https://www.amazon.com/gp/cart/view.html?ref_=nav_cart')
        try:
            driver.find_element_by_name('proceedToRetailCheckout').click()
        except NoSuchElementException:
            logger.error("Not successfully added to cart... redo the process")
            continue
        try:
            driver.find_element_by_id('ap_email').send_keys(LOGIN_MAIL)
            driver.find_element_by_id('continue').click()
            driver.find_element_by_id('ap_password').send_keys(LOGIN_PASSWORD)
            driver.find_element_by_id('signInSubmit').click()
        except:
            logger.info('LOGIN PASS.')
            pass
        time.sleep(1)
        p = driver.find_element_by_css_selector('td.grand-total-price').text
        r = re.search("\$([0-9]+\.[0-9]+)", p)
        price_str = r.group(1) if r else ""
        if float(price_str) > LIMIT_MAX_VALUE:
            logger.warning("Price %s is too large", price_str)
            continue

        driver.find_element_by_name('placeYourOrder1').click()
        break

    logger.info('ALL DONE.')
