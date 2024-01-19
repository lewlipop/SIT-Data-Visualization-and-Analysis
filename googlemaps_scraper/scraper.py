import csv
import logging
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException


# Constants


# list of planning areas in Singapore from https://en.wikipedia.org/wiki/Planning_Areas_of_Singapore
LIST_OF_PLANNING_AREAS = [
    "Ang Mo Kio",
    "Bedok",
    "Bishan",
    "Bukit Batok",
    "Bukit Merah",
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

TARGET = "food"


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
       last_category_location = WebDriverWait(browser, 4).until(EC.presence_of_element_located((By.XPATH, f"""//*[@aria-label="{last_category_in_page}"]""")))
       
       # Scroll to the last category
       browser.execute_script("arguments[0].scrollIntoView();", last_category_location)
       
def find_target_in_area(url, planning_area, browser, csv_writer):
    url = url + planning_area
    browser.get(url)
    print(url)
    # get all elements with class "hfpxzc"
    elements = browser.find_elements(By.CLASS_NAME, "hfpxzc")

    # iterate_and_scroll(elements)

    noMoreResults = False
    element_index = 0

    while True:
        # initialise variables
        location_name, star_rating, number_of_reviews, category_name, price_rating = "", "", "", "", ""

        seo_rating = element_index + 1

        print("Total elements found:", len(elements))
        current_element = elements[element_index]
        print("current element:", element_index)
        browser.execute_script("arguments[0].scrollIntoView();", current_element)
        current_element.click()

        # find the aria-label of the element
        location_name = current_element.get_attribute("aria-label")
        print("location_name:", location_name)

        # how to figure out if the pop out is loaded? check class "DUwDvf lfPIob"
        while True: # while loop to make sure it the popout is newly loaded and not the previous one
            try:
                location_name2 = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.DUwDvf.lfPIob'))).text
                print("location_name2:", location_name2)
            except TimeoutException:
                print("TimeoutException")
                print("Target has no location name")
                location_name2 = "TimeoutException"
                break
            except NoSuchElementException:
                print("NoSuchElementException")
                print("Target has no location name")
                location_name2 = "NoSuchElementException"
            except StaleElementReferenceException:
                print("StaleElementReferenceException")
                print("Target has no location name")
                location_name2 = "StaleElementReferenceException"
            if location_name == location_name2:
                break
            else:
                print(element_index)
                # reclick the element
                current_element.click()
                
                
        print("location_name2:", location_name2)
        

        try:
            # Find the star rating element within the main content div
            review_main_content_div = browser.find_element(By.CSS_SELECTOR, '.F7nice')

            # Extract the text content of the span containing the star rating
            star_rating = review_main_content_div.find_element(By.TAG_NAME, 'span').text

            # Print the star rating
            print("star_rating:", star_rating)

            # Extract the text content of the span containing the reviews count
            number_of_reviews = review_main_content_div.find_element(By.CSS_SELECTOR, 'span[aria-label*="reviews"]').text

            # Print the reviews count
            print("Number of Reviews:", number_of_reviews)
        except NoSuchElementException:
            print("NoSuchElementException")
            print("Target has no star rating")
            if star_rating == "":
                star_rating = "NAN"
            if number_of_reviews == "":
                number_of_reviews = "NAN"
        except StaleElementReferenceException:
            print("StaleElementReferenceException")
            print("Target has no star rating")
            if star_rating == "":
                star_rating = "StaleElementReferenceException"
            if number_of_reviews == "":
                number_of_reviews = "StaleElementReferenceException"
        except TimeoutException:
            print("TimeoutException")
            print("Target has no star rating")
            if star_rating == "":
                star_rating = "TimeoutException"
            if number_of_reviews == "":
                number_of_reviews = "TimeoutException"

        try:
            # Find the category name e.g. "Japanese reaurant" using the class in <button class="DkEaL " jsaction="pane.rating.category">Japanese restaurant</button> ...
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
            price_element = browser.find_element(By.CLASS_NAME, 'mgr77e')

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
                price_rating = "NAN"
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
            
        try:
            # find the text of all the divs with class "Io6YTe fontBodyMedium kR99db "
            list_of_divs = browser.find_elements(By.CSS_SELECTOR, '.Io6YTe.fontBodyMedium.kR99db')
            metadata_list = []
            for i, div in enumerate(list_of_divs):
                print("metadata " + str(i + 1), ": " + str(div.text))
                metadata_list.append(div.text)
        except NoSuchElementException:
            print("NoSuchElementException")
            print("Target has no metadata")
            metadata_list = ["NoSuchElementException"]
        except StaleElementReferenceException:
            print("StaleElementReferenceException")
            print("Target has no metadata")
            metadata_list = ["StaleElementReferenceException"]

        # Locate the tab list
        tab_list = browser.find_element(By.CLASS_NAME, 'RWPxGd')

        # Find all buttons within the tab list
        buttons = tab_list.find_elements(By.TAG_NAME, 'button')

        # if 3 buttons, there is a Review tab
        if len(buttons) == 3:
            # Click on the Second tab which is the "Reviews" tab
            buttons[1].click()

            element = WebDriverWait(browser, 4).until(EC.presence_of_element_located((By.CLASS_NAME, 'Bd93Zb')))

            # Extract the number of reviews for each star level
            reviews_elements = browser.find_elements(By.CLASS_NAME, 'BHOKXe')

            for review_element in reviews_elements:
                star_level = review_element.find_element(By.CLASS_NAME, 'yxmtmf').text
                reviews_count = review_element.get_attribute('aria-label').split(",")[1].split()[0]

                print(f"{star_level} stars: {reviews_count} reviews")

            # List of dishes
                
            # scrape_all_reviews()
            
            # Click on About tab
            buttons[2].click()
        else:
            print("Target has no reviews")
            # Click on About tab
            buttons[1].click()
        
         # Scrape about details
            
        

        
        csv_writer.writerow([planning_area, location_name, seo_rating, star_rating, number_of_reviews, category_name, price_rating, metadata_list])

        # if lesser than 5 elements left, scroll and load more elements
        if len(elements) - element_index < 4:
            scroll_and_load(browser, '.hfpxzc')

        # more elements are loaded after scrolling, add the new elements to the list, but only if they are not already in the list
        new_elements = browser.find_elements(By.CLASS_NAME, "hfpxzc")
        for new_element in new_elements:
            if new_element not in elements:
                elements.append(new_element)
        
        # Check if the "You've reached the end of the list." message is present
        end_of_list_element = browser.find_elements(By.CLASS_NAME, 'HlvSq')
        if end_of_list_element:
            print("You've scrolled to the end of the list.")
            noMoreResults = True
        
        element_index += 1
        
        if noMoreResults and element_index == len(new_elements):
            print("Finished scraping all elements")
            break
            

def main():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")

    browser = webdriver.Chrome(options=chrome_options)

    # Create a CSV file and write the header
    csv_file = open('scraped_data_' + TARGET.replace("+", "_") + '.csv', 'w', encoding='utf-8-sig', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Planning Area', 'Name', 'SEO Rating', 'Star Rating', 'Reviews', 'Category', 'Google Price Rating', 'Metadata'])

    # for each planning area, get the url and find the target
    for planning_area in LIST_OF_PLANNING_AREAS:
        find_target_in_area(URL + TARGET + "+in+Singapore,+", planning_area, browser, csv_writer)

    # Close the CSV file
    csv_file.close()

    browser.quit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()