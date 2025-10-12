"""
Интеграционные тесты полных пользовательских сценариев
"""

import pytest
import json
from app import Character, Location, db

@pytest.mark.integration
class TestCompleteUserWorkflows:
    """Полные пользовательские сценарии"""
    
    def test_gandalf_tracking_fellowship(self, client):
        """
        Интеграционный тест: Гэндальф отслеживает Братство
        1. Создает персонажей Братства
        2. Добавляет их местоположения 
        3. Просматривает на карте
        4. Анализирует маршруты
        """
        # 1. Создаем персонажей Братства
        fellowship = ['Фродо', 'Сэм', 'Арагорн', 'Леголас', 'Гимли']
        character_ids = {}
        
        for name in fellowship:
            response = client.post('/add_character', data={
                'name': name,
                'description': f'Член Братства Кольца',
                'race': 'hobbit' if name in ['Фродо', 'Сэм'] else 'human'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            character = Character.query.filter_by(name=name).first()
            character_ids[name] = character.id
        
        # 2. Добавляем местоположения для путешествия
        journey_locations = [
            {'name': 'Фродо', 'lat': -37.8, 'lng': 174.9, 'place': 'Хоббитон'},
            {'name': 'Фродо', 'lat': -39.8, 'lng': 176.9, 'place': 'Ривенделл'},
            {'name': 'Арагорн', 'lat': -39.8, 'lng': 176.9, 'place': 'Ривенделл'},
            {'name': 'Арагорн', 'lat': -41.8, 'lng': 178.9, 'place': 'Мория'},
        ]
        
        for loc in journey_locations:
            response = client.post('/add_location', data={
                'character_id': character_ids[loc['name']],
                'latitude': str(loc['lat']),
                'longitude': str(loc['lng']),
                'location_name': loc['place'],
                'timestamp': '2024-12-19 12:00'
            }, follow_redirects=True)
            assert response.status_code == 200
        
        # 3. Проверяем карту
        response = client.get('/map')
        assert response.status_code == 200
        assert b'map' in response.data.lower()
        
        # 4. Анализируем через API
        response = client.get('/api/locations')
        data = json.loads(response.data)
        assert len(data) == len(journey_locations)
        
        # Проверяем, что есть локации для каждого персонажа
        frodo_locations = [loc for loc in data if loc['character_name'] == 'Фродо']
        assert len(frodo_locations) == 2  # Хоббитон и Ривенделл
    
    @pytest.mark.slow
    def test_large_scale_tracking(self, client):
        """Тест отслеживания большого количества персонажей"""
        # Создаем много персонажей
        characters = []
        for i in range(20):
            response = client.post('/add_character', data={
                'name': f'Персонаж {i}',
                'race': 'human',
                'description': f'Тестовый персонаж номер {i}'
            }, follow_redirects=True)
            
            character = Character.query.filter_by(name=f'Персонаж {i}').first()
            characters.append(character)
        
        # Добавляем по несколько местоположений каждому
        for character in characters:
            for j in range(5):
                client.post('/add_location', data={
                    'character_id': character.id,
                    'latitude': str(j * 10 - 50),  # От -50 до 40
                    'longitude': str(j * 10 - 50),
                    'location_name': f'Место {j}',
                    'timestamp': f'2024-12-{j+1:02d} 12:00'
                }, follow_redirects=True)
        
        # Проверяем производительность API
        import time
        start_time = time.time()
        
        response = client.get('/api/locations')
        data = json.loads(response.data)
        
        end_time = time.time()
        
        assert len(data) == 20 * 5  # 20 персонажей * 5 местоположений
        assert end_time - start_time < 2.0  # Должно выполниться быстро

@pytest.mark.integration
class TestErrorRecovery:
    """Тесты восстановления после ошибок"""
    
    def test_recovery_from_database_error(self, client, sample_character):
        """Тест восстановления после ошибки БД"""
        # Пытаемся создать местоположение с неверными данными
        response = client.post('/add_location', data={
            'character_id': sample_character.id,
            'latitude': 'invalid',  # Неверная широта
            'longitude': '150.0',
            'timestamp': '2024-12-19 12:00'
        }, follow_redirects=True)
        
        # Приложение должно обработать ошибку, а не упасть
        assert response.status_code == 200
        
        # Проверяем, что некорректное местоположение не создалось
        locations = Location.query.filter_by(character_id=sample_character.id).all()
        assert len(locations) == 0
        
        # Проверяем, что после ошибки можно добавить корректное местоположение
        response = client.post('/add_location', data={
            'character_id': sample_character.id,
            'latitude': '50.0',
            'longitude': '150.0',
            'timestamp': '2024-12-19 12:00'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        locations = Location.query.filter_by(character_id=sample_character.id).all()
        assert len(locations) == 1
