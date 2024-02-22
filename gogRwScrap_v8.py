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
    predictions = [sentiment_pipeline(review) for review in reviews]
    average_scores = []
    for prediction in predictions:
        scores = [p['score'] for p in prediction]
        average_score = sum(scores) / len(scores)
        average_scores.append(average_score)
    overall_average_score = sum(average_scores) / len(average_scores)
    overall_sentiment_label = map_score(overall_average_score)
    return overall_average_score, overall_sentiment_label

@app.get("/scrape_google_reviews")
async def scrape_google_reviews(url: str = Query(..., description="URL del restaurante específico")):
    logger.info("Iniciando scraping de reseñas de Google...")

    async with async_playwright() as pw:
        logger.info("Lanzando el navegador...")
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        logger.info(f"Navegando a la URL del restaurante: {url}")
        await page.goto(url)

        cookie_dialog_selector = 'text="Aceptar todo"'  # Update the selector as needed
        if await page.is_visible(cookie_dialog_selector):
            logger.info("Aceptando cookies...")
            await page.click(cookie_dialog_selector)

        # Determinar el idioma del navegador
        language = await page.evaluate('''() => {
            return navigator.language || navigator.userLanguage;
        }''')

        # Hacer clic en el enlace 'All reviews' para ir a la sección de reseñas según el idioma
        if language.startswith('es'):
            await page.click("text='Reseñas'")
            logger.info("Haciendo clic en el enlace 'Reseñas' para ir a la sección de reseñas según el idioma...")
        else:
            await page.click("text='Reviews'")
            logger.info("Haciendo clic en el enlace 'Reviews' para ir a la sección de reseñas según el idioma...")

        logger.info("Esperando a que se cargue la página y las reseñas estén visibles...")

        # Esperar a que se carguen las reseñas
        await asyncio.sleep(1)  # Ajustar el tiempo de espera según sea necesario

        # Extraer el texto de las primeras 5 reseñas
        html = await page.inner_html('body')
        soup = BeautifulSoup(html, 'html.parser')
        review_elements = soup.select('.MyEned')
        reviews_text = [review.text.strip() for review in review_elements[:5]]

        # Si no hay reseñas, esperar un poco más y volver a intentarlo
        if not reviews_text:
            logger.info("No se encontraron reseñas. Esperando un poco más...")
            await asyncio.sleep(2)  # Esperar 2 segundos adicionales
            html = await page.inner_html('body')
            soup = BeautifulSoup(html, 'html.parser')
            review_elements = soup.select('.MyEned')
            #reviews_text = [review.text.strip() for review in review_elements[:5]]
            reviews_text = [review.find('span').text for review in reviews_text[:5]]

        logger.info("Cerrando el navegador...")
        await browser.close()
    
        overall_average_score, overall_sentiment_label = analyze_sentiment_severalReviews(reviews_text)
        logger.info("Análisis de sentimiento completado.")
        return {"overall_average_score": overall_average_score, "overall_sentiment_label": overall_sentiment_label}

@app.get('/')
async def read_root():
    return{"message": "Welcome to the review sentiment analysis API"}

