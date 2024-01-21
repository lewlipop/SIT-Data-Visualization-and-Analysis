import csv
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, ElementClickInterceptedException
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime

# Constants
import constants

file_write_lock = threading.Lock()
file_write_lock_reviews = threading.Lock()

def convert_relative_time(relative_time):
    now = datetime.now()

    if 'day' in relative_time:
        days_ago = int(relative_time.split()[0].replace("a", "1"))
        return now - relativedelta(days=days_ago)

    elif 'month' in relative_time:
        months_ago = int(relative_time.split()[0].replace("a", "1"))
        return now - relativedelta(months=months_ago)

    elif 'year' in relative_time:
        years_ago = int(relative_time.split()[0].replace("a", "1"))
        return now - relativedelta(years=years_ago)

    else:
        return None

def get_next_day(day_of_week):
    if day_of_week == "Monday":
        return "Tuesday"
    elif day_of_week == "Tuesday":
        return "Wednesday"
    elif day_of_week == "Wednesday":
        return "Thursday"
    elif day_of_week == "Thursday":
        return "Friday"
    elif day_of_week == "Friday":
        return "Saturday"
    elif day_of_week == "Saturday":
        return "Sunday"
    elif day_of_week == "Sunday":
        return "Monday"
       
def find_target_in_area(url, planning_area, browser, csv_writer, csv_writer_reviews):
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
        location_name, sponsored_label, popular_times, star_rating, indv_star_rating, number_of_reviews, category_name, price_rating, address, all_tags, about_combined = "", "", {}, "", "", "", "", "", "", [], []

        seo_rating = element_index + 1

        print("Total elements found:", len(elements))
        current_element = elements[element_index]
        # href of current element
        href = current_element.get_attribute("href")
        print("current element:", element_index)
        browser.execute_script("arguments[0].scrollIntoView();", current_element)
        current_element.click()

        # find the aria-label of the element, which contains the location name
        location_name = current_element.get_attribute("aria-label")

        # how to figure out if the pop out is loaded? check class "DUwDvf lfPIob"
        while True: # while loop to make sure it the popout is newly loaded and not the previous one
            try:
                location_name2 = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.DUwDvf.lfPIob'))).text
                print("location_name:", location_name)
                print("location_name2:", location_name2)
            except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                print("TimeoutException")
                print("Target has no location name")
            
            if location_name == location_name2:
                break
            else:
                print(element_index)
                # reclick the element
                current_element.click()

        print("location_name2:", location_name2)

        while True:
                try:
                    # Find the category name e.g. "Japanese reaurant" using the class in <button class="DkEaL " jsaction="pane.rating.category">Japanese restaurant</button> ...
                    category_name = browser.find_element(By.CLASS_NAME, 'DkEaL').text
                    
                    # Print the category name
                    print("Category:", category_name)
                    break
                except NoSuchElementException:
                    # click the first button
                    # find buttons
                    tab_list = browser.find_element(By.CLASS_NAME, 'RWPxGd')
                    buttons = tab_list.find_elements(By.TAG_NAME, 'button')
                    buttons[0].click()
                    logging.exception("NoSuchElementException")
                    if category_name == "":
                        category_name = "NoSuchElementException"
                except StaleElementReferenceException:
                    logging.exception("StaleElementReferenceException")
                    if category_name == "":
                        category_name = "StaleElementReferenceException"
                except TimeoutException:
                    # click the first button
                    # find buttons
                    tab_list = browser.find_element(By.CLASS_NAME, 'RWPxGd')
                    buttons = tab_list.find_elements(By.TAG_NAME, 'button')
                    buttons[0].click()
                    logging.exception("TimeoutException")
                    if category_name == "":
                        category_name = "TimeoutException"


        # Check if sponsored

        # check if element with the class "kpih0e uvopNe" exists
        try:
            # find element with class zvLtDc
            sponsored_parent = browser.find_element(By.CLASS_NAME, 'lMbq3e')
            # check if element with class "kpih0e uvopNe" exists
            sponsored_label_element = sponsored_parent.find_element(By.CLASS_NAME, 'kpih0e.uvopNe')
            sponsored_place = sponsored_parent.find_element(By.CLASS_NAME, 'DUwDvf').text
            print("sponsored_place:", sponsored_place)
            sponsored_label = "Yes"
        except NoSuchElementException:
            logging.info("NoSuchElementException")
            if sponsored_label == "":
                sponsored_label = "No"
        except StaleElementReferenceException:
            logging.exception("StaleElementReferenceException")
            if sponsored_label == "":
                sponsored_label = "StaleElementReferenceException"


        # Check if popular times g2BVhd eoFzo  is present 
                
        try:
            # Find the element with class "g2BVhd eoFzo"
            all_popular_times = browser.find_elements(By.CLASS_NAME, 'g2BVhd')
            if len(all_popular_times) != 7 and len(all_popular_times) != 0:
                raise NoSuchElementException
            # get day of the week e.g. "Monday"
            day_of_week = datetime.today().strftime('%A')

            for day_popular_time in all_popular_times:
                busy_elements = day_popular_time.find_elements(By.CSS_SELECTOR, '.dpoVLd[aria-label]')

                day_popular_times = {}
                for busy_element in busy_elements:
                    # Extract the aria-label value
                    busy_time = busy_element.get_attribute('aria-label').replace('\u202f', ' ')
                    if "Currently" in busy_time:
                        percentage_busy = busy_time.split("%")[-1].split(" ")[-1]
                        # find the current hour e.g. current time is 6:20 pm it becomes "6 pm"
                        current_hour = datetime.now().strftime('%I %p')
                        day_popular_times[current_hour] = percentage_busy+"%"
                    else:
                        percentage_busy = busy_time.split("%")[0]
                        time_hour = busy_time.split("at ")[-1].replace(".", "")
                        # add to the dictionary with the time as the key
                        day_popular_times[time_hour] = percentage_busy+"%"
                # add to the dictionary with the day of the week as the key
                popular_times[day_of_week] = day_popular_times
                # get the next day of the week after the current day_of_week
                day_of_week = get_next_day(day_of_week)

            # Print the popular times
            print("Popular Times:", popular_times)
        except NoSuchElementException:
            logging.info("NoSuchElementException")
        

        try:
            # Find the star rating element within the main content div
            review_main_content_div = browser.find_element(By.CSS_SELECTOR, '.F7nice')

            # Extract the text content of the span containing the star rating
            star_rating = review_main_content_div.find_element(By.TAG_NAME, 'span').text

            # Print the star rating
            print("star_rating:", star_rating)

            try:

                # Extract the text content of the span containing the reviews count
                number_of_reviews = review_main_content_div.find_element(By.CSS_SELECTOR, 'span[aria-label*="reviews"]').text

                # remove the brackets
                number_of_reviews = number_of_reviews.replace("(", "").replace(")", "").replace(",", "")
                
                # Print the reviews count
                print("Number of Reviews:", number_of_reviews)
            except NoSuchElementException:
                # Extract the text content of the span containing the reviews count
                number_of_reviews = review_main_content_div.find_element(By.CSS_SELECTOR, 'span[aria-label*="1 review"]').text

                # remove the brackets
                number_of_reviews = number_of_reviews.replace("(", "").replace(")", "").replace(",", "")
                
                # Print the reviews count
                print("Number of Reviews:", number_of_reviews)
        except NoSuchElementException:
            logging.info("NoSuchElementException")
            if star_rating == "":
                star_rating = "NAN"
            if number_of_reviews == "":
                number_of_reviews = "NAN"
        except StaleElementReferenceException:
            logging.exception("StaleElementReferenceException")
            if star_rating == "":
                star_rating = "StaleElementReferenceException"
            if number_of_reviews == "":
                number_of_reviews = "StaleElementReferenceException"
        except TimeoutException:
            logging.exception("TimeoutException")
            if star_rating == "":
                star_rating = "TimeoutException"
            if number_of_reviews == "":
                number_of_reviews = "TimeoutException"
        
        try:
            # Find the element with class "mgr77e" - pricing
            price_element = browser.find_element(By.CLASS_NAME, 'mgr77e')

            # Find the nested span element containing the aria-label
            nested_span_element = price_element.find_element(By.XPATH, './/span[@aria-label]')

            # Extract the aria-label value
            price_rating = nested_span_element.get_attribute('aria-label').split(":")[-1]

            # Print the price label
            print("Price Label:", price_rating)

        except NoSuchElementException:
            print("Target has no price label")
            if price_rating == "":
                price_rating = "NAN"
        except StaleElementReferenceException:
            logging.exception("StaleElementReferenceException")
            if price_rating == "":
                price_rating = "StaleElementReferenceException"
        except TimeoutException:
            logging.exception("TimeoutException")
            if price_rating == "":
                price_rating = "TimeoutException"
            
        try:
            # find the text of all the divs with class "Io6YTe fontBodyMedium kR99db "
            list_of_divs = browser.find_elements(By.CSS_SELECTOR, '.Io6YTe.fontBodyMedium.kR99db')
            metadata_list = []
            for i, div in enumerate(list_of_divs):
                if i == 0:
                    # write to address
                    address = div.text
                    print("address:", address)
                else:
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

        # if there is at least 1 review there is a review tab
        if number_of_reviews != "NAN":
            # make sure there is a Review tab
            while True:
                found_reviews_tab = False
                buttons = tab_list.find_elements(By.TAG_NAME, 'button')
                for button in buttons:
                    if button.find_element(By.CLASS_NAME, 'Gpq6kf.fontTitleSmall').text == "Reviews":
                        found_reviews_tab = True
                        review_button = button
                        break
                if found_reviews_tab:
                    break
            while True:
                # Click on the Second tab which is the "Reviews" tab
                review_button.click()
                # Locate the button element
                button = browser.find_element(By.CLASS_NAME, 'hh2c6.G7m0Af')
                # Check if the button is selected
                data_tab_index= button.get_attribute('data-tab-index')
                if data_tab_index == "1":
                    print("Reviews tab is selected")
                    break

            while True:
                try:
                    # Extract the number of reviews for each star level
                    reviews_elements = browser.find_elements(By.CLASS_NAME, 'BHOKXe')

                    for review_element in reviews_elements:
                        star_level = review_element.find_element(By.CLASS_NAME, 'yxmtmf').text
                        reviews_count = review_element.get_attribute('aria-label').split(",")[1].split()[0]
                        print(f"{star_level} - {reviews_count}")
                        indv_star_rating += f"{star_level} stars: {reviews_count}"

                        # Check if it's not the last review element, then add a comma
                        if review_element != reviews_elements[-1]:
                            indv_star_rating += ", "
                    break
                except StaleElementReferenceException:
                    logging.exception("StaleElementReferenceException")
            

            # List of dishes
            # Wait for the element with class "m6QErb tLjsW" to be present
            tags_elements_parent = WebDriverWait(browser, 4).until(EC.presence_of_element_located((By.CLASS_NAME, 'm6QErb.tLjsW')))

            # Find all tags and review counts under the element
            tags_elements = browser.find_elements(By.XPATH, '//div[@class="m6QErb tLjsW "]//div[@class="KNfEk "]')

            # Extract and print the tag and review count for each element
            for tag_element in tags_elements:
                tag = tag_element.find_element(By.CLASS_NAME, 'fontBodyMedium').text
                review_count = tag_element.find_element(By.CLASS_NAME, 'bC3Nkc').text
                tag_num = f"{tag} - {review_count}"
                print(tag_num)
                all_tags.append(tag_num)


                
            # Scrape all reviews
            review_index = 0
            # Scroll down
            # Locate the div element
            div_element = browser.find_element(By.CLASS_NAME, 'm6QErb.DxyBCb.kA9KIf.dS8AEf')

            # Scroll down within the div using JavaScript
            # find element m6QErb tLjsW 
            tags_element_scroll = browser.find_element(By.CLASS_NAME, 'm6QErb.tLjsW')
            browser.execute_script("arguments[0].scrollIntoView();", tags_element_scroll)

            # wait for the element with class "jftiEf fontBodyMedium", the review element class, to be present
            while True:
                try:
                    review_present = WebDriverWait(browser, 4).until(EC.presence_of_element_located((By.CLASS_NAME, 'jftiEf.fontBodyMedium')))
                    break
                except TimeoutException:
                    logging.exception("TimeoutException")
            
            visible_reviews = browser.find_elements(By.CLASS_NAME, 'jftiEf.fontBodyMedium')
            while True:
                current_review = visible_reviews[review_index]
                # # if less than 5 elements left, scroll and load more elements
                # if len(reviews) - review_index < 5:
                # Get href of current place
                href_of_place = href

                # Get review ID
                review_id = current_review.get_attribute('data-review-id')

                # Get relavancy ranking
                relavancy_ranking = review_index + 1

                # Get reviewer href which is the data-review-id of WEBjve class in the current review
                reviewer_href = current_review.find_element(By.CLASS_NAME, 'WEBjve').get_attribute('data-review-id')

                # Get reviewer name which is in the aria-label of the current review
                reviewer_name = current_review.get_attribute('aria-label')
                print("reviewer_name:", reviewer_name)

                # Get local guide status class RfnDt
                try:
                    reviewer_status = current_review.find_element(By.CLASS_NAME, 'RfnDt').text
                    reviewer_status_list = reviewer_status.split(" · ")
                    if len(reviewer_status_list) == 3:
                        reviewer_local_guide_status = True
                        reviewer_total_reviews = reviewer_status_list[1]
                        reviewer_total_photos = reviewer_status_list[2]
                    elif len(reviewer_status_list) == 2:
                        reviewer_local_guide_status = False
                        reviewer_total_reviews = reviewer_status_list[0]
                        reviewer_total_photos = reviewer_status_list[1]
                    reviewer_total_reviews = reviewer_total_reviews.split(" ")[0].replace(",", "")
                    reviewer_total_photos = reviewer_total_photos.split(" ")[0].replace(",", "")
                except NoSuchElementException:
                    logging.info("NoSuchElementException")
                    reviewer_local_guide_status = False
                    reviewer_total_reviews = "NAN"
                    reviewer_total_photos = "NAN"

                # Get star rating in aria-label of kvMYJc class in current review
                reviewer_star_rating = current_review.find_element(By.CLASS_NAME, 'kvMYJc').get_attribute('aria-label')
                reviewer_star_rating = reviewer_star_rating.split(" star")[0]
                print("reviewer_star_rating:", reviewer_star_rating)

                # Get date of review in class rsqaWe
                relative_time = current_review.find_element(By.CLASS_NAME, 'rsqaWe').text
                # find today's date and subtract the relative_time
                review_date = convert_relative_time(relative_time)
                print("review_date:", review_date)

                while True:
                    # Click the "more" button w8nwRe kyuRq to expand the review text if present
                    try:
                        more_button = current_review.find_element(By.CLASS_NAME, 'w8nwRe.kyuRq')
                        more_button.click()
                    except NoSuchElementException:
                        logging.info("NoSuchElementException")
                        print("No more button")
                        break
                    except StaleElementReferenceException:
                        logging.exception("StaleElementReferenceException")
                        print("No more button")
                        break
                
                # Get review text in class wiI7pd
                try:
                    review_text = current_review.find_element(By.CLASS_NAME, 'wiI7pd').text
                    print("review_text:", review_text)
                except NoSuchElementException:
                    logging.info("NoSuchElementException")
                    print("No review text")
                    review_text = "NAN"

                detail_list = []
                try:
                    # Find the review element using Selenium with jslog="127691" attribute
                    review_text_element = current_review.find_element(By.XPATH, './/div[@jslog="127691"]')
                    # Find all the metadata elements PBK6be
                    metadata_elements = review_text_element.find_elements(By.CLASS_NAME, 'PBK6be')
                    # Extract and print metadata details
                    for metadata_element in metadata_elements:
                        # Extract detail title
                        detail_title_element = metadata_element.find_element(By.CLASS_NAME, 'RfDO5c')
                        detail_title = detail_title_element.text.strip()

                        try:
                            # Extract detail content
                            detail_content_elements = metadata_element.find_elements(By.XPATH, './/div')
                            detail_content = detail_content_elements[1].text.strip()
                        except IndexError:
                            detail_content = ""
                        if detail_content == "":
                            detail_list.append(detail_title)
                        else:
                            detail_list.append(f"{detail_title}: {detail_content}")
                        print(f"{detail_title}: {detail_content}")
                except NoSuchElementException:
                    logging.info("NoSuchElementException")
                    print("No metadata")

                # Write to CSV file
                with file_write_lock_reviews:
                    csv_writer_reviews.writerow([href_of_place, review_id, relavancy_ranking, reviewer_href, reviewer_name, reviewer_local_guide_status, reviewer_total_reviews, reviewer_total_photos, reviewer_star_rating, review_date, review_text, detail_list])


                # scroll until there's more reviews below the current review
                # set max timing to wait for the next review to load to 5 seconds
                # start timing
                start_time = datetime.now()
                time_out_error = False
                while True:
                    if (datetime.now() - start_time).seconds > 5:
                        time_out_error = True
                        break
                    # scroll to last element
                    presentation_elements = browser.find_elements(By.CLASS_NAME, 'qCHGyb')
                    try:
                        browser.execute_script("arguments[0].scrollIntoView();", presentation_elements[-1])
                    except StaleElementReferenceException:
                        logging.exception("StaleElementReferenceException")

                    # more elements are loaded after scrolling, add the new elements to the list, but only if they are not already in the list
                    new_reviews = browser.find_elements(By.CLASS_NAME, 'jftiEf.fontBodyMedium')
                    for new_review in new_reviews:
                        if new_review not in visible_reviews:
                            visible_reviews.append(new_review)
                    if len(visible_reviews) > review_index + 1 or review_index == int(number_of_reviews)-1:
                        break
                
                if review_index == int(number_of_reviews)-1: # if reached the last review
                    break
                if review_index == constants.MAX_REVIEWS_PER_PLACE-1:
                    break
                if time_out_error:
                    break

                # increment review index
                review_index += 1


        # Find the about tab
        found_about_tab = False
        tab_list = browser.find_element(By.CLASS_NAME, 'RWPxGd')
        buttons = tab_list.find_elements(By.TAG_NAME, 'button')
        for button in buttons:
            if button.find_element(By.CLASS_NAME, 'Gpq6kf.fontTitleSmall').text == "About":
                found_about_tab = True
                about_button = button
        if found_about_tab:
            while True:
                try:
                    about_button.click()
                    about_present = browser.find_element(By.CLASS_NAME, 'iP2t7d.fontBodyMedium')
                    break
                except NoSuchElementException:
                    logging.info("NoSuchElementException")
                except ElementClickInterceptedException:
                    logging.exception("ElementClickInterceptedException")
            
            while True:
                try:
                    about_elements = browser.find_elements(By.XPATH, '//ul[@class="ZQ6we"]/li/span')
                    about_options = [option.text for option in about_elements]
                    about_combined = about_options
                    break
                except StaleElementReferenceException:
                    logging.exception("StaleElementReferenceException")
                    continue
            
        with file_write_lock:
            csv_writer.writerow([href, planning_area, location_name, seo_rating, sponsored_label, popular_times, star_rating, indv_star_rating, number_of_reviews, category_name, price_rating, address, metadata_list, all_tags, about_combined])

        # if lesser than 5 elements left, scroll and load more elements
        if len(elements) - element_index < 10:
            browser.execute_script("arguments[0].scrollIntoView();", elements[-1])

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
            
