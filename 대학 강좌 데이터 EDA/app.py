import os
import pandas as pd
import gradio as gr
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import json

# Gemini API 설정
GEMINI_API_KEY = "AIzaSyA2w5PqQOn98wHaZy2MtiRkbxeHqrEYbTo"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')  # 최신 모델 사용

# 데이터 로드
DATA_PATH = r"C:\cheon\cheon_wokespace\homework\fast3\class.txt"
df = pd.read_csv(DATA_PATH, encoding='utf-8')

# 전역 스타일 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 한글 폰트
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
sns.set_palette("husl")

def get_basic_info():
    """기본 데이터 정보 조회"""
    info_str = f"""
    ### 📊 데이터셋 기본 정보
    
    **총 행 수:** {len(df)}
    **총 열 수:** {len(df.columns)}
    
    **컬럼 목록:**
    {', '.join(df.columns.tolist())}
    
    **데이터 타입:**
    {df.dtypes.to_string()}
    
    **결측치 확인:**
    {df.isnull().sum().to_string()}
    
    **첫 5개 행:**
    """
    return info_str, df.head(10)

def get_statistical_summary():
    """통계 요약 정보"""
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    
    summary_str = "### 📈 수치형 데이터 통계 요약\n\n"
    if len(numeric_cols) > 0:
        summary = df[numeric_cols].describe()
        summary_str += summary.to_string()
    else:
        summary_str += "수치형 데이터가 없습니다."
    
    # 범주형 데이터 요약
    categorical_str = "\n\n### 📋 범주형 데이터 요약\n\n"
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    for col in categorical_cols[:5]:  # 처음 5개 범주형 컬럼만
        categorical_str += f"\n**{col}의 고유값 수:** {df[col].nunique()}\n"
        categorical_str += f"**상위 5개 값:**\n{df[col].value_counts().head().to_string()}\n"
    
    return summary_str + categorical_str

def create_visualizations():
    """다양한 시각화 생성"""
    figures = []
    
    # 1. 학과별 강좌 수
    fig1 = plt.figure(figsize=(12, 6))
    dept_counts = df['개설학과'].value_counts()
    plt.barh(range(len(dept_counts)), dept_counts.values)
    plt.yticks(range(len(dept_counts)), dept_counts.index)
    plt.xlabel('강좌 수')
    plt.ylabel('개설학과')
    plt.title('학과별 강좌 수')
    plt.tight_layout()
    figures.append(fig1)
    
    # 2. 수강인원 분포
    fig2 = plt.figure(figsize=(10, 6))
    plt.hist(df['수강인원'], bins=20, edgecolor='black', alpha=0.7)
    plt.xlabel('수강인원')
    plt.ylabel('빈도')
    plt.title('수강인원 분포')
    plt.axvline(df['수강인원'].mean(), color='red', linestyle='--', label=f'평균: {df["수강인원"].mean():.1f}')
    plt.legend()
    plt.tight_layout()
    figures.append(fig2)
    
    # 3. 학년별 강좌 수
    fig3 = plt.figure(figsize=(8, 6))
    grade_counts = df['개설학년'].value_counts().sort_index()
    plt.bar(grade_counts.index.astype(str), grade_counts.values, color='skyblue', edgecolor='black')
    plt.xlabel('개설학년')
    plt.ylabel('강좌 수')
    plt.title('학년별 강좌 수')
    plt.tight_layout()
    figures.append(fig3)
    
    # 4. 교수별 강좌 수 (상위 10명)
    fig4 = plt.figure(figsize=(12, 6))
    prof_counts = df['강좌대표교수'].value_counts().head(10)
    plt.barh(range(len(prof_counts)), prof_counts.values, color='coral')
    plt.yticks(range(len(prof_counts)), prof_counts.index)
    plt.xlabel('강좌 수')
    plt.ylabel('교수명')
    plt.title('강좌 수 상위 10명 교수')
    plt.tight_layout()
    figures.append(fig4)
    
    # 5. 학점별 강좌 수
    fig5 = plt.figure(figsize=(8, 6))
    credit_counts = df['교과목학점'].value_counts().sort_index()
    plt.bar(credit_counts.index.astype(str), credit_counts.values, color='lightgreen', edgecolor='black')
    plt.xlabel('학점')
    plt.ylabel('강좌 수')
    plt.title('학점별 강좌 수')
    plt.tight_layout()
    figures.append(fig5)
    
    # 6. 수업주수별 강좌 수
    fig6 = plt.figure(figsize=(8, 6))
    weeks_counts = df['수업주수'].value_counts().sort_index()
    plt.bar(weeks_counts.index.astype(str), weeks_counts.values, color='plum', edgecolor='black')
    plt.xlabel('수업주수')
    plt.ylabel('강좌 수')
    plt.title('수업주수별 강좌 수')
    plt.tight_layout()
    figures.append(fig6)
    
    return figures

