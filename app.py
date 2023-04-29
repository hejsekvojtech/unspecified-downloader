import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

import os, time, glob

songlist = "songlist.txt"
skipped = open('skipped.txt', 'w')
download_dir = os.path.join(os.path.expanduser("~"), "Downloads")

def getublock():
	s = Service(ChromeDriverManager().install())
	options = webdriver.ChromeOptions()
	options.add_argument('--lang=en')
	dir = os.getcwd()
	prefs = {'download.default_directory': dir}
	options.add_experimental_option('prefs', prefs)
	driver = webdriver.Chrome(service=s, chrome_options=options)
	driver.get(
		"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=112.0.5615.165&acceptformat=crx2,crx3&x=id%3Dcjpalhdlnbpafiamejdnhcphjbkeiagm%26uc")
	time.sleep(10)
	driver.close()

def downloadClick():
	dl_button = driver.find_element(By.XPATH, "//button[text()='Download']")
	driver.implicitly_wait(1.5)
	dl_button.click()

def selectQuality():
	driver.implicitly_wait(1.5)
	if quality == "1":
		ActionChains(driver).move_to_element(driver.find_element(By.ID, "mp3-128")).click().perform()
	elif quality == "2":
		ActionChains(driver).move_to_element(driver.find_element(By.ID, "mp3-320")).click().perform()
	elif quality == "3":
		ActionChains(driver).move_to_element(driver.find_element(By.ID, "flac")).click().perform()

def xpathExists(xpath):
	try:
		driver.find_element(By.XPATH, xpath)
	except NoSuchElementException:
		return False
	return True

def download():
	with open(songlist, encoding='utf-8') as fp:
		c = 1
		Lines = fp.readlines()
		for line in Lines:
			if line.strip() != '':
				time.sleep(1)
				driver.find_element(By.CLASS_NAME, 'input').clear()
				time.sleep(1)
				search_box = driver.find_element(By.CLASS_NAME, "input")
				search_button = driver.find_element(By.ID, "snd")
				query = line.strip()
				search_box.send_keys(query)
				time.sleep(1)
				search_button.click()
				time.sleep(2)

				if xpathExists("//span[text()='No results found.']"):
					print("Přeskakuji " + line.strip())
					skipped.write(line)
					continue

				downloadClick()
				selectQuality()
				if c == 1:
					driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				else:
					downloadClick()
				c += 1

				print("Stahuji " + line.strip())
				downloadStarted = False
				while not downloadStarted:
					time.sleep(0.5)
					for fname in os.listdir(download_dir):
						if ".crdownload" in fname:
							downloadStarted = True

				driver.execute_script("window.history.go(-1)")
				time.sleep(1)

		while True:
			downloadFinished = True
			for fname in os.listdir(download_dir):
				if ".crdownload" in fname:
					downloadFinished = False;
			if downloadFinished:
				print("Hotovo!")
				sys.exit(0)
			time.sleep(1)

def setupPage():
	driver.get("")
	driver.find_element(By.XPATH, ".//*[contains(text(), 'Search using our VPN')]").click()
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	download()
	time.sleep(60)


if __name__ == "__main__":
	print("Do what you want cause a pirate is free")
	adb = ""
	for file in glob.glob("*.crx"):
		adb = file
	time.sleep(2)
	if adb.endswith('.crx'):
		quality = input("1 for MP3 (128k), 2 MP3 (320k), 3 for FLAC: ")
		try:
			int(quality)
		except:
			sys.exit(1)
		
		options = webdriver.ChromeOptions()
		options.add_extension(adb)
		options.add_argument('--lang=en')
		s = Service(ChromeDriverManager().install())
		driver = webdriver.Chrome(service=s, options=options)
		setupPage()
		skipped.close()
	else:
		getublock()
