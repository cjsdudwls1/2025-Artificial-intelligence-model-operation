import gradio as gr
import requests
import json

# 서버 URL 설정
SERVER_URL = "http://localhost:8004"

def predict_iris_client(sepal_length, sepal_width, petal_length, petal_width):
    """FastAPI 서버에 예측 요청을 보내는 클라이언트 함수"""
    try:
        # FastAPI 서버에 POST 요청
        response = requests.post(
            f"{SERVER_URL}/predict",
            json={
                "sepal_length": sepal_length,
                "sepal_width": sepal_width,
                "petal_length": petal_length,
                "petal_width": petal_width
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return f"예측 결과: {result['prediction']}"
        else:
            return f"오류 발생: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요."
    except Exception as e:
        return f"오류: {str(e)}"

# Gradio 클라이언트 인터페이스
iface = gr.Interface(
    fn=predict_iris_client,
    inputs=[
        gr.Slider(0, 10, 5.1, label="꽃받침 길이"),
        gr.Slider(0, 10, 3.5, label="꽃받침 너비"),
        gr.Slider(0, 10, 1.4, label="꽃잎 길이"),
        gr.Slider(0, 10, 0.2, label="꽃잎 너비"),
    ],
    outputs=gr.Textbox(label="예측 결과"),
    title="붓꽃 품종 예측 클라이언트",
    description="FastAPI 서버에 연결하여 붓꽃 품종을 예측합니다."
)

if __name__ == "__main__":
    # Gradio 클라이언트 실행 (포트 7861)
    iface.launch(server_port=7861, share=False)
