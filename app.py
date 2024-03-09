import sys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException

import os
import time
import glob
import requests

songlist = "songlist.txt"
skipped = open("skipped.txt", "a")
download_dir = os.path.join(os.path.expanduser("~"), "Downloads")


def downloadUblock():
    print("Downloading uBlock Origin...")
    response = requests.get(
        "https://github.com/gorhill/uBlock/releases/download/1.55.0/uBlock0_1.55.0.firefox.signed.xpi"
    )
    with open(os.path.join(os.getcwd(), "uBlockOrigin.xpi"), "wb") as extension:
        extension.write(response.content)


def downloadClick():
    dl_button = driver.find_element(By.XPATH, "//button[text()='Download']")
    driver.implicitly_wait(1.5)
    dl_button.click()


def selectQuality():
    driver.implicitly_wait(1.5)
    if quality == "1":
        ActionChains(driver).move_to_element(
            driver.find_element(By.ID, "mp3-128")
        ).click().perform()
    elif quality == "2":
        ActionChains(driver).move_to_element(
            driver.find_element(By.ID, "mp3-320")
        ).click().perform()
    elif quality == "3":
        ActionChains(driver).move_to_element(
            driver.find_element(By.ID, "flac")
        ).click().perform()


def xpathExists(xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def fuckOff():
    driver.find_element(By.XPATH, "//p[text()='Consent']").click()


def download():
    with open(songlist, encoding="utf-8") as fp:
        c = 1
        Lines = fp.readlines()
        for line in Lines:
            if line.strip() != "":
                time.sleep(1)
                driver.find_element(By.CLASS_NAME, "input").clear()
                time.sleep(1)
                search_box = driver.find_element(By.CLASS_NAME, "input")
                search_button = driver.find_element(By.ID, "snd")
                query = line.strip()
                search_box.send_keys(query)
                time.sleep(1)
                search_button.click()

                # while not xpathExists("//span[text()='Close']"):
                #     time.sleep(1)
                #     if (xpathExists("//span[text()='Close']")):
                #         break

                # driver.find_element(By.XPATH, "//span[text()='Close']").click()

                # driver.execute_script("window.scrollBy(0, window.innerHeight / 4);")

                if xpathExists("//span[text()='No results found.']"):
                    print("Skipping " + line.strip())
                    skipped.write(line)
                    continue

                downloadClick()
                selectQuality()
                if c == 1:
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                else:
                    downloadClick()
                c += 1

                print("Downloading " + line.strip())
                downloadStarted = False
                while not downloadStarted:
                    time.sleep(0.5)
                    for fname in os.listdir(download_dir):
                        if ".part" in fname:
                            downloadStarted = True

                driver.execute_script("window.history.go(-1)")
                time.sleep(1)

        while True:
            downloadFinished = True
            for fname in os.listdir(download_dir):
                if ".part" in fname:
                    downloadFinished = False
            if downloadFinished:
                print("Done!")
                sys.exit(0)
            time.sleep(1)


def setupPage():
    driver.get("")
    driver.implicitly_wait(2)
    driver.refresh()
    time.sleep(1)
    # fuckOff()
    # driver.find_element(By.XPATH, ".//*[contains(text(), 'Search using our VPN')]").click()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    download()
    time.sleep(60)


if __name__ == "__main__":
    print("Do what you want cause a pirate is free")

    ublock = ""
    for file in glob.glob("*.xpi"):
        ublock = file

    if not ublock:
        downloadUblock()

    if ublock.endswith(".xpi"):
        quality = input("1 for MP3 (128k), 2 MP3 (320k), 3 for FLAC: ")
        try:
            int(quality)
        except:
            sys.exit(1)

        s = Service(executable_path="/usr/bin/geckodriver")
        options = webdriver.FirefoxOptions()
        options.set_preference("intl.accept_languages", "en")
        driver = webdriver.Firefox(service=s, options=options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        driver.install_addon(
            os.path.join(os.getcwd(), "uBlockOrigin.xpi"), temporary=True
        )
        driver.implicitly_wait(3)
        setupPage()
        skipped.close()
        driver.quit()