def create_interactive_plots():
    """Plotly를 사용한 인터랙티브 시각화"""
    plots = []
    
    # 1. 학과별 평균 수강인원
    dept_avg = df.groupby('개설학과')['수강인원'].mean().sort_values(ascending=True)
    fig1 = go.Figure(data=[
        go.Bar(x=dept_avg.values, y=dept_avg.index, orientation='h',
               marker=dict(color=dept_avg.values, colorscale='Viridis'))
    ])
    fig1.update_layout(title='학과별 평균 수강인원',
                       xaxis_title='평균 수강인원',
                       yaxis_title='개설학과',
                       height=500)
    plots.append(fig1)
    
    # 2. 과정별 강좌 분포 (파이 차트)
    course_counts = df['과정'].value_counts()
    fig2 = go.Figure(data=[
        go.Pie(labels=course_counts.index, values=course_counts.values,
               hole=0.3)
    ])
    fig2.update_layout(title='과정별 강좌 분포', height=500)
    plots.append(fig2)
    
    # 3. 학년별 평균 수강인원
    grade_avg = df.groupby('개설학년')['수강인원'].agg(['mean', 'min', 'max'])
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name='평균', x=grade_avg.index, y=grade_avg['mean']))
    fig3.add_trace(go.Scatter(name='최소', x=grade_avg.index, y=grade_avg['min'], mode='lines+markers'))
    fig3.add_trace(go.Scatter(name='최대', x=grade_avg.index, y=grade_avg['max'], mode='lines+markers'))
    fig3.update_layout(title='학년별 수강인원 통계',
                       xaxis_title='개설학년',
                       yaxis_title='수강인원',
                       height=500)
    plots.append(fig3)
    
    return plots

def gemini_analyze_data(question):
    """Gemini API를 사용한 데이터 분석"""
    try:
        # 데이터 요약 정보 생성
        data_summary = f"""
        다음은 대학 강좌 데이터입니다:
        
        총 강좌 수: {len(df)}
        
        학과별 강좌 수:
        {df['개설학과'].value_counts().to_string()}
        
        수강인원 통계:
        - 평균: {df['수강인원'].mean():.1f}명
        - 최소: {df['수강인원'].min()}명
        - 최대: {df['수강인원'].max()}명
        - 중앙값: {df['수강인원'].median():.1f}명
        
        학년별 분포:
        {df['개설학년'].value_counts().sort_index().to_string()}
        
        교과목학점 분포:
        {df['교과목학점'].value_counts().sort_index().to_string()}
        
        수업주수 분포:
        {df['수업주수'].value_counts().sort_index().to_string()}
        
        과정 유형:
        {df['과정'].value_counts().to_string()}
        
        상위 5개 교과목:
        {df['교과목명'].value_counts().head().to_string()}
        """
        
        prompt = f"""
        {data_summary}
        
        사용자 질문: {question}
        
        위 데이터를 바탕으로 사용자의 질문에 대해 상세하고 통찰력 있는 답변을 한국어로 제공해주세요.
        데이터의 패턴, 트렌드, 특이사항 등을 분석하여 답변해주세요.
        """
        
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        return f"분석 중 오류가 발생했습니다: {str(e)}"

def gemini_generate_insights():
    """Gemini를 사용한 자동 인사이트 생성"""
    try:
        data_summary = f"""
        대학 강좌 데이터 분석:
        
        총 강좌 수: {len(df)}
        개설학과 수: {df['개설학과'].nunique()}
        
        학과별 강좌 수:
        {df['개설학과'].value_counts().head(10).to_string()}
        
        수강인원 통계:
        - 평균: {df['수강인원'].mean():.1f}명
        - 표준편차: {df['수강인원'].std():.1f}명
        - 최소: {df['수강인원'].min()}명
        - 최대: {df['수강인원'].max()}명
        
        교수별 강좌 수 (상위 5명):
        {df['강좌대표교수'].value_counts().head().to_string()}
        
        학점별 분포:
        {df['교과목학점'].value_counts().sort_index().to_string()}
        
        수업주수별 분포:
        {df['수업주수'].value_counts().sort_index().to_string()}
        """
        
        prompt = f"""
        {data_summary}
        
        위 대학 강좌 데이터를 분석하여 다음 내용을 포함한 상세한 인사이트를 한국어로 제공해주세요:
        
        1. 데이터의 전반적인 특징
        2. 주목할만한 패턴이나 트렌드
        3. 학과별 특성 분석
        4. 수강인원의 분포 특성
        5. 개선이나 최적화를 위한 제안사항
        
        분석은 구체적이고 실용적으로 작성해주세요.
        """
        
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        return f"인사이트 생성 중 오류가 발생했습니다: {str(e)}"

def search_courses(keyword):
    """교과목 검색"""
    if not keyword:
        return df.head(20)
    
    mask = (df['교과목명'].str.contains(keyword, case=False, na=False) |
            df['개설학과'].str.contains(keyword, case=False, na=False) |
            df['강좌대표교수'].str.contains(keyword, case=False, na=False))
    
    result = df[mask]
    return result if len(result) > 0 else pd.DataFrame({"결과": ["검색 결과가 없습니다."]})

