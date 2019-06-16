#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import datetime
from tinydb import TinyDB, Query
import urllib3
import xlsxwriter
import re
import os
import time
import platform
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

urllib3.disable_warnings()

# Gets html code of website
# Returns html of website url
def make_soup(url):
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return BeautifulSoup(r.data,'lxml')

# Returns a list of urls for each station listed down on the mawn website
def get_station_urls():
    url = 'https://mawn.geo.msu.edu'
    html = make_soup(url)
    station_urls = re.findall('"/station.asp\?id=.+"',str(html))
    return station_urls

def get_hourly_urls():
    url = 'https://mawn.geo.msu.edu'
    station_urls = get_station_urls()
    c = 0
    for x in station_urls:
        x = x.replace('" shape="circle', '')
        station_urls[c] = url + x[1:-1] + "&rt=60"
        c = c + 1
    station_urls = list(dict.fromkeys(station_urls))
    return station_urls


def get_daily_urls():
    url = 'https://mawn.geo.msu.edu'
    station_urls = get_station_urls()
    c = 0
    for x in station_urls:
        x = x.replace('" shape="circle', '')
        station_urls[c] = url + x[1:-1] + "&rt=24"
        c = c + 1
    station_urls = list(dict.fromkeys(station_urls))
    return station_urls

# Scans and scours each station for soil moisture data from earliest to current
def get_csv(station_urls, feature, data_type, dir_name, dir_path):
    data_to_click = []
    data_p = []
    if feature == "precipitation":
        data_to_click = [
            'metric', 'csv', 'atmp_max', 'atmp_min', 'dwpt_max',
             'dwpt_min', 'srad', 'stmp_05cm_max', 'stmp_05cm_min',
             'soil0_min', 'soil0_max'
        ]
        if data_type != 'daily':
            data_p = ['pcpn']
    elif feature == "soil moisture":
        data_to_click = [
            'metric', 'csv', 'stmp_05cm', 'dwpt', 'atmp', 'pcpn',
            'relh', 'relh_45cm', 'relh_3m', 'srad', 'wdir', 'wspd',
            'leaf0', 'soil0', 'lws0_pwet'
        ]
        data_p = ['smst_05cm', 'smst_10cm', 'smst_20cm',
        'smst_50cm', 'mstr0', 'mstr1']

    data_to_click = data_to_click + data_p + ["Generate Report"]

    for url in station_urls:
        browser.get(url)
        print("RETRIEVING: Station " + url[40:43].upper())
        
        html = make_soup(url)
        date_string = re.findall('Dates Available.+through', str(html))
        date = {}
        date['smm'] = str(int(date_string[0][21:23]))
        date['sdd'] = str(int(date_string[0][24:26]))
        date['syy'] = str(int(date_string[0][27:31]))
        date['shh'] = str(int(date_string[0][32:34]))
        print("   FROM: " + date['smm'] + "/" + date['sdd']  + "/" + date['syy'] + "-" + date['shh'] + " to most recent")
        
        # Sets the record to earliest to current
        for de,el in date.items():
            try:
                template = "//select[@name='" + de + "']/option[@value='" + el + "']"
                browser.find_element_by_xpath(template).click()
                print("     SUCCESS: Setting " + de)
            except NoSuchElementException:
                print("     FAILURE: Setting " + de)

        plat = platform.system()
        
        # Checks only the soil moisture settings
        for d in data_to_click:
            try: 
                template = "//input[@value='" + d + "']"
                browser.find_element_by_xpath(template).click()
                print("     CLICKED: " + d)
            except NoSuchElementException:
                print("     SKIPPED: " + d)
        
        if plat == 'Windows':
            # Renames files with station names
            while not os.path.exists(dir_path + "\\" + dir_name + "\\mawn.csv"):
                time.sleep(1)
            os.rename(dir_path + "\\" + dir_name + "\\" + "mawn.csv", dir_path + "\\" + dir_name + "\\" + url[40:43] + ".csv")
        else:
            while not os.path.exists("./" + dir_name + "/mawn.csv"):
                time.sleep(1)
            os.rename("./" + dir_name + "/mawn.csv", dir_name + "/" + url[40:43] + ".csv")

def get_station_info(station_urls):
    header = ["Station Id", "Station Name", "City", "Latitude", "Longitude"]
    with open('mawn_stations_info.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(header)
        csvFile.close()
    
    with open('mawn_stations_info.csv', 'a', newline='') as csvFile:
        writer = csv.writer(csvFile)
        for url in station_urls:
            print(url)
            html = make_soup(url)
            station_info = re.findall('<td class="infotabledata" width="240">(.+)</td>', str(html))
            row = [station_info[1], station_info[0], station_info[4], station_info[6], station_info[7]]
            writer.writerow(row)
        csvFile.close()

def set_browser_settings (dir_name, dir_path):
    try:
        # Create target Directory
        os.mkdir(dir_name)
        print("Directory " , dir_name ,  " Created ") 
    except FileExistsError:
        print("Directory " , dir_name ,  " already exists")

    chromeOptions = webdriver.ChromeOptions()

    plat = platform.system()

    chromedriver = './chromedriverL'
    if plat == 'Windows':
        chromedriver = './chromedriver.exe'
        prefs = {"download.default_directory" : dir_path + "\\" + dir_name}
    else:
        chromedriver = './chromedriverL'
        prefs = {"download.default_directory" : "./" + dir_name}

    chromeOptions.add_experimental_option("prefs",prefs)

    browser = webdriver.Chrome(chromedriver, options=chromeOptions)
    return browser

if __name__== "__main__":

    data_type = input("What data type would you like? [hourly/daily]: ")
    feature = input("What variable would you like to scrape? [precipitation/soil moisture]: ")
    station_csv = input("Would you like a csv report of the station features? [y/n]: ")
    
    if data_type == "hourly":
        dir_name = 'Hourly' + feature + 'StationCSVs'
        dir_path = os.path.dirname(os.path.realpath(__file__))

        browser = set_browser_settings(dir_name, dir_path) 

        station_urls = get_hourly_urls()
        get_csv(station_urls, feature, data_type, dir_name, dir_path)
        
    elif data_type == "daily":
        dir_name = 'Daily' + feature +'StationCSVs'
        dir_path = os.path.dirname(os.path.realpath(__file__))

        browser = set_browser_settings(dir_name, dir_path) 

        station_urls = get_daily_urls()
        get_csv(station_urls, feature, data_type, dir_name, dir_path)

    if station_csv == "y":
        station_urls = get_hourly_urls()
        get_station_info(station_urls)
    browser.close()