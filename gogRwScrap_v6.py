from fastapi import FastAPI, Query
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from transformers import pipeline
import logging

app = FastAPI()

# Configuración de trazas de registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model_name = "mrcaelumn/yelp_restaurant_review_sentiment_analysis"
sentiment_pipeline = pipeline("text-classification", model=model_name)

def map_score(score):
    if score >= 0.5:
        return "POSITIVE"
    elif score <= 0.4:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

def analyze_sentiment_severalReviews(reviews: list):
    logger.info("Analizando el sentimiento de las revisiones...")
    predictions = [sentiment_pipeline(review) for review in reviews]
    average_scores = []
    for prediction in predictions:
        scores = [p['score'] for p in prediction]
        average_score = sum(scores) / len(scores)
        average_scores.append(average_score)
    overall_average_score = sum(average_scores) / len(average_scores)
    overall_sentiment_label = map_score(overall_average_score)
    logger.info("Análisis de sentimiento completado.")
    return overall_average_score, overall_sentiment_label

@app.get("/scrape_google_reviews")
async def scrape_google_reviews(url: str = Query(..., description="URL del restaurante específico")):
    logger.info("Iniciando scraping de reseñas de Google...")

    GOOGLE_URL = "https://www.google.com/"

    async with async_playwright() as pw:
        # Lanzar el navegador
        logger.info("Lanzando el navegador...")
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to Google
        logger.info("Navegando a Google...")
        await page.goto(f"{GOOGLE_URL}")

        # deal with cookies page
        logger.info("Lidiando con la página de cookies...")
        await page.click('.QS5gu.sy4vM')

        # Navigate to the restaurant URL provided by the user
        logger.info(f"Navegando a la URL del restaurante: {url}")
        await page.goto(f"{url}")

        # Esperar a que se cargue la página del restaurante
        logger.info("Esperando a que se cargue la página del restaurante...")
        await asyncio.sleep(1)  # Ajustar el tiempo de espera según sea necesario

        # Determinar el idioma del navegador
        logger.info("Determinando el idioma del navegador...")
        language = await page.evaluate('''() => {
            return navigator.language || navigator.userLanguage;
        }''')

        # Hacer clic en el enlace 'All reviews' para ir a la sección de reseñas según el idioma
        logger.info("Haciendo clic en el enlace 'All reviews'...")
        if language.startswith('es'):
            await page.click("text='Reseñas'")
        else:
            await page.click("text='Reviews'")

        # Esperar a que se carguen las reseñas
        logger.info("Esperando a que se carguen las reseñas...")
        await asyncio.sleep(1)  # Ajustar el tiempo de espera según sea necesario

        # Extraer el texto de las primeras 5 reseñas
        logger.info("Extrayendo el texto de las reseñas...")
        html = await page.inner_html('body')
        soup = BeautifulSoup(html, 'html.parser')
        review_elements = soup.select('.MyEned')
        reviews_text = [review.text.strip() for review in review_elements[:5]]

        # Cerrar el navegador
        logger.info("Cerrando el navegador...")
        await browser.close()

        # Analizar el sentimiento de las revisiones y calcular la media del puntaje
        logger.info("Calculando el sentimiento de las reseñas...")
        overall_average_score, overall_sentiment_label = analyze_sentiment_severalReviews(reviews_text)

        # Devolver el puntaje promedio general y su etiqueta de sentimiento
        logger.info("Devolviendo los resultados.")
        return {"overall_average_score": overall_average_score, "overall_sentiment_label": overall_sentiment_label}


@app.get('/')
async def read_root():
       return{"message": "Welcome to the review sentiment analysis API"}


# URL para probar: 
# https://www.google.com/maps/place/Organi+Chiado/@38.7165792,-9.1985607,14z/data=!4m10!1m2!2m1!1svegan+restaurants+Lisbon,+Portugal!3m6!1s0xd1934792e992c63:0xfe03e3a5a36c5929!8m2!3d38.7102973!4d-9.1397163!15sCiJ2ZWdhbiByZXN0YXVyYW50cyBMaXNib24sIFBvcnR1Z2FsWiMiIXZlZ2FuIHJlc3RhdXJhbnRzIGxpc2JvbiBwb3J0dWdhbJIBEHZlZ2FuX3Jlc3RhdXJhbnTgAQA!16s%2Fg%2F11cst26nc2?entry=ttu
# Devuelve una MEDIA de las 5 primeras reseñas junto con la MEDIA de los sentimientos de estas
