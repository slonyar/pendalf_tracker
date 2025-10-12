"""
Конфигурация pytest и общие фикстуры для всех тестов
"""

import pytest
import tempfile
import os
import sys
from datetime import datetime, timedelta

# Добавляем корневую директорию в путь для импорта app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, db, Character, Location

@pytest.fixture(scope='session')
def test_app():
    """Создает тестовое приложение Flask для всей сессии тестов"""
    # Создаем временный файл для тестовой БД
    db_fd, db_path = tempfile.mkstemp()
    
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    yield app
    
    # Очистка
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='function')
def client(test_app):
    """Создает тестового клиента для каждого теста"""
    with test_app.test_client() as client:
        with test_app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def app_context(test_app):
    """Создает контекст приложения"""
    with test_app.app_context():
        yield test_app

@pytest.fixture
def sample_character(client):
    """Создает тестового персонажа"""
    character = Character(
        name='Тестовый Фродо',
        description='Тестовый хоббит для юнит-тестов',
        race='hobbit',
        status='active'
    )
    db.session.add(character)
    db.session.commit()
    return character

@pytest.fixture
def sample_location(client, sample_character):
    """Создает тестовое местоположение"""
    location = Location(
        character_id=sample_character.id,
        latitude=-37.8136,
        longitude=174.9442,
        timestamp=datetime.now(),
        location_name='Тестовый Хоббитон',
        notes='Тестовая заметка для юнит-тестов'
    )
    db.session.add(location)
    db.session.commit()
    return location

@pytest.fixture
def multiple_characters(client):
    """Создает несколько персонажей для тестов"""
    characters_data = [
        {'name': 'Фродо', 'race': 'hobbit', 'description': 'Хранитель Кольца'},
        {'name': 'Арагорн', 'race': 'human', 'description': 'Следопыт'},
        {'name': 'Леголас', 'race': 'elf', 'description': 'Эльф-лучник'},
        {'name': 'Гимли', 'race': 'dwarf', 'description': 'Гном-воин'},
    ]
    
    characters = []
    for char_data in characters_data:
        character = Character(**char_data)
        characters.append(character)
        db.session.add(character)
    
    db.session.commit()
    return characters

@pytest.fixture
def character_with_journey(client):
    """Создает персонажа с несколькими местоположениями (путешествие)"""
    character = Character(
        name='Путешественник',
        race='human',
        description='Персонаж для тестирования маршрутов'
    )
    db.session.add(character)
    db.session.flush()  # Получаем ID до commit
    
    # Создаем маршрут путешествия
    journey_points = [
        {'lat': -37.8136, 'lng': 174.9442, 'name': 'Хоббитон', 'days_ago': 10},
        {'lat': -39.8136, 'lng': 176.9442, 'name': 'Ривенделл', 'days_ago': 7},
        {'lat': -41.8136, 'lng': 178.9442, 'name': 'Мория', 'days_ago': 5},
        {'lat': -44.8136, 'lng': 181.9442, 'name': 'Минас Тирит', 'days_ago': 1},
    ]
    
    locations = []
    for point in journey_points:
        location = Location(
            character_id=character.id,
            latitude=point['lat'],
            longitude=point['lng'],
            location_name=point['name'],
            timestamp=datetime.now() - timedelta(days=point['days_ago']),
            notes=f'Остановка в {point["name"]} {point["days_ago"]} дней назад'
        )
        locations.append(location)
        db.session.add(location)
    
    db.session.commit()
    return character, locations

@pytest.fixture
def empty_database(client):
    """Обеспечивает полностью пустую базу данных"""
    # Очищаем все данные, если они есть
    Location.query.delete()
    Character.query.delete()
    db.session.commit()
    
    # Проверяем, что база действительно пустая
    assert Character.query.count() == 0
    assert Location.query.count() == 0
    
    yield True
    
    # Очистка после теста (на всякий случай)
    Location.query.delete()
    Character.query.delete()
    db.session.commit()

# Параметризованные фикстуры
@pytest.fixture(params=['hobbit', 'human', 'elf', 'dwarf', 'wizard'])
def character_race(request):
    """Параметризованная фикстура для тестирования разных рас"""
    return request.param

@pytest.fixture(params=[
    (-90, -180),    # Крайний юго-запад
    (90, 180),      # Крайний северо-восток  
    (0, 0),         # Нулевой остров
    (55.7558, 37.6173),  # Москва
])
def coordinate_pair(request):
    """Параметризованная фикстура для тестирования координат"""
    return request.param

@pytest.fixture
def database_with_sample_data(client):
    """База данных с примерными данными для интеграционных тестов"""
    from app import init_sample_data
    
    # Убеждаемся, что база пустая
    Location.query.delete()
    Character.query.delete()
    db.session.commit()
    
    # Загружаем примерные данные
    init_sample_data()
    
    yield True
    
    # Очистка после теста
    Location.query.delete()
    Character.query.delete()
    db.session.commit()
