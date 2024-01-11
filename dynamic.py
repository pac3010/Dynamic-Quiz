from flask import Flask, render_template, request, url_for, redirect,flash, session, jsonify
from datetime import datetime
from db_handler import *
import requests

date = datetime.now()

app = Flask(__name__)
app.secret_key = ''

@app.route('/')
@app.route('/index')
def index(name='index'):
    return render_template('index.html', name=name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password do not match. Please try again.', 'error')
            return redirect ('/register')
        if is_username_exists(nickname):
            flash('Username already exists. Please choose another username.', 'error')
            return redirect('/register')
        
        add_user(nickname, password)
        flash('Registration Successful!', 'success')
        return redirect('/register')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']

        user_id = get_id(nickname)

        if user_id and verify_login(nickname, password):
            session['nickname'] = nickname
            session['user_id'] = user_id
            print(session)
            
            return redirect(url_for('index'))
        else:
            flash('Sorry, the account information you entered is incorrect. Please try again', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    print(session)
    session.pop('nickname', None)
    print(session)
    return redirect(url_for('index'))

@app.route('/leaderboard')
def leaderboard():
    leaderboard_data = get_leaderboard_data()
    return render_template('leaderboard.html', users=leaderboard_data)

@app.route('/weather', methods=['GET', 'POST'])
def getWeather():
    if request.method == 'POST':
        city = request.form.get('city')
        api_key = 'a7e5e03016424475adb145437232412'
        api_url = f'https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=3'

        response = requests.get(api_url)
        weather_data= response.json()

        forecast = weather_data.get('forecast', {}).get('forecastday', [])[:3]

        return render_template('weather.html', weather=forecast, city=city)
    return 'ERROR 405', 405

@app.route('/get_question')
def get_question():
    if 'current_question' in session:
        del session['current_question'] 

    question = get_random_question()
    session['current_question'] = question['id']  
    return jsonify(question)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'current_question' not in session:
        return jsonify({'error': 'No question set'})

    user_answer = int(request.form['user_answer'])
    correct_answer = get_correct_answer(session['current_question'])
    score_change = 0

    if user_answer == correct_answer:
        score_change = 10
    else:
        score_change = 0
    
    user_id=session.get('user_id')
    update_leaderboard(user_id, score_change)

    question = get_random_question()
    session['current_question'] = question['id']
    return jsonify(question)

@app.route('/quiz')
def quiz():
    question = get_random_question()  
    session['current_question'] = question['id']
    return render_template('quiz.html', question=question)

@app.route('/get_user_score')
def get_user_score():
    user_nickname = session.get('nickname') 
    print(user_nickname)
    
    if user_nickname:  
        user_id = get_id(user_nickname)
        score = get_score(user_id)
        return jsonify({'score': score})
    else:
        return jsonify({'error': 'Nickname not found in session'})

