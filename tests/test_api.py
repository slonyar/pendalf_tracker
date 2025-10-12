"""
Тесты API endpoints
"""

import pytest
import json
from datetime import datetime, timedelta
from app import Location, db

class TestCharactersAPI:
    """Тесты API персонажей"""
    
    def test_get_characters_empty(self, client, empty_database):
        """Тест получения персонажей из пустой БД"""
        response = client.get('/api/characters')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data == []
    
    def test_get_characters_with_data(self, client, multiple_characters):
        """Тест получения персонажей с данными"""
        response = client.get('/api/characters')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) == len(multiple_characters)
        
        character_names = [char['name'] for char in data]
        assert 'Фродо' in character_names
        assert 'Арагорн' in character_names
    
    def test_get_characters_with_sample_data(self, client, database_with_sample_data):
        """Тест получения персонажей с примерными данными"""
        response = client.get('/api/characters')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) == 9  # Количество персонажей в примерных данных
        
        character_names = [char['name'] for char in data]
        assert 'Фродо Бэггинс' in character_names
        assert 'Гэндальф Серый' in character_names

class TestLocationsAPI:
    """Тесты API местоположений"""
    
    def test_get_locations_empty(self, client, empty_database):
        """Тест получения местоположений из пустой БД"""
        response = client.get('/api/locations')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data == []

    
    def test_get_locations_with_data(self, client, character_with_journey):
        """Тест получения местоположений с данными"""
        character, locations = character_with_journey
        
        response = client.get('/api/locations')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) == len(locations)
    
    def test_filter_locations_by_character(self, client, character_with_journey):
        """Тест фильтрации местоположений по персонажу"""
        character, locations = character_with_journey
        
        response = client.get(f'/api/locations?character_id={character.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) == len(locations)
        assert all(loc['character_id'] == character.id for loc in data)
    
    def test_filter_locations_by_date(self, client, character_with_journey):
        """Тест фильтрации местоположений по дате"""
        character, locations = character_with_journey
        
        # Фильтруем последние 7 дней
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        response = client.get(f'/api/locations?start_date={week_ago}')
        
        data = json.loads(response.data)
        # Должны получить только недавние местоположения
        assert len(data) < len(locations)

