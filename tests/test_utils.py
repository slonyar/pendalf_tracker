"""
Тесты вспомогательных функций и утилит
"""

import pytest
from app import init_sample_data, Character, Location, db

class TestInitialization:
    """Тесты инициализации приложения"""
    
    def test_init_sample_data_creates_all_characters(self, client, empty_database):
        """Тест создания всех примерных персонажей"""
        from app import init_sample_data
        
        # Убеждаемся, что база пустая
        assert Character.query.count() == 0
        
        # Инициализируем данные
        init_sample_data()
        
        assert Character.query.count() == 9
        
        expected_characters = [
            'Фродо Бэггинс', 'Сэмуайз Гэмджи', 'Арагорн',
            'Леголас', 'Гимли', 'Боромир', 
            'Мерри Брендибак', 'Пиппин Тук', 'Гэндальф Серый'
        ]
        
        for name in expected_characters:
            character = Character.query.filter_by(name=name).first()
            assert character is not None, f"Character {name} not created"
    
    def test_init_sample_data_idempotent(self, client, empty_database):
        """Тест что повторный вызов не создает дубликаты"""
        from app import init_sample_data
        
        init_sample_data()
        first_count = Character.query.count()
        
        init_sample_data()  # Второй вызов
        second_count = Character.query.count()
        
        assert first_count == second_count
        assert first_count == 9  # Ожидаемое количество персонажей

class TestDataValidation:
    """Тесты валидации данных"""
    
    @pytest.mark.parametrize("lat,lng,expected", [
        (0, 0, True),
        (90, 180, True),
        (-90, -180, True),
        (91, 0, False),
        (0, 181, False),
        (-91, 0, False),
        (0, -181, False),
    ])
    def test_coordinate_validation_logic(self, lat, lng, expected):
        """Тест логики валидации координат"""
        is_valid = (-90 <= lat <= 90) and (-180 <= lng <= 180)
        assert is_valid == expected
