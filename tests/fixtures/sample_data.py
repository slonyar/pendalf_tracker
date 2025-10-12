"""
Образцы тестовых данных
"""

from datetime import datetime, timedelta

# Тестовые персонажи
SAMPLE_CHARACTERS = [
    {
        'name': 'Фродо Бэггинс',
        'race': 'hobbit',
        'description': 'Хранитель Кольца, храбрый хоббит из Шира',
        'status': 'active'
    },
    {
        'name': 'Арагорн',
        'race': 'human', 
        'description': 'Следопыт Севера, наследник трона Гондора',
        'status': 'active'
    },
    {
        'name': 'Гэндальф Серый',
        'race': 'wizard',
        'description': 'Мудрый маг, наставник Братства',
        'status': 'active'
    },
]

# Известные места Средиземья
MIDDLE_EARTH_LOCATIONS = {
    'hobbiton': {
        'name': 'Хоббитон',
        'latitude': -37.8136,
        'longitude': 174.9442,
        'description': 'Деревня хоббитов в Шире'
    },
    'rivendell': {
        'name': 'Ривенделл',
        'latitude': -39.8136,
        'longitude': 176.9442,
        'description': 'Дом Эльронда'
    },
    'moria': {
        'name': 'Мория',
        'latitude': -41.8136,
        'longitude': 178.9442,
        'description': 'Заброшенные гномьи копи'
    },
    'lorien': {
        'name': 'Лориэн',
        'latitude': -42.5,
        'longitude': 180.2,
        'description': 'Лес леди Галадриэли'
    },
    'minas_tirith': {
        'name': 'Минас Тирит',
        'latitude': -44.8136,
        'longitude': 181.9442,
        'description': 'Белый город, столица Гондора'
    },
    'mordor': {
        'name': 'Мордор',
        'latitude': -46.8136,
        'longitude': 183.9442,
        'description': 'Земля Тьмы, владения Саурона'
    }
}

# Тестовые маршруты
SAMPLE_JOURNEYS = {
    'frodo_journey': [
        {'location': 'hobbiton', 'days_ago': 100, 'notes': 'Начало путешествия'},
        {'location': 'rivendell', 'days_ago': 80, 'notes': 'Совет Эльронда'},
        {'location': 'moria', 'days_ago': 60, 'notes': 'Проход через копи'},
        {'location': 'lorien', 'days_ago': 50, 'notes': 'Отдых у эльфов'},
        {'location': 'mordor', 'days_ago': 1, 'notes': 'Уничтожение Кольца'}
    ],
    'aragorn_journey': [
        {'location': 'rivendell', 'days_ago': 80, 'notes': 'Совет Эльронда'},
        {'location': 'moria', 'days_ago': 60, 'notes': 'Проход через Морию'},
        {'location': 'minas_tirith', 'days_ago': 10, 'notes': 'Коронация короля'}
    ]
}

# Граничные значения для тестирования
COORDINATE_EDGE_CASES = [
    {'lat': 90, 'lng': 180, 'name': 'Северо-восточный полюс'},
    {'lat': -90, 'lng': -180, 'name': 'Юго-западный полюс'},
    {'lat': 0, 'lng': 0, 'name': 'Нулевой остров'},
    {'lat': 89.9999, 'lng': 179.9999, 'name': 'Почти полюс'},
]

# Невалидные данные для негативного тестирования
INVALID_DATA = {
    'coordinates': [
        {'lat': 91, 'lng': 0, 'error': 'Latitude too high'},
        {'lat': -91, 'lng': 0, 'error': 'Latitude too low'},
        {'lat': 0, 'lng': 181, 'error': 'Longitude too high'},
        {'lat': 0, 'lng': -181, 'error': 'Longitude too low'},
        {'lat': 'abc', 'lng': 0, 'error': 'Invalid latitude format'},
        {'lat': 0, 'lng': 'xyz', 'error': 'Invalid longitude format'},
    ],
    'character_names': [
        '',  # Пустое имя
        'A' * 101,  # Слишком длинное имя (если есть ограничение)
    ]
}

def create_test_journey(character_id, journey_name='frodo_journey'):
    """
    Создает тестовое путешествие для персонажа
    
    Args:
        character_id: ID персонажа
        journey_name: Название маршрута из SAMPLE_JOURNEYS
    
    Returns:
        List of Location objects
    """
    from app import Location
    
    journey = SAMPLE_JOURNEYS.get(journey_name, SAMPLE_JOURNEYS['frodo_journey'])
    locations = []
    
    for point in journey:
        location_info = MIDDLE_EARTH_LOCATIONS[point['location']]
        location = Location(
            character_id=character_id,
            latitude=location_info['latitude'],
            longitude=location_info['longitude'],
            location_name=location_info['name'],
            notes=point['notes'],
            timestamp=datetime.now() - timedelta(days=point['days_ago'])
        )
        locations.append(location)
    
    return locations

