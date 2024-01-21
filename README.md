# Dining Insights: Singapore

## Overview

Welcome to the Dining Insights project by Group 3! This Python project focuses on analyzing and visualizing data from dine-in food places, including restaurants and coffee shops, in Singapore. Our objective aligns with the requirements of the ICT1002 Programming Fundamentals course, aiming to apply and deepen our Python programming skills, practice team collaboration using Python tools and libraries, and gain hands-on experience in solving real-world problems.

## Project Scope

In adherence to the project specifications, we will explore various aspects of dining establishments in Singapore, such as:

- **Location Ratings:** Identifying areas with higher ratings based on customer reviews.
- **Price Analysis:** Analyzing the distribution of food prices, highlighting places with more expensive and more affordable options.
- **Cuisine Diversity:** Exploring the types of cuisine available in specific areas.
- **Review Quality:** Identifying locations with better and higher reviews.

## Tools and Technologies

To achieve our objectives, we will leverage the following technologies:

- **Python:** The primary programming language for data processing, analysis, and visualization.
- **Google Maps:** To scrape relevant data about dine-in establishments in Singapore.
- **Data Visualization Libraries:** Utilizing libraries like Matplotlib and Seaborn for creating pie charts, bar graphs, and other visualizations.

## Project Structure

The project will be organized into the following sections:

1. **Data Collection:** Scraping relevant data from Google Maps using Selenium.
2. **Data Processing:** Cleaning and organizing the collected data for analysis.
3. **Data Analysis:** Extracting insights from the dataset to answer specific questions about dining establishments.
4. **Data Visualization:** Creating visually appealing and informative charts and graphs to represent our findings.
5. **Documentation:** Providing comprehensive documentation to guide users and developers through the project.

## Getting Started

To run and explore the project locally, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/AlexanderLJX/SIT-Data-Visualization-and-Analysis.git
2. Install Dependencies:
   ```bash
   pip install -r requirements.txt
3. Run the Project:
   ```bash
   python main.py

## Web Scraping

1. Lauching the web srcaper
   ```bash
   python googlemaps_scraper/scraper.py

## Data parsing

1. Launching the data parser
   ```bash
   python parser.py

## Data

**Restaurants csv:**
 - **href:** Link to the restaurant
 - **Planning area:** 1 of the 55 divisions in Singapore
 - **Name:** Name of the restaurant
 - **Search Engine Rating:** 1 means it it the first restaurant that appears in the list when searching that specific planning area, 2 means it's the second, and so on.
 - **Sponsored:** Whether the restaurant paid for google advertising. This will probably mean it will be the first to appear in the list, search engine rating 1.
 - **Popular Times:** Data on aggregated and anonymized Location History data
 - **Average Star Rating:** Average star rating of the restaurant
 - **Reviews:** Number of reviews of the restaurant
 - **Category:** Category of the restaurant e.g. (Korean, Japanese, etc...)
 - **Price Rating:** Official Google price rating of the restaurant (The number of dollar signs)
 - **Address:** Address of the restaurant
 - **Metadata:** Metadata of the restaurant, including location etc.
 - **Tags** Food tags, given by reviewers. e.g. Chicken, Pasta, etc..
 - **About** A list of stuff in the About section of the restaurant


**Reviews csv:**
 - **href of Place:** Link to the place on google maps, can be used as Primary key for the Restaurants csv
 - **Review ID:** Review ID of the review
 - **Relavancy Ranking:** Ranking of the review, 1 being the most relevant (Appears as the first review)
 - **Reviewer href:** Link to reviewer, can be used a primary key
 - **Reviewer Name:** Name of the reviewer
 - **Local Guide:** Whether the reviewer is a local guide
 - **Total Reviews:** Total number of reviews the reviewer has made
 - **Total Photos:** Total number of photos the reviewer has made
 - **Star Rating:** Star rating of the review
 - **Date:** Date the review was made - calculated based on relative time
 - **Review:** Text of the review
 - **Metadata:** Food, Service ratings etc.
 

## TODO

