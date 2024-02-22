import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# URL of the specific restaurant
RESTAURANT_URL = "https://www.google.com/maps/place/Organi+Chiado/@38.7165792,-9.1985607,14z/data=!4m10!1m2!2m1!1svegan+restaurants+Lisbon,+Portugal!3m6!1s0xd1934792e992c63:0xfe03e3a5a36c5929!8m2!3d38.7102973!4d-9.1397163!15sCiJ2ZWdhbiByZXN0YXVyYW50cyBMaXNib24sIFBvcnR1Z2FsWiMiIXZlZ2FuIHJlc3RhdXJhbnRzIGxpc2JvbiBwb3J0dWdhbJIBEHZlZ2FuX3Jlc3RhdXJhbnTgAQA!16s%2Fg%2F11cst26nc2?entry=ttu"
GOOGLE_URL = "https://www.google.com/"

if __name__ == '__main__':
    with sync_playwright() as pw:
        # Launch the browser
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to Google
        print("Navigating to Google...")
        page.goto(f"{GOOGLE_URL}")

        # deal with cookies page
        page.click('.QS5gu.sy4vM')
        
        # Navigate to Google Maps search
        
        print("Navigating to Google Maps search...")
        page.goto(f"{RESTAURANT_URL}")

        # Wait for the restaurant page to load
        print("Waiting for the restaurant page to load...")
        time.sleep(2)  # Adjust sleep time as needed
        
        # Determine the language of the browser
        language = page.evaluate('''() => {
            return navigator.language || navigator.userLanguage;
        }''')

        # Click on the 'All reviews' link to go to the reviews section based on language
        if language.startswith('es'):
            print("Clicking on the 'Reseñas' link...")
            page.click("text='Reseñas'")
        else:
            print("Clicking on the 'Reviews' link...")
            page.click("text='Reviews'")
        
        # Wait for the reviews to load
        print("Waiting for the reviews to load...")
        time.sleep(2)  # Adjust sleep time as needed
        
        # Extract the text of the first 5 reviews
        print("Extracting the text of the first 5 reviews...")
        
        # load all reviews
        print("Loading all reviews...")
        # create new soup
        html = page.inner_html('body')
        # create beautiful soup element
        soup = BeautifulSoup(html, 'html.parser')
        # scrape reviews
        reviews = soup.select('.MyEned')
        # scrape reviews, taking only the first 5 reviews
        reviews = [review.find('span').text for review in reviews[:5]]

        # print reviews
        for review in reviews:
            print(review)
            print('\n')

        # Close the browser
        print("Closing the browser...")
        browser.close()

