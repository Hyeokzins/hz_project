from flask import Flask, request, render_template

app = Flask(__name__)
text = None  # text를 전역 변수로 선언

@app.route('/', methods=['GET', 'POST'])
def index():
    global text  # 전역 변수 text를 사용
    if request.method == 'POST':
        text = request.form.get('text')
    return render_template('index.html', text=text)

if __name__ == '__main__':
    app.run()