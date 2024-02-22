from fastapi import FastAPI, HTTPException
from typing import Union
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

class review(BaseModel):
        Review: str

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

def extract_reviews_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        reviews = []
        review_elements = soup.find_all("p", class_="partial_entry")  # Adjust based on Tripadvisor HTML structure
        for element in review_elements:
            reviews.append(element.text.strip())
        return reviews
    else:
        return None

def analyze_sentiment(item: review):
    predictions = sentiment_pipeline(item.Review)
    mapped_predictions = [{'label': map_label(prediction['label']), 'score': prediction['score']} for prediction in predictions]
    return mapped_predictions
    

@app.get('/')
async def read_root():
       return{"message": "Welcome to the review sentiment analysis API"}


@app.post('/predict_reviews')
async def predict_Reviews(item: review):
    return analyze_sentiment(item)


@app.post("/predict_reviews_URL")
async def predict_Reviews_v2(review: Union[str, dict]):
    if isinstance(review, str):  # If plain text review
        review_obj = review(Review=review)  # Create a dictionary with the review string
        return analyze_sentiment(review_obj)
    
    elif isinstance(review, dict) and "url" in review:  # If URL provided
        url = review["url"]
        reviews = extract_reviews_from_url(url)
        if reviews:
            sentiments = [analyze_sentiment(review) for review in reviews]
            return {"sentiments": sentiments}
        else:
            raise HTTPException(status_code=404, detail="No reviews found on the provided URL")
    else:
        raise HTTPException(status_code=400, detail="Invalid request")





       