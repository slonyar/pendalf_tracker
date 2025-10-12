from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateTimeField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gandalf-secret-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fellowship_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    race = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # active, inactive, lost
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    locations = db.relationship('Location', backref='character', lazy=True, cascade='all, delete-orphan')

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    location_name = db.Column(db.String(200))  # Например: "Шир", "Ривенделл", "Мория"

class CharacterForm(FlaskForm):
    name = StringField('Имя персонажа', validators=[DataRequired()])
    description = TextAreaField('Описание')
    race = SelectField('Раса', choices=[
        ('hobbit', 'Хоббит'),
        ('human', 'Человек'),
        ('elf', 'Эльф'),
        ('dwarf', 'Гном'),
        ('wizard', 'Маг'),
        ('other', 'Другое')
    ])

class LocationForm(FlaskForm):
    character_id = SelectField('Персонаж', coerce=int, validators=[DataRequired()])
    latitude = FloatField('Широта', validators=[DataRequired(), NumberRange(-90, 90)])
    longitude = FloatField('Долгота', validators=[DataRequired(), NumberRange(-180, 180)])
    timestamp = DateTimeField('Дата и время', validators=[DataRequired()], default=datetime.now)
    location_name = StringField('Название места')
    notes = TextAreaField('Заметки')

@app.route('/')
def index():
    characters = Character.query.all()
    recent_locations = db.session.query(Location).join(Character).order_by(Location.timestamp.desc()).limit(10).all()
    return render_template('index.html', characters=characters, recent_locations=recent_locations)

@app.route('/characters')
def characters():
    characters = Character.query.all()
    return render_template('characters.html', characters=characters)

@app.route('/add_character', methods=['GET', 'POST'])
def add_character():
    form = CharacterForm()
    if form.validate_on_submit():
        character = Character(
            name=form.name.data,
            description=form.description.data,
            race=form.race.data
        )
        db.session.add(character)
        db.session.commit()
        flash(f'Персонаж {character.name} добавлен!', 'success')
        return redirect(url_for('index'))
    return render_template('add_character.html', form=form)

@app.route('/add_location', methods=['GET', 'POST'])
def add_location():
    characters = Character.query.all()
    
    if request.method == 'POST':
        try:
            character_id = request.form.get('character_id')
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            timestamp_str = request.form.get('timestamp')
            location_name = request.form.get('location_name', '')
            notes = request.form.get('notes', '')
            
            print(f"Debug - Received data:")
            print(f"  character_id: {character_id}")
            print(f"  latitude: {latitude}")
            print(f"  longitude: {longitude}")
            print(f"  timestamp_str: '{timestamp_str}'")
            
            # Проверяем обязательные поля
            if not character_id:
                flash('Выберите персонажа!', 'error')
                return render_template('add_location_simple.html', characters=characters)
            
            if not latitude or not longitude:
                flash('Укажите координаты!', 'error')
                return render_template('add_location_simple.html', characters=characters)
            
            # Обрабатываем timestamp (поддерживаем разные форматы)
            if timestamp_str and timestamp_str.strip():
                try:
                    # Формат от Flatpickr: "2024-12-19 15:30"
                    if ' ' in timestamp_str and 'T' not in timestamp_str:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M')
                    # Формат datetime-local: "2024-12-19T15:30"
                    elif 'T' in timestamp_str:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M')
                    # ISO формат
                    else:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    print(f"  parsed timestamp: {timestamp}")
                except ValueError as e:
                    print(f"  timestamp parse error: {e}")
                    timestamp = datetime.now()
                    flash('Некорректная дата, использовано текущее время', 'warning')
            else:
                timestamp = datetime.now()
                print(f"  using current timestamp: {timestamp}")
            
            location = Location(
                character_id=int(character_id),
                latitude=float(latitude),
                longitude=float(longitude),
                timestamp=timestamp,
                location_name=location_name,
                notes=notes
            )
            
            db.session.add(location)
            db.session.commit()
            
            character_name = Character.query.get(character_id).name
            location_display = location_name if location_name else f"координаты {latitude}, {longitude}"
            flash(f'📍 Местоположение "{location_display}" для {character_name} добавлено!', 'success')
            return redirect(url_for('index'))
            
        except ValueError as e:
            flash(f'Ошибка в данных: {str(e)}', 'error')
            print(f"ValueError: {e}")
        except Exception as e:
            flash(f'Ошибка при добавлении местоположения: {str(e)}', 'error')
            print(f"Exception: {e}")
            db.session.rollback()
    
    return render_template('add_location_simple.html', characters=characters)

@app.route('/map')
def map_view():
    characters = Character.query.all()
    return render_template('map.html', characters=characters)

