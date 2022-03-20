from sys import platform
import bs4
from bs4 import NavigableString
try:
    from urllib import quote, quote_plus, unquote  # Python 2.X
except ImportError:
    from urllib.parse import quote, quote_plus, unquote  # Python 3+

#import urllib2
import requests, base64
##import pandas as pd
import math, numbers
import datetime
import time
##from pandas import DataFrame
from collections import OrderedDict
import sortedcontainers
##import cPickle
import json
from random import randint, uniform, shuffle
import os, sys, getopt, zipfile, re, glob
# import boto3
# import boto.utils
from difflib import SequenceMatcher
#from html.parser import HTMLParser
#import html.parser
import unicodedata
import string

import certifi
import urllib3
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
urllib3.disable_warnings()


#import concurrent, threading
#import tornado.ioloop
# NOT using this threading capability right now with python 2.7 - recruiter contact details crawl removed from code for now
# from concurrent.futures import ThreadPoolExecutor

# executor = concurrent.futures.ThreadPoolExecutor(5)
# class _LocalIOLoop(threading.local):
#     def __init__(self):
#         self.value = tornado.ioloop.IOLoop()

# local_ioloop = _LocalIOLoop()



allAgentChoices = [
    'Mozilla/5.0 (iPhone; U; CPU iPhone OS)',
    'Mozilla/5.0 (Linux; Android 5.0; SM-G920A)'
    'Mozilla/5.0 (iPhone; U; CPU iPhone OS)',
    'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P)'
]

uberEatsPhotoCache = {}
failedUrls = []

#IMPORTANT NOTE:  to attempt to crawl alot faster play with these parameters to increase/decreas speed of crawl
pictDelayScaleFactor = 1.25
restDelayScaleFactor = 1.25
pictDelayMin = round(8 * pictDelayScaleFactor, 0)
pictDelayMax = round(15 * pictDelayScaleFactor, 0)
restDelayMin = round(45 * restDelayScaleFactor, 0)
restDelayMax = round(60 * restDelayScaleFactor, 0)



valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255

def clean_filename(filename, whitelist=valid_filename_chars, replace=' '):
    # replace spaces
    for r in replace:
        filename = filename.replace(r,'_')

    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename)>char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit]



def runRequestsWithTimeout(getRequestUrl, headers, timeout):
    timeout = timeout
    body = []
    errVal = 0
    blockSize = 4 * 1024  #4K

    start = time.time()
    #NOTE:  this is for python 3
    r = requests.get(getRequestUrl, headers=headers, verify=False, stream=True, timeout=timeout)

    ##NOTE calling this way is for python 2
    ##r = http.request('GET', getRequestUrl, headers=headers, timeout=timeout)

    #print("r: " + str(r))
    #print("r.status: " + str(r.status))
    #print("r.data: " + str(r.data))

    for chunk in r.iter_content(blockSize): # Adjust this value to provide more or less granularity.
        body.append(chunk)
        if time.time() > (start + timeout):
            errVal = -1
            break # You can set an error value here as well if you want.

    content = b''.join(body)
    return content, errVal



#useful when we need to use selenium to crawl something that might have lazy loading of images (for example uber eats)
def returnSoupFromSelenium(url):

    from selenium.webdriver.chrome.options import Options
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    print('Here fetching soup')

    # options = Options()
    # options.headless = True
    
    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.binary_location = ''
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument('--ignore-certificate-errors')

    if platform == "linux":
        DRIVER_PATH = '/bin/chromedriver'
    else:
        DRIVER_PATH = 'C:/Users/monyei/bin/chromedriver.exe'
    driver = webdriver.Chrome(options=chrome_options, executable_path=DRIVER_PATH)

    try:
        driver.get(url)
    except Exception as e:
        print("Error trying to get url: ", str(e))
        return -1

    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    SCROLL_PAUSE_TIME = 0.5
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # operating_hrsDiv = driver.find_element(By.XPATH,"/html/body/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[1]/section[2]/div[2]/div[2]")
    # operating_hrsDiv = driver.find_elements (By.XPATH ("//*[text()='Tue']"));
    operating_hrsDiv = driver.find_element(By.XPATH, "/html/body/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[1]/section[2]/div[2]/div[2]/div/div/table")
    #get list size with len
    s = len(operating_hrsDiv)
    print (s)
    # operating_day = operating_hrsDiv.find_elements(By.TAG_NAME, "th")
    # for col in operating_day:
    #     operating_time = operating_hrsDiv.find_elements(By.TAG_NAME, "td")
    #     for row in operating_time:
    #         print( col.text, ':', row.text)
    
    # print("operating_hrsDiv: " + operating_hrsDiv.text)
    # loop through different divs for operating hours
    # find elements by tag name for each hrsDiv
    # hrsTag = operating_hrsDiv.find_elements(By.TAG_NAME, "th")
    # loop through each hrsTag
    # for tag in hrsTag:
        # day = tag.text
        # print(day)
        # day = hrsTag[0].text
        # find elements by class name for each hrsDiv
        # hrsClass = hrsDiv.find_elements(By.TAG_NAME, "li")
        # time = hrsClass[0].text
        # print("Day: " + day)
        # print("Time: " + time)
        # print("hrsDiv: " + str(hrsDiv))

    # print("operating_hrsDiv: " + operating_hrsDiv)
    # operating_hrsList = operating_hrsDiv.find_elements(By.TAG_NAME, 'li')
    # loop through operating hours listed on page
    # for operating_hrs in operating_hrsList:
    #     print("Here fetch operating hrs")
    #     operating_hrs_text = operating_hrs.text
    #     print(operating_hrs_text)
    
        
        # print(driver.page_source)

    soup = bs4.BeautifulSoup(driver.page_source, "lxml")

    driver.quit()
    return soup

