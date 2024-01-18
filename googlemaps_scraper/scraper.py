import csv
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import time


# list of planning areas in Singapore from https://en.wikipedia.org/wiki/Planning_Areas_of_Singapore
LIST_OF_PLANNING_AREAS = [
    "Ang Mo Kio",
    "Bedok",
    # "Bishan",
    # "Bukit Batok",
    # "Bukit Merah",
    # "Bukit Panjang",
    # "Bukit Timah",
    # "Central Water Catchment",
    # "Changi",
    # "Choa Chu Kang",
    # "Clementi",
    # "Downtown Core",
    # "Geylang",
    # "Hougang",
    # "Jurong East",
    # "Jurong West",
    # "Kallang",
    # "Lim Chu Kang",
    # "Mandai",
    # "Marina East",
    # "Marina South",
    # "Marine Parade",
    # "Museum",
    # "Newton",
    # "Novena",
    # "Outram",
    # "Pasir Ris",
    # "Paya Lebar",
    # "Pioneer",
    # "Punggol",
    # "Queenstown",
    # "River Valley",
    # "Rochor",
    # "Seletar",
    # "Sembawang",
    # "Sengkang",
    # "Serangoon",
    # "Simpang",
    # "Singapore River",
    # "Southern Islands",
    # "Sungei Kadut",
    # "Tampines",
    # "Tanglin",
    # "Tengah",
    # "Toa Payoh",
    # "Tuas",
    # "Western Islands",
    # "Western Water Catchment",
    # "Woodlands",
    # "Yishun"
]

# google's main URL
# URL = "https://www.google.com/maps/search/japanese+restaurants/@1.3143869,103.78828,17z"

URL = "https://www.google.com/maps/search/"

TARGET = "japanese+restaurants"

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless=new")

browser = webdriver.Chrome(options=chrome_options)

# Create a CSV file and write the header
csv_file = open('scraped_data_' + TARGET.replace("+", "_") + '.csv', 'w', encoding='utf-8', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Planning Area', 'Name', 'Star Rating', 'Reviews', 'Category', 'Price Label', 'Metadata'])

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
       
def find_target_in_area(url, planning_area):
    url = url + planning_area
    browser.get(url)
    print(url)
    # get all elements with class "hfpxzc"
    elements = browser.find_elements(By.CLASS_NAME, "hfpxzc")

    # iterate_and_scroll(elements)

    noMoreResults = False
    iterator = 0

    while True:
        # initialise variables
        location_name, star_rating, reviews_text, category_name, price_rating = "", "", "", "", ""


        print("Total elements found:", len(elements))
        current_element = elements[iterator]
        browser.execute_script("arguments[0].scrollIntoView();", current_element)
        current_element.click()
        print("element clicked")
        # # add delay to allow page to load
        # time.sleep(1)
        print("current element:", iterator + 1)
        # find the aria-label of the element
        location_name = current_element.get_attribute("aria-label")
        print("location_name:", location_name)

        try:
            # Find the star rating element within the main content div
            review_main_content_div = WebDriverWait(browser, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.F7nice')))

            # Extract the text content of the span containing the star rating
            star_rating = review_main_content_div.find_element(By.TAG_NAME, 'span').text

            # Print the star rating
            print("star_rating:", star_rating)

            # Extract the text content of the span containing the reviews count
            reviews_text = review_main_content_div.find_element(By.CSS_SELECTOR, 'span[aria-label*="reviews"]').text

            # Print the reviews count
            print("Number of Reviews:", reviews_text)
        except NoSuchElementException:
            print("NoSuchElementException")
            print("Target has no star rating")
            if star_rating == "":
                star_rating = "NoSuchElementException"
            if reviews_text == "":
                reviews_text = "NoSuchElementException"
        except StaleElementReferenceException:
            print("StaleElementReferenceException")
            print("Target has no star rating")
            if star_rating == "":
                star_rating = "StaleElementReferenceException"
            if reviews_text == "":
                reviews_text = "StaleElementReferenceException"
        except TimeoutException:
            print("TimeoutException")
            print("Target has no star rating")
            if star_rating == "":
                star_rating = "TimeoutException"
            if reviews_text == "":
                reviews_text = "TimeoutException"

        try:
            # Find the category name "Japanese reaurant" using the class in <button class="DkEaL " jsaction="pane.rating.category">Japanese restaurant</button> ...
            category_name = WebDriverWait(browser, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.DkEaL'))).text
            
            # Print the category name
            print("Category:", category_name)
        except NoSuchElementException:
            print("NoSuchElementException")
            print("Target has no category name")
            if category_name == "":
                category_name = "NoSuchElementException"
        except StaleElementReferenceException:
            print("StaleElementReferenceException")
            print("Target has no category name")
            if category_name == "":
                category_name = "StaleElementReferenceException"
        except TimeoutException:
            print("TimeoutException")
            print("Target has no category name")
            if category_name == "":
                category_name = "TimeoutException"
        
        try:
            # Find the element with class "mgr77e" - pricing
            price_element = WebDriverWait(browser, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'mgr77e')))

            # Find the nested span element containing the aria-label
            nested_span_element = price_element.find_element(By.XPATH, './/span[@aria-label]')

            # Extract the aria-label value
            price_rating = nested_span_element.get_attribute('aria-label')

            # Print the price label
            print("Price Label:", price_rating)

        except NoSuchElementException:
            print("NoSuchElementException")
            print("Target has no price label")
            if price_rating == "":
                price_rating = "NoSuchElementException"
        except StaleElementReferenceException:
            print("StaleElementReferenceException")
            print("Target has no price label")
            if price_rating == "":
                price_rating = "StaleElementReferenceException"
        except TimeoutException:
            print("TimeoutException")
            print("Target has no price label")
            if price_rating == "":
                price_rating = "TimeoutException"
            
        # find the text of all the divs with class "Io6YTe fontBodyMedium kR99db "
        list_of_divs = browser.find_elements(By.CSS_SELECTOR, '.Io6YTe.fontBodyMedium.kR99db')
        metadata_list = []
        for i, div in enumerate(list_of_divs):
            print("metadata " + str(i + 1), ": " + str(div.text))
            metadata_list.append(div.text)

        # save the data to csv
        try:
            csv_writer.writerow([planning_area, location_name, star_rating, reviews_text, category_name, price_rating, metadata_list])
        except NameError:
            "element cannot be saved to csv"

        # if lesser than 5 elements left, scroll and load more elements
        if len(elements) - iterator < 5:
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
    find_target_in_area(URL + TARGET + "+in+", planning_area)


browser.quit()
