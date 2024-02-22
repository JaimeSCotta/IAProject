from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests
from transformers import pipeline

app = FastAPI()

model_name = "mrcaelumn/yelp_restaurant_review_sentiment_analysis"
sentiment_pipeline = pipeline("text-classification", model=model_name)

custom_headers = {
    "Accept-language": "en-GB,en;q=0.9",     # aceptar textos en español "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
}

def get_soup(url):
    response = requests.get(url, headers=custom_headers)

    if response.status_code != 200:
        print("Error in getting webpage")
        exit(-1)

    soup = BeautifulSoup(response.text, "html.parser")
    return soup

def get_reviews_text(soup):
    review_elements = soup.select("div.review")

    reviews_text = []
    reviews_count = 0

    for review in review_elements:
        if reviews_count >= 5:
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

def analyze_sentiment_severalReviews(reviews: list):
    # Analizar el sentimiento de todas las revisiones
    predictions = [sentiment_pipeline(review) for review in reviews]
    
    # Calcular los puntajes promedio
    average_scores = []
    for prediction in predictions:
        scores = [p['score'] for p in prediction]
        average_score = sum(scores) / len(scores)
        average_scores.append(average_score)
    
    # Calcular la media de los puntajes promedio
    overall_average_score = sum(average_scores) / len(average_scores)
    
    # Mapear el puntaje promedio general
    overall_sentiment_label = map_score(overall_average_score)
    
    return overall_average_score, overall_sentiment_label

@app.get("/Predict sentiment form Amz reviews given the URL")
async def predict_Reviews_URL(url: str):
    # Obtener el HTML de la página web
    soup = get_soup(url)
    
    # Extraer el texto de las revisiones
    reviews_text = get_reviews_text(soup)
    
    # Analizar el sentimiento de las revisiones y calcular la media del puntaje
    overall_average_score, overall_sentiment_label = analyze_sentiment_severalReviews(reviews_text)
    
    # Devolver el puntaje promedio general y su etiqueta de sentimiento
    return {"overall_average_score": overall_average_score, "overall_sentiment_label": overall_sentiment_label}


@app.get('/')
async def read_root():
       return{"message": "Welcome to the review sentiment analysis API"}


#URL para probar: 
# https://www.amazon.com/BERIBES-Cancelling-Transparent-Soft-Earpads-Charging-Black/product-reviews/B0CDC4X65Q/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews
# Devuelve una MEDIA de las 5 primeras reseñas junto con la MEDIA de los sentimientos de estas


