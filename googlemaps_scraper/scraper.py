import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# list of planning areas in Singapore from https://en.wikipedia.org/wiki/Planning_Areas_of_Singapore
LIST_OF_PLANNING_AREAS = [
    "Ang Mo Kio",
    "Bedok",
    "Bishan",
    "Bukit Batok",
    "Bukit Merah",
    "Bukit Panjang",
    "Bukit Timah",
    "Central Water Catchment",
    "Changi",
    "Choa Chu Kang",
    "Clementi",
    "Downtown Core",
    "Geylang",
    "Hougang",
    "Jurong East",
    "Jurong West",
    "Kallang",
    "Lim Chu Kang",
    "Mandai",
    "Marina East",
    "Marina South",
    "Marine Parade",
    "Museum",
    "Newton",
    "Novena",
    "Outram",
    "Pasir Ris",
    "Paya Lebar",
    "Pioneer",
    "Punggol",
    "Queenstown",
    "River Valley",
    "Rochor",
    "Seletar",
    "Sembawang",
    "Sengkang",
    "Serangoon",
    "Simpang",
    "Singapore River",
    "Southern Islands",
    "Sungei Kadut",
    "Tampines",
    "Tanglin",
    "Tengah",
    "Toa Payoh",
    "Tuas",
    "Western Islands",
    "Western Water Catchment",
    "Woodlands",
    "Yishun"
]

# google's main URL
# URL = "https://www.google.com/maps/search/japanese+restaurants/@1.3143869,103.78828,17z"

URL = "https://www.google.com/maps/search/"

TARGET = "japanese+restaurants"

browser = webdriver.Chrome()


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
       last_category_location = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, f"""//*[@aria-label="{last_category_in_page}"]""")))
       
       # Scroll to the last category
       browser.execute_script("arguments[0].scrollIntoView();", last_category_location)
       
       # Wait for the page to load more content
       time.sleep(0.1)

# # Function to iterate through elements, click, and scroll if needed
# def iterate_and_scroll(elements):
#     print("Total elements found:", len(elements))
    
#     for index, element in enumerate(elements):
#         element.click()
#         print(f"Element {index + 1} clicked")
#         # Add delay to allow page to load
#         time.sleep(1)
        
#         # Check if it's the last element
#         if index == len(elements) - 1:
#             # Scroll and load more elements
#             scroll_and_load(browser, '.hfpxzc')
            
#             # Update the elements list with newly loaded elements
#             new_elements = elements = browser.find_elements(By.CLASS_NAME, "hfpxzc")
#             elements.extend(new_elements)
            
#             print(f"Total elements after scrolling: {len(elements)}")

def find_target_in_area(url):
    browser.get(url)
    print(url)
    # get all elements with class "hfpxzc"
    elements = browser.find_elements(By.CLASS_NAME, "hfpxzc")

    # iterate_and_scroll(elements)

    noMoreResults = False
    iterator = 0

    while True:
        print("Total elements found:", len(elements))
        current_element = elements[iterator]
        browser.execute_script("arguments[0].scrollIntoView();", current_element)
        current_element.click()
        print("element clicked")
        # add delay to allow page to load
        time.sleep(0.1)
        scroll_and_load(browser, '.hfpxzc')

        # more elements are loaded after scrolling, add the new elements to the list, but only if they are not already in the list
        new_elements = browser.find_elements(By.CLASS_NAME, "hfpxzc")
        for new_element in new_elements:
            if new_element not in elements:
                elements.append(new_element)
        
        # Check if the "You've reached the end of the list." message is present
        end_of_list_element = browser.find_elements(By.CLASS_NAME, 'HlvSq')
        if end_of_list_element:
            print("You've reached the end of the list.")
            noMoreResults = True
        
        iterator += 1
        
        if noMoreResults and iterator == len(new_elements):
            print("Finished scraping all elements")
            break
            

# for each planning area, get the url and find the target
for planning_area in LIST_OF_PLANNING_AREAS:
    url = URL + TARGET + "+in+" + planning_area
    find_target_in_area(url)


#     html = browser.page_source
#     soup = BeautifulSoup(html, 'html.parser')

#     reviews = soup.find_all('div', {'class': 'section-review-content'})

# for review in reviews:
#    print(review.text)

browser.quit()
