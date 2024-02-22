from fastapi import FastAPI, HTTPException
from bs4 import BeautifulSoup
import requests
from transformers import pipeline

app = FastAPI()

# Configuración del modelo de análisis de sentimientos
model_name = "mrcaelumn/yelp_restaurant_review_sentiment_analysis"
sentiment_pipeline = pipeline("text-classification", model=model_name)

# Encabezados HTTP para las solicitudes
custom_headers = {
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
}

def get_soup(url):
    response = requests.get(url, headers=custom_headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error en obtener la página web")
    return BeautifulSoup(response.text, "html.parser")

def get_reviews_text(soup):
    review_elements = soup.select("div.review")
    reviews_text = []
    reviews_count = 0
    for review in review_elements:
        if reviews_count >= 5:  # Límite de 5 revisiones
            break
        r_content_element = review.select_one("span.review-text")
        r_content = r_content_element.text.strip() if r_content_element else None
        if r_content:
            reviews_text.append(r_content)
            reviews_count += 1
    return reviews_text

def map_score(score):
    if score >= 0.5:
        return "POSITIVE"
    elif score <= 0.4:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

def analyze_sentiment(review):
    predictions = sentiment_pipeline(review)
    scores = [prediction['score'] for prediction in predictions]
    average_score = sum(scores) / len(scores)
    label = map_score(average_score)
    return {'average_score': average_score, 'label': label}

@app.get("/scrape-reviews/")
async def scrape_reviews(url: str):
    try:
        soup = get_soup(url)
        reviews_text = get_reviews_text(soup)
        if not reviews_text:
            raise HTTPException(status_code=404, detail="No se encontraron revisiones en la página")
        sentiments = [analyze_sentiment(review) for review in reviews_text]
        return {"reviews": reviews_text, "sentiments": sentiments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/')
async def read_root():
       return{"message": "Welcome to the review sentiment analysis API"}

# URL para probar: 
# https://www.amazon.com/BERIBES-Cancelling-Transparent-Soft-Earpads-Charging-Black/product-reviews/B0CDC4X65Q/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews
# Devuelve las 5 reseñas por separado junto con los 5 sentimientos de estas