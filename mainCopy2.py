from fastapi import FastAPI, HTTPException
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

class review(BaseModel):
        Review: str

class url(BaseModel):
        URL: str

model_name = "mrcaelumn/yelp_restaurant_review_sentiment_analysis"
sentiment_pipeline = pipeline("text-classification", model=model_name)

def map_label(label):
    if label == "LABEL_2":
        return "POSITIVE"
    elif label == "LABEL_1":
        return "NEUTRAL"
    elif label == "LABEL_0":
        return "NEGATIVE"
    else:
        return "UNKNOWN"
    
def map_score(score):
    if score >= 0.5:
        return "POSITIVE"
    elif score <= 0.4:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

import logging

# Configurar el sistema de registro
logging.basicConfig(level=logging.INFO)

def extract_reviews_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        reviews = []
        review_elements = soup.find_all("p", class_="partial_entry")[:5]  # Limitar a las primeras 5 revisiones
        for element in review_elements:
            review_text = element.text.strip()
            reviews.append(review_text)
            # Registrar la revisión obtenida
            logging.info(f"Obtenida revisión: {review_text}")
        return reviews
    else:
        # Registrar el error de solicitud
        logging.error(f"Error al obtener la página: {response.status_code}")
        return None


def analyze_sentiment(item: review):
    predictions = sentiment_pipeline(item.Review)
    mapped_predictions = [{'label': map_label(prediction['label']), 'score': prediction['score']} for prediction in predictions]
    return mapped_predictions

def analyze_sentiment_severalReviews(item: str):
    predictions = sentiment_pipeline(item)
    scores = [prediction['score'] for prediction in predictions]
    average_score = sum(scores) / len(scores)
    label = map_score(average_score)
    return average_score, label
    

@app.get('/')
async def read_root():
       return{"message": "Welcome to the review sentiment analysis API"}


@app.post('/Predict reviews from Raw Text')
async def predict_Reviews_raw(item: review):
    return analyze_sentiment(item)

    
@app.post("/Predict reviews from URL")
async def predict_Reviews_URL(url: url):
    reviews = extract_reviews_from_url(url.URL)
    if reviews: 
        average_scores, label = [analyze_sentiment_severalReviews(review) for review in reviews]
        overall_average_score = sum(average_scores) / len(average_scores)
        overall_sentiment_label = [{'label': label, 'score': overall_average_score}]
        return overall_sentiment_label
    else:
        raise HTTPException(status_code=404, detail="No reviews found on the provided URL")


@app.post("/Predict reviews from URL v2")
async def predict_Reviews_URL(url: url):
    reviews = extract_reviews_from_url(url.URL)
    if reviews: 
        average_scores_and_labels = [analyze_sentiment_severalReviews(review) for review in reviews]
        average_scores = [score for score, _ in average_scores_and_labels]
        overall_average_score = sum(average_scores) / len(average_scores)
        overall_sentiment_label = map_score(overall_average_score)
        return {'label': overall_sentiment_label, 'score': overall_average_score}
    else:
        raise HTTPException(status_code=404, detail="No reviews found on the provided URL")





       