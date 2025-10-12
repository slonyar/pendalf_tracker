PYTHON = python3
PIP = pip3
FLASK_APP = app.py
VENV_NAME = venv
PORT = 5000

RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help install dev prod clean test lint format docker-build docker-run setup check

help:
	@echo "$(BLUE)Fellowship Tracker - Makefile команды:$(NC)"
	@echo ""
	@echo "$(GREEN)Основные команды:$(NC)"
	@echo "  make setup       - Полная настройка проекта (создание venv, установка зависимостей)"
	@echo "  make install     - Установка зависимостей"
	@echo "  make dev         - Запуск в режиме разработки"
	@echo "  make prod        - Запуск в продакшен режиме"
	@echo ""
	@echo "$(GREEN)Утилиты:$(NC)"
	@echo "  make clean       - Очистка временных файлов"
	@echo "  make check       - Проверка состояния проекта"
	@echo "  make lint        - Проверка кода (flake8)"
	@echo "  make format      - Форматирование кода (black)"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  make docker-build - Сборка Docker образа"
	@echo "  make docker-run   - Запуск в Docker контейнере"
	@echo ""

setup:
	@echo "$(YELLOW)Настройка проекта Fellowship Tracker...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(BLUE)Создание виртуального окружения...$(NC)"; \
		$(PYTHON) -m venv $(VENV_NAME); \
	fi
	@echo "$(BLUE)Активация виртуального окружения и установка зависимостей...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && $(PIP) install --upgrade pip && $(PIP) install -r requirements.txt; \
	else \
		$(VENV_NAME)/Scripts/activate.bat && $(PIP) install --upgrade pip && $(PIP) install -r requirements.txt; \
	fi
	@echo "$(GREEN)✓ Проект успешно настроен!$(NC)"
	@echo "$(YELLOW)Для запуска используйте: make dev$(NC)"

install:
	@echo "$(BLUE)Установка зависимостей...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Зависимости установлены$(NC)"

check:
	@echo "$(BLUE)Проверка состояния проекта...$(NC)"
	@echo "Python версия: $$($(PYTHON) --version)"
	@echo "Pip версия: $$($(PIP) --version)"
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "$(GREEN)✓ Виртуальное окружение найдено$(NC)"; \
	else \
		echo "$(RED)✗ Виртуальное окружение не найдено$(NC)"; \
	fi
	@if [ -f "requirements.txt" ]; then \
		echo "$(GREEN)✓ Файл requirements.txt найден$(NC)"; \
	else \
		echo "$(RED)✗ Файл requirements.txt не найден$(NC)"; \
	fi
	@if [ -f "$(FLASK_APP)" ]; then \
		echo "$(GREEN)✓ Flask приложение найдено$(NC)"; \
	else \
		echo "$(RED)✗ Flask приложение не найдено$(NC)"; \
	fi

dev:
	@echo "$(GREEN)Запуск приложения в режиме разработки...$(NC)"
	@echo "$(YELLOW)Приложение будет доступно по адресу: http://localhost:$(PORT)$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && FLASK_ENV=development FLASK_DEBUG=1 $(PYTHON) $(FLASK_APP); \
	else \
		FLASK_ENV=development FLASK_DEBUG=1 $(PYTHON) $(FLASK_APP); \
	fi

prod:
	@echo "$(GREEN)Запуск приложения в продакшен режиме...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && FLASK_ENV=production $(PYTHON) $(FLASK_APP); \
	else \
		FLASK_ENV=production $(PYTHON) $(FLASK_APP); \
	fi

clean:
	@echo "$(YELLOW)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	find . -name ".DS_Store" -delete
	@if [ -f "fellowship_tracker.db" ]; then \
		rm fellowship_tracker.db; \
		echo "$(GREEN)✓ База данных удалена$(NC)"; \
	fi
	@echo "$(GREEN)✓ Временные файлы очищены$(NC)"

lint:
	@echo "$(BLUE)Проверка кода с помощью flake8...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 *.py --max-line-length=88 --ignore=E203,W503; \
		echo "$(GREEN)✓ Проверка кода завершена$(NC)"; \
	else \
		echo "$(RED)flake8 не установлен. Установите: pip install flake8$(NC)"; \
	fi

format:
	@echo "$(BLUE)Форматирование кода с помощью black...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		black *.py --line-length=88; \
		echo "$(GREEN)✓ Код отформатирован$(NC)"; \
	else \
		echo "$(RED)black не установлен. Установите: pip install black$(NC)"; \
	fi

