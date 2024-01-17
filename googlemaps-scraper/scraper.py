import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# google's main URL
URL = "https://www.google.com/maps/search/japanese+restaurant/@1.3093935,103.7809834,14z"


browser = webdriver.Chrome()
browser.get(URL)


def scroll_and_load(browser, css_selector):
   """Scroll div function"""
   for _ in range(2):
       # Get the HTML of the body
       html = browser.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML')
       
       # Create a BeautifulSoup object
       soup = BeautifulSoup(html, 'html.parser')
       
       # Select items
       categories = soup.select(css_selector)
       
       # Get the label of the last category
       last_category_in_page = categories[-1].get('aria-label')
       
       # Find the location of the last category
       last_category_location = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, f"//*[@aria-label='{last_category_in_page}']")))
       
       # Scroll to the last category
       browser.execute_script("arguments[0].scrollIntoView();", last_category_location)
       
       # Wait for the page to load more content
       time.sleep(1)

# get all elements with class "hfpxzc"
elements = browser.find_elements(By.CLASS_NAME, "hfpxzc")

# iterate over the elements and click on each one
print("elements found:", len(elements))
for element in elements:
   element.click()
   print("element clicked")
   # add delay to allow page to load
   time.sleep(1)
   scroll_and_load(browser, '.hfpxzc')
   

html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')

reviews = soup.find_all('div', {'class': 'section-review-content'})

for review in reviews:
   print(review.text)

browser.quit()
