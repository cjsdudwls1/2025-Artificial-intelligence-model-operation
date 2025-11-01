import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import pickle
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# 데이터 로딩 및 모델 학습
iris = load_iris()
X = iris.data
y = iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 학습
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# 모델 저장
with open('iris_model.pkl', 'wb') as f:
    pickle.dump(model, f)

# 모델 로드
with open('iris_model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

# 예측 함수
def predict_iris(sepal_length, sepal_width, petal_length, petal_width):
    input_data = [[sepal_length, sepal_width, petal_length, petal_width]]
    prediction = loaded_model.predict(input_data)[0]
    return iris.target_names[prediction]

# Pydantic 모델 정의
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# FastAPI 앱
app = FastAPI(title="붓꽃 예측 API")

@app.get("/")
def root():
    return {"message": "붓꽃 예측 API"}

@app.post("/predict")
def predict(data: IrisInput):
    result = predict_iris(data.sepal_length, data.sepal_width, data.petal_length, data.petal_width)
    return {"prediction": result}

if __name__ == "__main__":
    # FastAPI 서버만 실행 (포트 8004)
    uvicorn.run(app, host="0.0.0.0", port=8004)