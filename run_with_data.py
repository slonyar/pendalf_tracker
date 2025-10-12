"""
Скрипт для быстрого запуска приложения с примерными данными
"""

from app import app, db, init_sample_data

def main():
    """Запускает приложение с примерными данными"""
    with app.app_context():
        db.create_all()
        
        from app import Character
        if Character.query.count() == 0:
            print("Загружаем примерные данные...")
            init_sample_data()
            print("Примерные данные загружены!")
        else:
            print("Данные уже существуют")
    
    print("Запускаем сервер на http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()

