from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd

app = FastAPI()

class review(BaseModel):
        Review: str


with open('model.pkl', 'rb') as f:
        model = pickle.load(f)


@app.get('/')
async def scoring_endpoint():
        return{"hello":"world"}

@app.post('/')
async def predictReviews(item:review):
        df = pd.DataFrame([item.dict().values()], colums=item.dict().keys())
        yhat = model.predict(df)
        return {"prediction":int(yhat)}