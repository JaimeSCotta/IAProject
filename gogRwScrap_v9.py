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

async def extract_reviews(page):
    logger.info("Esperando a que aparezcan las reseñas...")
    await page.wait_for_selector('.MyEned')
    logger.info("Las reseñas están disponibles. Extrayendo...")
    html = await page.inner_html('body')
    soup = BeautifulSoup(html, 'html.parser')
    review_elements = soup.select('.MyEned')
    reviews_text = [review.text.strip() for review in review_elements]
    logger.info(f"Se han extraído {len(reviews_text)} reseñas.")
    return reviews_text

async def scrape_with_retry(url):
    attempt = 0
    while attempt < 3:
        try:
            logger.info(f"Iniciando intento de scraping ({attempt + 1})...")
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                logger.info(f"Navegando a la URL: {url}")
                await page.goto(url)
                cookie_dialog_selector = 'text="Aceptar todo"'
                if await page.is_visible(cookie_dialog_selector):
                    logger.info("Aceptando cookies...")
                    await page.click(cookie_dialog_selector)
                reviews = await extract_reviews(page)
                logger.info("Cerrando el navegador...")
                await browser.close()
                logger.info("Extracción completada con éxito.")
                return reviews
        except Exception as e:
            logger.error(f"Error en el intento {attempt + 1}: {e}")
            attempt += 1
            logger.info(f"Reintentando en {2 ** attempt} segundos...")
            await asyncio.sleep(2 ** attempt)  # Backoff exponencial
    raise Exception("No se pudo completar la extracción después de varios intentos.")

@app.get("/scrape_google_reviews")
async def scrape_google_reviews(url: str = Query(..., description="URL del restaurante específico")):
    logger.info("Iniciando scraping de reseñas de Google...")
    try:
        reviews = await scrape_with_retry(url)
        overall_average_score, overall_sentiment_label = analyze_sentiment_severalReviews(reviews)
        logger.info("Análisis de sentimiento completado.")
        return {"overall_average_score": overall_average_score, "overall_sentiment_label": overall_sentiment_label}
    except Exception as e:
        logger.error(f"Error durante el scraping: {e}")
        return {"error": str(e)}

@app.get('/')
async def read_root():
    return {"message": "Welcome to the review sentiment analysis API"}

# Si se ejecuta esta app desde un SO Windows, se tiene que hacer "uvicorn gogRwScrap_v9:app" 
# en caso de querer utilizar la opcion "--reload" de uvicorn usar la version 10 de este codigo.
# El error NotImplementedError es un problema conocido al usar asyncio y operaciones de subproceso en Windows, especialmente con Python 3.8 y versiones posteriores.

