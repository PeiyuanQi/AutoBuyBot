import selenium, os, logging, time, re, random, datetime
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

    SHOP_URL = os.environ.get("SHOP_URL")

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

    start_time = '08:00:00'
    start_time = '00:00:00'
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    while current_time < start_time:
        logger.info(current_time)
        time.sleep(1)
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

    logger.info("Start Bot now")

    # if in stock?
    while True:
        try:
            target_shoes = []
            target_xpath = "//li[@class='shoes']/a"
            # target_xpath = "//li[@class='tops/sweaters']/a"
            shoes = driver.find_elements_by_xpath(target_xpath)
            for each_shoe in shoes:
                href = each_shoe.get_attribute('href')
                logger.debug("Find shoe link: " + str(href))
                if str(href) != "https://www.supremenewyork.com/shop/shoes/m6sh4qcy1":
                    target_shoes.append(href)

            while len(target_shoes) == 0:
                time.sleep(random.randint(0,5))
                driver.get(SHOP_URL)
                time.sleep(1)
                shoes = driver.find_elements_by_xpath(target_xpath)
                for each_shoe in shoes:
                    href = each_shoe.get_attribute('href')
                    logger.debug("Find shoe link: " + str(href))
                    if str(href) != "https://www.supremenewyork.com/shop/shoes/m6sh4qcy1":
                        target_shoes.append(href)
            size1_flag = False
            for each_shoe in target_shoes:
                driver.get(each_shoe)
                # find if sold out
                try:
                    driver.find_element_by_xpath("//b[@class='button sold-out']")
                    continue
                except NoSuchElementException:
                    logger.info("Current Item Not Sold Out " + str(each_shoe))
                except Exception as e:
                    logger.debug(e)
                # try to select size
                try:
                    driver.find_element_by_xpath("//select[@name='s']/option[text()='8.5']").click()
                    # driver.find_element_by_xpath("//select[@name='s']/option[text()='Large']").click()
                    size1_flag = True
                except NoSuchElementException:
                    logger.error("Not find find_element_by_xpath(//select[@name='s']/option[text()='Large'])")
                except Exception as e:
                    logger.debug(e)
                if not size1_flag:
                    try:
                        driver.find_element_by_xpath("//select[@name='s']/option[text()='8']").click()
                    except NoSuchElementException:
                        logger.error("Not find driver.find_element_by_xpath(//select[@name='s']/option[text()='8']).click()")
                    except Exception as e:
                        logger.debug(e)
                # try to select color
                try:
                    driver.find_element_by_xpath("//button[@data-style-name='Hyper Blue']").click()
                    # driver.find_element_by_xpath("//button[@data-style-name='Dusty Royal']").click()
                except NoSuchElementException:
                    logger.error("Not find driver.find_element_by_xpath(//button[@data-style-name='Dusty Royal']).click()")
                except Exception as e:
                    logger.debug(e)
                # driver.find_element_by_xpath("//select[@name='s']/option[text()='8.5']").click()
                driver.find_element_by_xpath("//input[@value='add to cart']").click()
                time.sleep(0.1)
            driver.get("https://www.supremenewyork.com/checkout")
            try:
                driver.find_element_by_id('order_billing_name').send_keys(os.environ.get("BUYER_NAME"))
                driver.find_element_by_id('order_email').send_keys(os.environ.get("BUYER_EMAIL"))
                driver.find_element_by_id('order_tel').send_keys(os.environ.get("BUYER_PHONE"))
                driver.find_element_by_id('bo').send_keys(os.environ.get("BUYER_ADDR"))
                driver.find_element_by_id('order_billing_zip').send_keys(os.environ.get("BUYER_ZIPCODE"))
                driver.find_element_by_id('order_billing_city').send_keys(os.environ.get("BUYER_CITY"))
                driver.find_element_by_xpath("//select[@id='order_billing_state']/option[@value='CA']").click()
                driver.find_element_by_xpath("//select[@id='credit_card_type']/option[@value='credit card']").click()
                driver.find_element_by_id('rnsnckrn').send_keys(os.environ.get("CARD_NUM"))
                driver.find_element_by_xpath("//select[@id='credit_card_month']/option[@value='04']").click()
                driver.find_element_by_xpath("//select[@id='credit_card_year']/option[@value='2024']").click()
                driver.find_element_by_id('orcer').send_keys(os.environ.get("CARD_CVV"))
                driver.find_element_by_xpath("//label[@class='has-checkbox terms']").click()
                driver.find_element_by_xpath("//input[@value='process payment']").click()
            except Exception as e:
                logger.error(e)
                logger.error("Check out failed.")
            break

        except Exception as e:
            logger.debug(e)
            time.sleep(random.randint(0, 13))
            driver.refresh()

    logger.info('ALL DONE.')