@app.route('/api/locations')
def api_locations():
    character_id = request.args.get('character_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Location.query.join(Character)
    
    if character_id:
        query = query.filter(Location.character_id == character_id)
    
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(Location.timestamp >= start)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(Location.timestamp <= end)
    
    locations = query.order_by(Location.timestamp).all()
    
    return jsonify([{
        'id': loc.id,
        'character_id': loc.character_id,
        'character_name': loc.character.name,
        'character_race': loc.character.race,
        'latitude': loc.latitude,
        'longitude': loc.longitude,
        'timestamp': loc.timestamp.isoformat(),
        'location_name': loc.location_name,
        'notes': loc.notes
    } for loc in locations])

@app.route('/api/characters')
def api_characters():
    characters = Character.query.all()
    return jsonify([{
        'id': char.id,
        'name': char.name,
        'description': char.description,
        'race': char.race,
        'status': char.status,
        'location_count': len(char.locations)
    } for char in characters])

@app.route('/character/<int:character_id>')
def character_detail(character_id):
    character = Character.query.get_or_404(character_id)
    locations = Location.query.filter_by(character_id=character_id).order_by(Location.timestamp.desc()).all()
    return render_template('character_detail.html', character=character, locations=locations)

@app.route('/delete_character/<int:character_id>', methods=['POST'])
def delete_character(character_id):
    character = Character.query.get_or_404(character_id)
    db.session.delete(character)
    db.session.commit()
    flash(f'Персонаж {character.name} удален!', 'success')
    return redirect(url_for('characters'))

def init_sample_data():
    """Инициализация примерных данных"""
    if Character.query.count() == 0:
        characters_data = [
            {'name': 'Фродо Бэггинс', 'race': 'hobbit', 'description': 'Хранитель Кольца'},
            {'name': 'Сэмуайз Гэмджи', 'race': 'hobbit', 'description': 'Верный друг Фродо'},
            {'name': 'Арагорн', 'race': 'human', 'description': 'Следопыт, наследник Исилдура'},
            {'name': 'Леголас', 'race': 'elf', 'description': 'Эльф из Лесного царства'},
            {'name': 'Гимли', 'race': 'dwarf', 'description': 'Гном из Одинокой горы'},
            {'name': 'Боромир', 'race': 'human', 'description': 'Сын наместника Гондора'},
            {'name': 'Мерри Брендибак', 'race': 'hobbit', 'description': 'Кузен Фродо'},
            {'name': 'Пиппин Тук', 'race': 'hobbit', 'description': 'Младший из хоббитов'},
            {'name': 'Гэндальф Серый', 'race': 'wizard', 'description': 'Маг, наставник Братства'}
        ]
        
        for char_data in characters_data:
            character = Character(**char_data)
            db.session.add(character)
        
        db.session.commit()
        
        locations_data = [
            {'character_name': 'Фродо Бэггинс', 'lat': -37.8136, 'lng': 174.9442, 'name': 'Хоббитон', 'notes': 'Начало путешествия'},
            {'character_name': 'Фродо Бэггинс', 'lat': -38.8136, 'lng': 175.9442, 'name': 'Старый лес', 'notes': 'Встреча с Томом Бомбадилом'},
            {'character_name': 'Фродо Бэггинс', 'lat': -39.8136, 'lng': 176.9442, 'name': 'Ривенделл', 'notes': 'Совет Эльронда'},
            
            {'character_name': 'Арагорн', 'lat': -40.8136, 'lng': 177.9442, 'name': 'Заверта', 'notes': 'Встреча с хоббитами'},
            {'character_name': 'Арагорн', 'lat': -39.8136, 'lng': 176.9442, 'name': 'Ривенделл', 'notes': 'Совет Эльронда'},
            {'character_name': 'Арагорн', 'lat': -41.8136, 'lng': 178.9442, 'name': 'Мория', 'notes': 'Проход через копи'},
            
            {'character_name': 'Гэндальф Серый', 'lat': -37.8136, 'lng': 174.9442, 'name': 'Хоббитон', 'notes': 'Встреча с Фродо'},
            {'character_name': 'Гэндальф Серый', 'lat': -39.8136, 'lng': 176.9442, 'name': 'Ривенделл', 'notes': 'Совет Эльронда'},
            {'character_name': 'Гэндальф Серый', 'lat': -41.8136, 'lng': 178.9442, 'name': 'Мория', 'notes': 'Битва с Балрогом'},
        ]
        
        for i, loc_data in enumerate(locations_data):
            character = Character.query.filter_by(name=loc_data['character_name']).first()
            if character:
                timestamp = datetime.now() - timedelta(days=len(locations_data) - i)
                location = Location(
                    character_id=character.id,
                    latitude=loc_data['lat'],
                    longitude=loc_data['lng'],
                    location_name=loc_data['name'],
                    notes=loc_data['notes'],
                    timestamp=timestamp
                )
                db.session.add(location)
        
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    print("Запуск сервера на http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
