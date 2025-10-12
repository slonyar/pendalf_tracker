"""
Тесты веб-маршрутов
"""

import pytest
from app import Character, Location, db

class TestMainPages:
    """Тесты основных страниц"""
    
    @pytest.mark.parametrize("endpoint", [
        '/',
        '/characters', 
        '/map',
        '/add_character',
    ])
    def test_main_pages_load(self, client, endpoint):
        """Тест загрузки основных страниц"""
        response = client.get(endpoint)
        assert response.status_code == 200
    
    def test_index_with_data(self, client, character_with_journey):
        """Тест главной страницы с данными"""
        character, locations = character_with_journey
        response = client.get('/')
        
        assert response.status_code == 200
        assert character.name.encode() in response.data

class TestCharacterManagement:
    """Тесты управления персонажами"""
    
    def test_add_character_success(self, client):
        """Тест успешного добавления персонажа"""
        response = client.post('/add_character', data={
            'name': 'Новый Персонаж',
            'description': 'Тестовое описание',
            'race': 'human'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        character = Character.query.filter_by(name='Новый Персонаж').first()
        assert character is not None
        assert character.race == 'human'
    
    def test_character_detail_page(self, client, character_with_journey):
        """Тест страницы детальной информации о персонаже"""
        character, locations = character_with_journey
        
        response = client.get(f'/character/{character.id}')
        assert response.status_code == 200
        assert character.name.encode() in response.data
        
        # Проверяем, что отображаются местоположения
        for location in locations:
            if location.location_name:
                assert location.location_name.encode() in response.data

class TestLocationManagement:
    """Тесты управления местоположениями"""
    
    def test_add_location_page_requires_characters(self, client):
        """Тест что страница добавления местоположения требует персонажей"""
        response = client.get('/add_location')
        assert response.status_code == 200
        # Должна быть пустая форма выбора персонажа
    
    def test_add_location_success(self, client, sample_character):
        """Тест успешного добавления местоположения"""
        response = client.post('/add_location', data={
            'character_id': sample_character.id,
            'latitude': '51.5074',
            'longitude': '-0.1278',
            'timestamp': '2024-12-19 15:30',
            'location_name': 'Лондон',
            'notes': 'Столица Англии'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        location = Location.query.filter_by(location_name='Лондон').first()
        assert location is not None
        assert location.character_id == sample_character.id
