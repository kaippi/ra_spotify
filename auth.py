import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from urllib.parse import urlparse

ignored_exceptions=(StaleElementReferenceException,NoSuchElementException)

def wdwfind(path):
    return WebDriverWait(driver, 15,ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((By.XPATH,(path))))

driver = webdriver.Chrome()
driver.get('https://accounts.spotify.com/authorize?response_type=code&client_id=9c2c599cacf14ee29ab7e9e22aeea7e8&scope=playlist-modify-public&redirect_uri=http://127.0.0.1:8080/')
time.sleep(1)
driver.find_element_by_id('login-username').send_keys("ochokocho@gmail.com")
driver.find_element_by_id('login-password').send_keys("fizzfuzz")
driver.find_element_by_id('login-button').click()
time.sleep(1)
cur_url = urlparse(driver.current_url)
print(cur_url.query[5:])