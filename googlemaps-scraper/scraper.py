import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# the category for which we seek reviews
# CATEGORY = "restaurants"

# the location
# LOCATION = "New York, USA"

# google's main URL
URL = "https://www.google.com/maps/search/japanese+restaurant/@1.3093935,103.7809834,14z"


browser = webdriver.Chrome()
browser.get(URL)

# Hello


# # deal with cookies
# cookies = browser.find_element_by_class_name('.QS5gu.sy4vM')
# cookies.click()

# # write what you're looking for
# search_field = browser.find_element_by_tag_name("textarea")
# search_field.send_keys(f"{CATEGORY} near {LOCATION}")

# # press enter
# search_field.submit()

# # change to English
# english_button = browser.find_element_by_xpath("//*[contains(text(),'Change to English')]")
# english_button.click()
# time.sleep(4)

# # click in the "Maps" HTML element
# maps_button = browser.find_element_by_class_name('.GKS7s')
# maps_button.click()
# time.sleep(4)



# def scroll_div(browser, css_selector):
#  """Scroll div function"""
#  div = browser.find_element(By.CSS_SELECTOR, css_selector)
#  browser.execute_script("arguments[0].scrollIntoView(false);", div)
#  time.sleep(2)

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
       time.sleep(4)

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
   # scroll_div(browser, ".m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd")
   

html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')

reviews = soup.find_all('div', {'class': 'section-review-content'})

for review in reviews:
   print(review.text)

browser.quit()
