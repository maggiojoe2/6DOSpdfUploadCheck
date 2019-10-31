#!/usr/bin/env python3.6.3
"""Check for uploaded pdf files for 6DOS accounts listed by the csv provided by the user.

Outputs:
    missingUploads.csv
    RuntimeLogs.log
"""

from csv import reader, writer, QUOTE_MINIMAL
from os import access
from sys import stdout
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from time import time, strftime, gmtime
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from webdrivermanager import ChromeDriverManager
import logging

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format('.', 'RuntimeLogs'))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

rootLogger.setLevel(logging.INFO)


def main():
    """Check for uploaded pdf files for 6DOS accounts listed by the csv provided by the user."""
    # Get filename and test if it is valid
    root = Tk()
    root.withdraw()
    fileName = askopenfilename()
    root.update()
    try:
        testFile = open(fileName, "r")
    except FileNotFoundError:
        rootLogger.error(fileName + " does not exist!")
        quit()

    # Save start time
    startTime = time()

    rootLogger.info("Starting Browser...")

    # Run Chrome headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("log-level=3")

    # Start browser driver
    try:
        browser = webdriver.Chrome(chrome_options=chrome_options, executable_path='./chromedriver.exe')
    except WebDriverException:
        gdd = ChromeDriverManager(link_path='.')
        gdd.download_and_install()
        browser = webdriver.Chrome()

    # Login
    rootLogger.info("Logging in...")
    login(browser)

    # Check pages
    rootLogger.info("Checking pages...")
    check_pages(browser, testFile, startTime)

    elapsedTime = time() - startTime
    strftime("Total Time: %M minutes %S seconds", gmtime(elapsedTime))


def check_experience(browser):
    """Check for work experience on page.

    Args:
        browser (WebDriver): The web driver for selenium

    Returns:
        bool: true if work experience is found. False if there is no experience.

    """
    try:
        browser.find_element_by_xpath("//td[contains(text(), 'No Experience Found')]")
    except NoSuchElementException:
        return True

    return False



def check_pages(browser, testFile, startTime):
    """Check each page for Work Experience which is being used to see if the PDF has been uploaded

    Args:
        browser (WebDriver): The web driver for selenium
        testFile (file): The open test file

    """
    numMissing = 0
    numChecked = 0
    with open('missingUploads.csv', mode='w') as outFile:
        read = reader(testFile)
        csvWriter = writer(outFile, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
        for i, row in enumerate(read):
            if i is 0:
                continue
            url = row[6]
            browser.get(url)
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Work Experience')]")))

            if not check_experience(browser):
                rootLogger.info("Missing Upload For: " + url)
                row.append("Missing Upload")
                numMissing+=1
                csvWriter.writerow(row)

            numChecked+=1
            print("Checked Pages: ", numChecked, "Missing Pages: ", numMissing, "Elapsed Time: ", int(time() - startTime), "seconds", end='\r')
            stdout.flush()

    rootLogger.info("Finished checking urls.\nNumber of missing files: %d\nTotal elapsed time: %d" % (numMissing, int(time() - startTime)))




def login(browser):
    """Log into 6DOS.

    Args:
        browser (WebDriver): The web driver for selenium

    """
    url = "https://app.6dos.co"
    browser.get(url)

    username = browser.find_element_by_css_selector("input.form-control[formcontrolname='username']")
    password = browser.find_element_by_css_selector("input.form-control[formcontrolname='password']")
    username.send_keys("")
    password.send_keys("")

    submitButton = browser.find_element_by_css_selector("button.btn-primary-custom.roundedBtn")

    submitButton.click()

    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "app-header")))
    return

if __name__== "__main__":
  main()
