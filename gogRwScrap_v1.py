from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get('https://www.google.es/maps/place/St.+JOHN+Restaurant/@51.519344,-0.1502597,14z/data=!4m12!1m2!2m1!1slondon+restaurants!3m8!1s0x48761b5161b93317:0x86773f8e76f37d7!8m2!3d51.5204534!4d-0.1014304!9m1!1b1!15sChJsb25kb24gcmVzdGF1cmFudHNaFCISbG9uZG9uIHJlc3RhdXJhbnRzkgESd2VzdGVybl9yZXN0YXVyYW504AEA!16zL20vMGdmZng2?entry=ttu')

# Click the 'All reviews' button to load the reviews
wait = WebDriverWait(driver, 20)
all_reviews_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Todas')]")))
all_reviews_button.click()

# Wait for the reviews to load
try:
    reviews = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='ODSEW-ShBeI-content']")))
except TimeoutException:
    print("Timeout: No se pudieron encontrar los elementos de las reseñas dentro del tiempo de espera.")
    driver.quit()


# Find all the review elements
reviews = driver.find_elements(By.XPATH, "//div[@class='ODSEW-ShBeI-content']")

# Print the text of the first 5 reviews
for index, review in enumerate(reviews[:5], start=1):
    print(f"Review {index}: {review.text}")

driver.quit()
