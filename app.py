from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

app = FastAPI()

class review(BaseModel):
    Review: str

# Pre-download the model
model_name = "mrcaelumn/yelp_restaurant_review_sentiment_analysis"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
sentiment_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)

def map_label(label):
    if label == "LABEL_2":
        return "POSITIVE"
    elif label == "LABEL_1":
        return "NEUTRAL"
    elif label == "LABEL_0":
        return "NEGATIVE"
    else:
        return "UNKNOWN"

@app.get('/')
async def read_root():
       return{"message": "Welcome to the review sentiment analysis API"}

@app.post('/')
async def predictReviews(item: review):
    predictions = sentiment_pipeline(item.Review)
    mapped_predictions = [{'label': map_label(prediction['label']), 'score': prediction['score']} for prediction in predictions]
    return mapped_predictions
