import pandas as pd
import re
from bs4 import BeautifulSoup
# from datetime import date, timedelta, datetime
# from IPython.core.display import clear_output
# from random import randint
# from requests import get
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from time import time
start_time = time()

from warnings import warn

def scrap(year,transmission_type,make,car_type,fuel_type):
    options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-ssl-errors=yes')
    # options.add_argument('--ignore-certificate-errors')

    # driver = webdriver.Remote(command_executor='http://172.17.0.2:4444',options=options)
    driver = webdriver.Chrome()


    # make = "Nissan"
    # # model = "Altima"
    # year = "2013"
    # transmission_type = "automatic"
    # car_type = "sedan"
    # fuel_type = "gas"
    # mileage = "100000"


    url = ("https://www.carmax.com/cars/{}/{}/{}/{}?year={}".format(make,transmission_type,fuel_type,car_type,year))

    driver.get(url)
    sleep(3)
    action = ActionChains(driver)

    pageSource = driver.page_source
    lxml_soup = BeautifulSoup(pageSource, 'lxml')
    #     print(lxml_soup)

    car_container = lxml_soup.find_all('p', class_ = "price-miles-info kmx-typography--body-3")
    car_price = []
    for car in car_container:
        temp =  re.search("[0-9]*[,][0-9]*",(car.find('span', class_="price").text)).group(0)
        car_price.append(temp)

    # print("$",min(car_price))
    return min(car_price)

    driver.quit()