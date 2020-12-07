
def decline_warranty(cur_driver, logger):
    try:
        cur_driver.find_element_by_id('siNoCoverage-announce').click()
    except:
        logger.info("try to get warranty decline btn failed, might warranty ad not shown.")