def scrape_area(planning_area, csv_writer, csv_writer_reviews):
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    browser = webdriver.Chrome(options=chrome_options)

    # Navigate to the Chrome settings page
    browser.get('chrome://settings/')
    # Execute JavaScript code to set the default zoom level to 80%
    browser.execute_script('chrome.settingsPrivate.setDefaultZoom(0.8);')

    find_target_in_area(constants.URL + constants.TARGET + "+in+Singapore,+", planning_area, browser, csv_writer, csv_writer_reviews)

    browser.quit()

def main():

    # Create a CSV file and write the header
    csv_file = open('scraped_data_' + constants.TARGET.replace("+", "_") + '.csv', 'w', encoding='utf-8-sig', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['href', 'Planning Area', 'Name', 'Search Engine Rating', 'Sponsored', 'Popular Times', 'Average Star Rating', 'Individual Star Rating', 'Reviews', 'Category', 'Price Rating', 'Address', 'Metadata', 'Tags', 'About'])

    csv_file_reviews = open('scraped_data_reviews_' + constants.TARGET.replace("+", "_") + '.csv', 'w', encoding='utf-8-sig', newline='')
    csv_writer_reviews = csv.writer(csv_file_reviews)
    csv_writer_reviews.writerow(['href of Place', 'Review ID', 'Relavancy Ranking', 'Reviewer href', 'Reviewer Name', 'Local Guide', 'Total Reviews', 'Total Photos', 'Star Rating', 'Date', 'Review', 'Metadata', ])

    # run Multi Threaded
    with ThreadPoolExecutor(max_workers=6) as executor:
        for planning_area in constants.LIST_OF_PLANNING_AREAS:
            executor.submit(scrape_area, planning_area, csv_writer, csv_writer_reviews)

    # # run Single Threaded
    # for planning_area in constants.LIST_OF_PLANNING_AREAS:
    #     scrape_area(planning_area, csv_writer, csv_writer_reviews)

    # # Close the CSV file
    # csv_file.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()