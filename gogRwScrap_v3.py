import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# the category for which we seek reviews
CATEGORY = "vegan restaurants"
# the location
LOCATION = "Lisbon, Portugal"
# google's main URL
URL = "https://www.google.com/"

if __name__ == '__main__':
    with sync_playwright() as pw:
        # creates an instance of the Chromium browser and launches it
        print("Launching the browser...")
        browser = pw.chromium.launch(headless=False)
        # creates a new browser page (tab) within the browser instance
        page = browser.new_page()
        # go to url with Playwright page element
        print(f"Going to URL: {URL}")
        page.goto(URL)
        # deal with cookies page
        print("Handling cookies...")
        page.click('.QS5gu.sy4vM')
        # write what you're looking for
        print(f"Searching for '{CATEGORY} near {LOCATION}'...")
        page.fill("textarea", f"{CATEGORY} near {LOCATION}")
        # press enter
        page.keyboard.press('Enter')
        # change to English
        #print("Switching to English...")
        #page.locator("text='Change to English'").click()
        #time.sleep(4)
        # click on the "Maps" HTML element
        print("Clicking on the 'Maps' HTML element...")
        page.click('.GKS7s')
        time.sleep(4)
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
            page.locator("text='Reviews'").first.click()
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
