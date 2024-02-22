from fastapi import FastAPI
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import logging

# Configuración de trazas de registro
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/scrape_google_reviews")
async def scrape_google_reviews():
    logger.info("Iniciando scraping de reseñas de Google...")

    # URL del restaurante específico
    RESTAURANT_URL = "https://www.google.com/maps/place/Organi+Chiado/@38.7165792,-9.1985607,14z/data=!4m10!1m2!2m1!1svegan+restaurants+Lisbon,+Portugal!3m6!1s0xd1934792e992c63:0xfe03e3a5a36c5929!8m2!3d38.7102973!4d-9.1397163!15sCiJ2ZWdhbiByZXN0YXVyYW50cyBMaXNib24sIFBvcnR1Z2FsWiMiIXZlZ2FuIHJlc3RhdXJhbnRzIGxpc2JvbiBwb3J0dWdhbJIBEHZlZ2FuX3Jlc3RhdXJhbnTgAQA!16s%2Fg%2F11cst26nc2?entry=ttu"
    GOOGLE_URL = "https://www.google.com/"

    async with async_playwright() as pw:
        # Lanzar el navegador
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to Google
        print("Navigating to Google...")
        await page.goto(f"{GOOGLE_URL}")

        # deal with cookies page
        await page.click('.QS5gu.sy4vM')
        
        # Navigate to Google Maps search
        
        print("Navigating to Google Maps search...")
        await page.goto(f"{RESTAURANT_URL}")

        # Wait for the restaurant page to load
        print("Waiting for the restaurant page to load...")

        # Navegar a la búsqueda de Google Maps
        await page.goto(RESTAURANT_URL)
        logger.info("Página del restaurante cargada.")

        # Esperar a que se cargue la página del restaurante
        await asyncio.sleep(2)  # Ajustar el tiempo de espera según sea necesario

        # Determinar el idioma del navegador
        language = await page.evaluate('''() => {
            return navigator.language || navigator.userLanguage;
        }''')

        logger.info(f"Idioma del navegador: {language}")

        # Hacer clic en el enlace 'All reviews' para ir a la sección de reseñas según el idioma
        if language.startswith('es'):
            await page.click("text='Reseñas'")
        else:
            await page.click("text='Reviews'")

        logger.info("Haciendo clic en el enlace de reseñas.")

        # Esperar a que se carguen las reseñas
        await asyncio.sleep(2)  # Ajustar el tiempo de espera según sea necesario

        # Extraer el texto de las primeras 5 reseñas
        html = await page.inner_html('body')
        soup = BeautifulSoup(html, 'html.parser')
        review_elements = soup.select('.MyEned')
        reviews_text = [review.text.strip() for review in review_elements[:5]]

        print("Contenido de las reseñas:", reviews_text)

        logger.info("Reseñas extraídas exitosamente.")

        await asyncio.sleep(2)

        # Cerrar el navegador
        await browser.close()

        logger.info("Navegador cerrado.")

        return {"reviews": reviews_text}


@app.get('/')
async def read_root():
       return{"message": "Welcome to the review sentiment analysis API"}