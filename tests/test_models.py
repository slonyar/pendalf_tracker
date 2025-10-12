"""
Тесты моделей базы данных
"""

import pytest
from datetime import datetime, timedelta
from app import Character, Location, db
from tests.fixtures.sample_data import SAMPLE_CHARACTERS, COORDINATE_EDGE_CASES, INVALID_DATA

class TestCharacterModel:
    """Тесты для модели Character"""
    
    def test_create_character_basic(self, client):
        """Тест создания простого персонажа"""
        character = Character(
            name='Тестовый Гэндальф',
            description='Серый маг',
            race='wizard'
        )
        db.session.add(character)
        db.session.commit()
        
        assert character.id is not None
        assert character.name == 'Тестовый Гэндальф'
        assert character.race == 'wizard'
        assert character.status == 'active'
        assert character.created_at is not None
    
    @pytest.mark.parametrize("char_data", SAMPLE_CHARACTERS)
    def test_create_character_with_sample_data(self, client, char_data):
        """Тест создания персонажей с образцовыми данными"""
        character = Character(**char_data)
        db.session.add(character)
        db.session.commit()
        
        assert character.name == char_data['name']
        assert character.race == char_data['race']
    
    def test_character_unique_name_constraint(self, client):
        """Тест ограничения уникальности имени"""
        char1 = Character(name='Уникальное Имя', race='human')
        db.session.add(char1)
        db.session.commit()
        
        char2 = Character(name='Уникальное Имя', race='elf')
        db.session.add(char2)
        
        with pytest.raises(Exception):
            db.session.commit()
    
    def test_character_cascade_delete(self, client, sample_character, sample_location):
        """Тест каскадного удаления местоположений при удалении персонажа"""
        character_id = sample_character.id
        location_id = sample_location.id
        
        db.session.delete(sample_character)
        db.session.commit()
        
        assert Character.query.get(character_id) is None
        assert Location.query.get(location_id) is None

class TestLocationModel:
    """Тесты для модели Location"""
    
    def test_create_location_basic(self, client, sample_character):
        """Тест создания основного местоположения"""
        location = Location(
            character_id=sample_character.id,
            latitude=-45.123456,
            longitude=170.987654,
            timestamp=datetime.now(),
            location_name='Тестовое место',
            notes='Тестовые заметки'
        )
        db.session.add(location)
        db.session.commit()
        
        assert location.id is not None
        assert location.character_id == sample_character.id
        assert location.latitude == -45.123456
        assert location.longitude == 170.987654
    
    @pytest.mark.parametrize("coord_data", COORDINATE_EDGE_CASES)
    def test_coordinate_edge_cases(self, client, sample_character, coord_data):
        """Тест граничных значений координат"""
        location = Location(
            character_id=sample_character.id,
            latitude=coord_data['lat'],
            longitude=coord_data['lng'],
            location_name=coord_data['name'],
            timestamp=datetime.now()
        )
        db.session.add(location)
        db.session.commit()
        
        assert location.latitude == coord_data['lat']
        assert location.longitude == coord_data['lng']