docker-build:
	@echo "$(BLUE)Сборка Docker образа...$(NC)"
	docker build -t fellowship-tracker .
	@echo "$(GREEN)✓ Docker образ собран$(NC)"

docker-run:
	@echo "$(GREEN)Запуск приложения в Docker контейнере...$(NC)"
	@echo "$(YELLOW)Приложение будет доступно по адресу: http://localhost:$(PORT)$(NC)"
	docker run -p $(PORT):$(PORT) --name fellowship-tracker-container fellowship-tracker

docker-stop:
	@echo "$(YELLOW)Остановка Docker контейнера...$(NC)"
	docker stop fellowship-tracker-container || true
	docker rm fellowship-tracker-container || true
	@echo "$(GREEN)✓ Контейнер остановлен$(NC)"

init-db:
	@echo "$(BLUE)Инициализация базы данных...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && $(PYTHON) -c "from app import db, app; app.app_context().push(); db.create_all(); print('Database initialized')"; \
	else \
		$(PYTHON) -c "from app import db, app; app.app_context().push(); db.create_all(); print('Database initialized')"; \
	fi
	@echo "$(GREEN)✓ База данных инициализирована$(NC)"

migrate:
	@echo "$(BLUE)Создание миграций...$(NC)"
	@if command -v flask >/dev/null 2>&1; then \
		flask db migrate -m "Auto migration"; \
		flask db upgrade; \
		echo "$(GREEN)✓ Миграции применены$(NC)"; \
	else \
		echo "$(YELLOW)Flask-Migrate не установлен, используем прямое создание таблиц$(NC)"; \
		make init-db; \
	fi

seed:
	@echo "$(BLUE)Загрузка тестовых данных...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && $(PYTHON) -c "from app import init_sample_data, app; app.app_context().push(); init_sample_data(); print('Sample data loaded')"; \
	else \
		$(PYTHON) -c "from app import init_sample_data, app; app.app_context().push(); init_sample_data(); print('Sample data loaded')"; \
	fi
	@echo "$(GREEN)✓ Тестовые данные загружены$(NC)"

reset: clean
	@echo "$(YELLOW)Полная переустановка проекта...$(NC)"
	@if [ -d "$(VENV_NAME)" ]; then \
		rm -rf $(VENV_NAME); \
		echo "$(GREEN)✓ Виртуальное окружение удалено$(NC)"; \
	fi
	make setup
	make init-db
	make seed
	@echo "$(GREEN)✓ Проект переустановлен и готов к работе!$(NC)"

watch:
	@echo "$(GREEN)Запуск с автоматической перезагрузкой...$(NC)"
	@if command -v watchdog >/dev/null 2>&1; then \
		watchdog --patterns="*.py;*.html;*.css;*.js" --recursive --auto-restart make dev; \
	else \
		echo "$(YELLOW)watchdog не установлен, запускаем обычный режим разработки$(NC)"; \
		make dev; \
	fi

security:
	@echo "$(BLUE)Проверка безопасности зависимостей...$(NC)"
	@if command -v safety >/dev/null 2>&1; then \
		safety check; \
		echo "$(GREEN)✓ Проверка безопасности завершена$(NC)"; \
	else \
		echo "$(RED)safety не установлен. Установите: pip install safety$(NC)"; \
	fi

backup:
	@echo "$(BLUE)Создание бэкапа базы данных...$(NC)"
	@if [ -f "fellowship_tracker.db" ]; then \
		cp fellowship_tracker.db "fellowship_tracker_backup_$$(date +%Y%m%d_%H%M%S).db"; \
		echo "$(GREEN)✓ Бэкап создан$(NC)"; \
	else \
		echo "$(YELLOW)База данных не найдена$(NC)"; \
	fi

logs:
	@echo "$(BLUE)Последние логи приложения:$(NC)"
	@if [ -f "app.log" ]; then \
		tail -n 50 app.log; \
	else \
		echo "$(YELLOW)Файл логов не найден$(NC)"; \
	fi

.DEFAULT_GOAL := help

# Тестирование
test:
	@echo "$(BLUE)Запуск всех тестов...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && pytest; \
	else \
		pytest; \
	fi

test-unit:
	@echo "$(BLUE)Запуск юнит-тестов...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && pytest tests/test_models.py tests/test_utils.py -v; \
	else \
		pytest tests/test_models.py tests/test_utils.py -v; \
	fi

test-integration:
	@echo "$(BLUE)Запуск интеграционных тестов...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && pytest -m integration -v; \
	else \
		pytest -m integration -v; \
	fi

