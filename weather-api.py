from flask import Flask, redirect, url_for, flash, render_template, request
import sys
import requests
from flask_sqlalchemy import SQLAlchemy
import os

key = os.urandom(24)  # specify the length in brackets
app = Flask(__name__)
app.config['SECRET_KEY'] = key
api_key = "6b8c9e17276ea55d906eee4e23c8367b"
URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route('/', methods=['POST', 'GET'])
def index():
    weathers = []
    if request.method == 'GET':
        for city in City.query.all():
            city_name, city_id = city.name, city.id
            r = requests.get(URL, params={'q': city_name, 'appid': api_key})
            json_data = r.json()
            temperature = round(int(json_data['main']['temp']) - 273.15)
            weather_state = json_data['weather'][0]['main']
            weather_dict = {"city_name": city_name,
                            "current_temperature": temperature,
                            "weather_state": weather_state,
                            "city_id": city_id}
            weathers.append(weather_dict)
        return render_template('index.html', weathers=weathers)


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


@app.route('/profile')
def profile():
    return 'This is profile page'


@app.route('/login')
def log_in():
    return 'This is login page'


@app.route('/add', methods=['POST', 'GET'])
def add_city():
    if request.method == 'POST':
        city_name = request.form.get('city_name')
        r = requests.get(URL, params={'q': city_name, 'appid': api_key})
        json_data = r.json()
        cod = int(json_data['cod'])
        if cod != 200:
            flash("The city doesn't exist!")
            return redirect('/')
        if City.query.filter_by(name=city_name).first() is not None:
            flash("The city has already been added to the list!")
            return redirect('/')
        city = City(name=city_name)
        db.session.add(city)
        db.session.commit()
        return redirect(url_for('index'))


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return self.name + " " + str(self.id)


db.create_all()


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
