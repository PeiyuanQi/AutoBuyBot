import selenium, os, logging, time
from os.path import join, dirname
from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv(verbose=True)
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))