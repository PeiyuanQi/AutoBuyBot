import selenium, os, logging, time, re, random
from selenium.common.exceptions import NoSuchElementException
from os.path import join, dirname
from selenium import webdriver
from dotenv import load_dotenv

from utils.customized_exception import *
from utils.utils import decline_warranty

log_level = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO}

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
    logger.setLevel(log_level[os.environ.get("LOG_LEVEL")])

    # ITEM_URL = os.environ.get("ITEM_URL")
    SHOP_URL = os.environ.get("SHOP_URL")
    LIMIT_MAX_VALUE = 1000.0

    try:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1200x600')
        # driver = selenium.webdriver.Chrome('./chromedriver', options=options)
        driver = selenium.webdriver.Chrome('../drivers/chromedriver')
        driver.get(SHOP_URL)
    except Exception as e:
        logger.error(e)
        exit()

    time.sleep(2)

    while True:
        # if in stock?
        while True:
            try:
                target_shoes = []
                # shoes = driver.find_elements_by_xpath("//li[@class='shoes']/a")
                shoes = driver.find_elements_by_xpath("//li[@class='tops/sweaters']/a")
                for each_shoe in shoes:
                    href = each_shoe.get_attribute('href')
                    logger.debug("Find shoe link: " + str(href))
                    if str(href) != "https://www.supremenewyork.com/shop/shoes/m6sh4qcy1":
                        target_shoes.append(href)

                for each_shoe in target_shoes:
                    driver.get(each_shoe)
                    try:
                        driver.find_element_by_xpath("//select[@name='s']/option[text()='Large']").click()
                    except NoSuchElementException:
                        logger.error("Not find find_element_by_xpath(//select[@name='s']/option[text()='Large'])")
                        continue
                    except Exception as e:
                        logger.debug(e)
                        continue
                    # driver.find_element_by_xpath("//select[@name='s']/option[text()='8.5']").click()
                    driver.find_element_by_xpath("//input[@value='add to cart']").click()
                    time.sleep(0.1)
                    print("breaking")
                    break
                driver.get("https://www.supremenewyork.com/checkout")
                driver.find_element_by_id('order_billing_name').send_keys(os.environ.get("BUYER_NAME"))
                exit()

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
        time.sleep(1)
        decline_warranty(driver, logger)

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
            logger.error('login failed')
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