def returnSoupFromSelenium2(url):
    from selenium.webdriver.chrome.options import Options
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.binary_location = ''
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument('--ignore-certificate-errors')

    if platform == "linux":
        DRIVER_PATH = '/bin/chromedriver'
    else:
        DRIVER_PATH = 'C:/Users/monyei/bin/chromedriver.exe'
    driver = webdriver.Chrome(options=chrome_options, executable_path=DRIVER_PATH)


    try:
        driver.get(url)
    except Exception as e:
        print("Error trying to get url: ", str(e))
        return -1

    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    SCROLL_PAUSE_TIME = 0.5
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    ##print(driver.page_source)

    soup = bs4.BeautifulSoup(driver.page_source, "lxml")

    driver.quit()
    return soup

#todo:  rewrite this code to call new API updateRestaurantHours() and pull in supporting files for auth etc
def sendUpdateForThisOrder(order):

    global nodeServerHostname
    global nodeServerPort
    global nodeServerAdminEmail
    global nodeServerAdminPassword
    global signinToken
    global userId

    if len(signinToken) == 0:
        #todo: first sign in to get token then do next step
        posturl = "https://%s/api/signin" % (nodeServerHostname)
        print("sendOrderingResults - posturl: " + str(posturl))

        headersObj = {}
        headersObj['Content-Type'] = 'application/json'
        bodyObj = {}
        bodyObj['email'] = nodeServerAdminEmail
        bodyObj['password'] = nodeServerAdminPassword

        response = requests.post(str(posturl), json.dumps(bodyObj),
                                headers=headersObj)
        print("response: " + str(response))
        print("response.content: " + str(response.content))

        responseData = response.json()
        if response.status_code == 200:
            signinToken = responseData['token']
            userId = responseData['user']['_id']
            print("got return code status of 200, saved token and userid")
        else:
            errMsg = 'Failed to sign in status code %s - bodyObj %s' % (str(response.status_code), str(bodyObj))
            print(errMsg)
            logger.error(errMsg)

    if len(signinToken) > 0:
        print("order: " + str(order))

        deliveryId = order['deliveryId']
        posturl = "https://%s/api/delivery/update/ordered/%s/%s" % (nodeServerHostname, userId, deliveryId)

        print("updating order - posturl: " + str(posturl))

        headersObj = {}
        headersObj['Content-Type'] = 'application/json'
        #bodyObj = order

        response = requests.post(str(posturl), json.dumps(order),
                                headers=headersObj)
        print("response: " + str(response))
        print("response.content: " + str(response.content))
        if response.status_code != 200:
            errMsg = 'Failed to update order object %s - json.dumps(order) %s' % (str(posturl), str(json.dumps(order)))
            print(errMsg)
            logger.error(errMsg)
    else:
        errMsg = 'UNABLE TO DO UPDATE due to bad signinToken %s' % (str(signinToken))
        print(errMsg)
        logger.error(errMsg)



def yelp_times(url):

    times = {}
    soup = returnSoupFromSelenium(url)
    # print(soup)

    if soup != -1:
        for row in soup.find('table', class_=' table-row__09f24__YAU9e').find_all('tr'):

            detes = row.find_all('p')
            mapper = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}
            if not detes:
                continue
            times[mapper[detes[0].text]] = [ele.text.lower().replace(' ', '').replace('-', ' - ').replace('(Nextday)', ' (Next day)') for ele in detes[1:]]
        print(times)

    else:
        print("failed to get open and close times from yelp")
    return times


def getData(jsonSourcePath, jsonOutPath):


    urlsDict = {}
    if jsonSourcePath != None:
        print("reading from file...")
        with open(jsonSourcePath,'rb') as openedfile:
            lines = openedfile.read()
            urlsDict = json.loads(lines.decode("utf-8"))
            print("urlsDict: " + str(urlsDict))
    else:
        print("exiting because no source url file passed to this...")
        exit(-1)


    topLevelDict = {}
    restaurantList = []

    for restDict in urlsDict['urls']:

        #print(restDict)


        yelpEatsUrl = restDict['yelp']
        if len(yelpEatsUrl) == 0:
            print("skipping...we require the restaurant to be listed on doordash for now..")
            continue

        soup = returnSoupFromSelenium(yelpEatsUrl)
        # soup = yelp_times(yelpEatsUrl)
        #todo:  call yelpTimes() and save result in restDict
        #       then save into restDict and later it will save rest dict into .out file 
        #       step 2: or send back to Node server
        #
        
        #slow down the crawl on purpose
        # time.sleep(uniform(45, 60))



    #print(restaurantDict)
    if jsonOutPath != None:
        print("writing to file...")
        with open(jsonOutPath, 'w') as f:
            json.dump(topLevelDict, f)
            f.write('\n')




def main(argv):

    global failedUrls

    dateStarted = datetime.datetime.now()

    #todo:  add in cmd line args later if needed
    getData("./sourceUrls2.json", "./yelpOut.json")

    dateFinished = datetime.datetime.now()
    print("dateStarted: " + str(dateStarted))
    print("dateFinished: " + str(dateFinished))

    print("failedUrls: " + str(failedUrls))



if ( __name__ == "__main__") :
    main(sys.argv[1:])