test-api:
	@echo "$(BLUE)Запуск тестов API...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && pytest tests/test_api.py -v; \
	else \
		pytest tests/test_api.py -v; \
	fi

test-routes:
	@echo "$(BLUE)Запуск тестов маршрутов...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && pytest tests/test_routes.py -v; \
	else \
		pytest tests/test_routes.py -v; \
	fi

test-coverage:
	@echo "$(BLUE)Запуск тестов с покрытием кода...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && pytest --cov=app --cov-report=html --cov-report=term-missing; \
	else \
		pytest --cov=app --cov-report=html --cov-report=term-missing; \
	fi
	@echo "$(GREEN)Отчет о покрытии сохранен в tests/htmlcov/index.html$(NC)"

test-fast:
	@echo "$(BLUE)Запуск быстрых тестов (без медленных)...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && pytest -m "not slow" -v; \
	else \
		pytest -m "not slow" -v; \
	fi

test-watch:
	@echo "$(BLUE)Запуск тестов в режиме наблюдения...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && pytest-watch; \
	else \
		pytest-watch; \
	fi

clean:
	@echo "$(YELLOW)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	find . -name ".DS_Store" -delete
	rm -rf tests/htmlcov/
	rm -rf tests/.pytest_cache/
	rm -f tests/coverage.xml
	@if [ -f "fellowship_tracker.db" ]; then \
		rm fellowship_tracker.db; \
		echo "$(GREEN)✓ База данных удалена$(NC)"; \
	fi
	@echo "$(GREEN)✓ Временные файлы очищены$(NC)"

init-sample-data:
	@echo "$(BLUE)Инициализация базы данных с примерными данными...$(NC)"
	@if [ -f "$(VENV_NAME)/bin/activate" ]; then \
		. $(VENV_NAME)/bin/activate && $(PYTHON) -c "from app import app, db, init_sample_data; app.app_context().push(); db.create_all(); init_sample_data(); print('Примерные данные загружены!')"; \
	else \
		$(PYTHON) -c "from app import app, db, init_sample_data; app.app_context().push(); db.create_all(); init_sample_data(); print('Примерные данные загружены!')"; \
	fi

setup:
	@echo "$(YELLOW)Настройка проекта Fellowship Tracker...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(BLUE)Создание виртуального окружения...$(NC)"; \
		$(PYTHON) -m venv $(VENV_NAME); \
	fi
	@echo "$(BLUE)Активация виртуального окружения и установка зависимостей...$(NC)"
	@. $(VENV_NAME)/bin/activate && $(PIP) install --upgrade pip && $(PIP) install -r requirements.txt
	@echo "$(BLUE)Инициализация базы данных...$(NC)"
	@. $(VENV_NAME)/bin/activate && $(PYTHON) -c "from app import app, db; app.app_context().push(); db.create_all(); print('База данных создана!')"
	@echo "$(GREEN)✓ Проект успешно настроен!$(NC)"
	@echo "$(YELLOW)Для загрузки примерных данных используйте: make init-sample-data$(NC)"
	@echo "$(YELLOW)Для запуска используйте: make dev$(NC)"

dev-with-data: init-sample-data dev

help:
	@echo "$(BLUE)Fellowship Tracker - Makefile команды:$(NC)"
	@echo ""
	@echo "$(GREEN)Основные команды:$(NC)"
	@echo "  make setup       - Полная настройка проекта"
	@echo "  make install     - Установка зависимостей"
	@echo "  make dev         - Запуск в режиме разработки"
	@echo "  make dev-with-data - Запуск с загрузкой примерных данных"
	@echo "  make prod        - Запуск в продакшен режиме"
	@echo "  make clean       - Очистка временных файлов"
	@echo ""
	@echo "$(GREEN)База данных:$(NC)"
	@echo "  make init-sample-data - Загрузка примерных данных"
	@echo "  make init-db     - Создание пустой базы данных"
	@echo ""
	@echo "$(GREEN)Тестирование:$(NC)"
	@echo "  make test        - Запуск всех тестов"
	@echo "  make test-coverage - Запуск тестов с отчетом покрытия"
	@echo "  make test-unit   - Запуск юнит-тестов"
	@echo "  make test-integration - Запуск интеграционных тестов"
	@echo "  make test-api    - Тесты API endpoints"
	@echo "  make test-routes - Тесты веб-маршрутов"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  make docker-build - Сборка Docker образа"
	@echo "  make docker-run   - Запуск в Docker контейнере"

