import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)
actions = webdriver.ActionChains(driver)
delay = 5

site_url = 'http://127.0.0.1:8000'
driver.get(site_url)
print("----------------------------------------------------------------")
print("Test 1 - Open HomePage with Signup Form: ", end="")
if driver.find_element_by_name('Sign Up'):
    print('PASSED')
else: print('FAILED')
print("----------------------------------------------------------------")

driver.find_element_by_name('Login Button').click()
print("----------------------------------------------------------------")
print("Test 2 - Click Login Button to show Login Page: ", end="")
if driver.find_element_by_name('Log In'):
    print('PASSED')
else: print('FAILED')
print("----------------------------------------------------------------")
time.sleep(2)

# first log into website
username = driver.find_element_by_name('username'); username.clear()
password = driver.find_element_by_name('password'); password.clear()
username.send_keys('athu')
time.sleep(2)
password.send_keys('athu123')
time.sleep(2)
driver.find_element_by_name('Log In').click()
time.sleep(2)
print("----------------------------------------------------------------")
print("Test 3 - Logged in and to open User Homepage with Tree Count: ", end="")
if driver.find_element_by_id('welcome'):
    print('PASSED')
else: print('FAILED')
print("----------------------------------------------------------------")
time.sleep(30)

# plant a tree
original_tree_count = driver.find_element_by_id('tree_count').text
driver.find_element_by_name('Plant Tree').click()
time.sleep(40)
new_tree_count = driver.find_element_by_id('tree_count').text
print("----------------------------------------------------------------")
print("Test 4 - Tree Count changed after planting tree: ", end="")
if int(original_tree_count)+1 == int(new_tree_count):
    print('PASSED')
else: print('FAILED')
print("----------------------------------------------------------------")


# logout of website
driver.find_element_by_name('Logout Button').click()
print("----------------------------------------------------------------")
print("Test 5 - Logged out: ", end="")
if driver.find_element_by_name('Log In'):
    print('PASSED')
else: print('FAILED')
print("----------------------------------------------------------------")
time.sleep(2)

driver.close()