# Gradio 인터페이스 구성
with gr.Blocks(title="대학 강좌 데이터 EDA", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎓 대학 강좌 데이터 탐색적 분석 (EDA)
    ### Powered by Google Gemini AI
    
    이 애플리케이션은 대학 강좌 데이터를 분석하고 AI 기반 인사이트를 제공합니다.
    """)
    
    with gr.Tabs():
        # 탭 1: 기본 정보
        with gr.Tab("📊 기본 정보"):
            gr.Markdown("## 데이터셋 기본 정보")
            info_btn = gr.Button("데이터 정보 보기", variant="primary")
            info_text = gr.Markdown()
            info_table = gr.Dataframe()
            
            info_btn.click(
                fn=get_basic_info,
                outputs=[info_text, info_table]
            )
        
        # 탭 2: 통계 요약
        with gr.Tab("📈 통계 요약"):
            gr.Markdown("## 데이터 통계 분석")
            stats_btn = gr.Button("통계 요약 보기", variant="primary")
            stats_output = gr.Markdown()
            
            stats_btn.click(
                fn=get_statistical_summary,
                outputs=stats_output
            )
        
        # 탭 3: 시각화
        with gr.Tab("📉 시각화"):
            gr.Markdown("## 데이터 시각화")
            viz_btn = gr.Button("시각화 생성", variant="primary")
            
            with gr.Row():
                plot1 = gr.Plot(label="학과별 강좌 수")
                plot2 = gr.Plot(label="수강인원 분포")
            
            with gr.Row():
                plot3 = gr.Plot(label="학년별 강좌 수")
                plot4 = gr.Plot(label="교수별 강좌 수")
            
            with gr.Row():
                plot5 = gr.Plot(label="학점별 강좌 수")
                plot6 = gr.Plot(label="수업주수별 강좌 수")
            
            viz_btn.click(
                fn=create_visualizations,
                outputs=[plot1, plot2, plot3, plot4, plot5, plot6]
            )
        
        # 탭 4: 인터랙티브 차트
        with gr.Tab("📊 인터랙티브 차트"):
            gr.Markdown("## 인터랙티브 데이터 시각화 (Plotly)")
            interactive_btn = gr.Button("인터랙티브 차트 생성", variant="primary")
            
            iplot1 = gr.Plot(label="학과별 평균 수강인원")
            iplot2 = gr.Plot(label="과정별 강좌 분포")
            iplot3 = gr.Plot(label="학년별 수강인원 통계")
            
            interactive_btn.click(
                fn=create_interactive_plots,
                outputs=[iplot1, iplot2, iplot3]
            )
        
        # 탭 5: AI 분석
        with gr.Tab("🤖 AI 분석 (Gemini)"):
            gr.Markdown("## Gemini AI 기반 데이터 분석")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 💡 자동 인사이트 생성")
                    insights_btn = gr.Button("AI 인사이트 생성", variant="primary")
                    insights_output = gr.Markdown()
                    
                    insights_btn.click(
                        fn=gemini_generate_insights,
                        outputs=insights_output
                    )
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### ❓ 데이터에 대해 질문하기")
                    question_input = gr.Textbox(
                        label="질문을 입력하세요",
                        placeholder="예: 수강인원이 가장 많은 학과는 어디인가요?",
                        lines=3
                    )
                    analyze_btn = gr.Button("AI에게 질문하기", variant="primary")
                    answer_output = gr.Markdown()
                    
                    analyze_btn.click(
                        fn=gemini_analyze_data,
                        inputs=question_input,
                        outputs=answer_output
                    )
        
        # 탭 6: 검색
        with gr.Tab("🔍 강좌 검색"):
            gr.Markdown("## 강좌 검색")
            search_input = gr.Textbox(
                label="검색어",
                placeholder="교과목명, 학과명, 교수명으로 검색"
            )
            search_btn = gr.Button("검색", variant="primary")
            search_output = gr.Dataframe()
            
            search_btn.click(
                fn=search_courses,
                inputs=search_input,
                outputs=search_output
            )
    
    gr.Markdown("""
    ---
    ### 📝 사용 가이드
    - **기본 정보**: 데이터셋의 기본 구조와 샘플 데이터 확인
    - **통계 요약**: 수치형 및 범주형 데이터의 통계적 요약
    - **시각화**: 다양한 각도에서의 데이터 시각화 (Matplotlib)
    - **인터랙티브 차트**: 상호작용 가능한 차트 (Plotly)
    - **AI 분석**: Gemini AI를 활용한 인사이트 생성 및 질의응답
    - **강좌 검색**: 키워드로 강좌 정보 검색
    """)

# 애플리케이션 실행
if __name__ == "__main__":
    demo.launch(
        share=True,  # 외부 공개 링크 생성
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )

