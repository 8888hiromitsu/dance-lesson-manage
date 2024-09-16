import openai
import matplotlib.pyplot as plt
import io
import base64
from flask import Markup, current_app
from app.models import Survey, Lesson

def analyze_data_with_gpt(instructor_id):
    openai.api_key = current_app.config['OPENAI_API_KEY']
    
    # データを取得
    lessons = Lesson.query.filter_by(instructor_id=instructor_id).all()
    surveys = Survey.query.filter(Survey.lesson_id.in_([lesson.id for lesson in lessons])).all()

    # データを基にプロンプトを生成
    prompt = "次のデータを元に、レッスンの改善提案を出してください。データ: " + str([survey.satisfaction for survey in surveys])

    # ChatGPT APIを使って提案を生成
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    
    proposal = response.choices[0].text.strip()

    # 仮のグラフ作成
    dates = [lesson.date.strftime("%Y-%m-%d") for lesson in lessons]
    satisfactions = [survey.satisfaction for survey in surveys]

    fig, ax = plt.subplots()
    ax.plot(dates, satisfactions, marker='o')
    ax.set_title('Satisfaction Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Satisfaction')

    # グラフをバイナリデータとして保存
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return proposal, Markup(f'<img src="data:image/png;base64,{plot_url}" alt="Proposal Chart">")
