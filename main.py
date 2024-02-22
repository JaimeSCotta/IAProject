from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd
from transformers import pipeline

app = FastAPI()

class review(BaseModel):
        Review: str


'''with open('model.pkl', 'rb') as f:
        model = pickle.load(f)'''

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
    

@app.get('/')
async def read_root():
       return{"message": "Welcome to the review sentiment analysis API"}

@app.post('/')
async def predict_Reviews(item: review):
    predictions = sentiment_pipeline(item.Review)
    mapped_predictions = [{'label': map_label(prediction['label']), 'score': prediction['score']} for prediction in predictions]
    return mapped_predictions


        #df = pd.DataFrame([item.dict().values()], colums=item.dict().keys())
        #yhat = model.predict(df)
        #return {"prediction":int(yhat)}
       