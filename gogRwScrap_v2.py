import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Define the search query
SEARCH_QUERY = "Organi Chiado"
# Google Maps search URL format
MAPS_SEARCH_URL = "https://www.google.com/maps/search/"

GOOGLE_URL = "https://www.google.com/"

if __name__ == '__main__':
    with sync_playwright() as pw:
        # Launch the browser
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to Google
        print("Navigating to Google...")
        page.goto(f"{GOOGLE_URL}")

        # deal with cookies page
        page.click('.QS5gu.sy4vM')
        
        # Navigate to Google Maps search
        
        print("Navigating to Google Maps search...")
        page.goto(f"{MAPS_SEARCH_URL}{SEARCH_QUERY}")

        # Wait for the search results to load
        print("Waiting for the search results to load...")
        time.sleep(5)  # Adjust sleep time as needed for your connection speed
        
        # Click on the first search result to go to its Google Maps page
        print("Clicking on the first search result...")
        page.click('.hfpxzc:first-child')
        
        # Wait for the restaurant page to load
        print("Waiting for the restaurant page to load...")
        time.sleep(5)  # Adjust sleep time as needed
        
        # Click on the 'All reviews' link to go to the reviews section
        print("Clicking on the 'Reseñas' link...")
        page.click("text='Reseñas'")
        
        # Wait for the reviews to load
        print("Waiting for the reviews to load...")
        time.sleep(5)  # Adjust sleep time as needed
        
        # Extract the text of the first 5 reviews
        print("Extracting the text of the first 5 reviews...")


        # scrolling
        for i in range(2):
            # tackle the body element
            print("Scrolling...")
            html = page.inner_html('body')
            # create beautiful soup element
            soup = BeautifulSoup(html, 'html.parser')

            # select items
            categories = soup.select('.hfpxzc')
            last_category_in_page = categories[-1].get('aria-label')
            # scroll to the last item
            last_category_location = page.locator(
                f"text={last_category_in_page}")
            last_category_location.scroll_into_view_if_needed()
            # wait to load contents
            time.sleep(4)

        # get links of all categories after scroll
        links = [item.get('href') for item in soup.select('.hfpxzc')]

        for link in links:
            # go to subject link
            print(f"Going to link: {link}")
            page.goto(link)
            time.sleep(4)
            # load all reviews
            print("Loading all reviews...")
            page.locator("text='Reseñas'").first.click()
            time.sleep(4)
            # create new soup
            html = page.inner_html('body')
            # create beautiful soup element
            soup = BeautifulSoup(html, 'html.parser')
            # scrape reviews
            reviews = soup.select('.MyEned')
            reviews = [review.find('span').text for review in reviews]
            # print reviews
            for review in reviews:
                print(review)
                print('\n')


        
        # Close the browser
        print("Closing the browser...")
        browser.close()

