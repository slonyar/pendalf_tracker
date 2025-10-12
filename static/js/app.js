// Основной JavaScript файл приложения
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initializeApp();
});

function initializeApp() {
    // Инициализация уведомлений
    initNotifications();
    
    // Инициализация форм
    initForms();
    
    // Инициализация карт (если есть на странице)
    initMaps();
    
    // Инициализация интерактивных элементов
    initInteractiveElements();
}

// Система уведомлений
function initNotifications() {
    // Автоматическое скрытие алертов через 5 секунд
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Улучшение форм
function initForms() {
    // Валидация форм в реальном времени
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Показываем уведомление об ошибке
                showNotification('Пожалуйста, заполните все обязательные поля корректно', 'error');
            }
            form.classList.add('was-validated');
        });
        
        // Улучшение полей ввода координат
        const latInput = form.querySelector('input[name="latitude"]');
        const lngInput = form.querySelector('input[name="longitude"]');
        
        if (latInput && lngInput) {
            [latInput, lngInput].forEach(input => {
                input.addEventListener('input', function() {
                    validateCoordinate(this);
                });
            });
        }
    });
}

// Валидация координат
function validateCoordinate(input) {
    const value = parseFloat(input.value);
    const isLat = input.name === 'latitude';
    const min = isLat ? -90 : -180;
    const max = isLat ? 90 : 180;
    
    if (isNaN(value) || value < min || value > max) {
        input.classList.add('is-invalid');
        if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('invalid-feedback')) {
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = `${isLat ? 'Широта' : 'Долгота'} должна быть от ${min} до ${max}`;
            input.parentNode.insertBefore(feedback, input.nextSibling);
        }
    } else {
        input.classList.remove('is-invalid');
        const feedback = input.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.remove();
        }
    }
}

// Инициализация карт
function initMaps() {
    // Общие настройки для всех карт
    const mapDefaults = {
        center: [-39.0, 176.0],
        zoom: 6,
        tileLayer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '© OpenStreetMap contributors'
    };
    
    // Глобальные переменные для карт
    window.appMaps = window.appMaps || {};
}

// Интерактивные элементы
function initInteractiveElements() {
    // Улучшение кнопок удаления
    const deleteButtons = document.querySelectorAll('button[onclick*="confirm"], form[onsubmit*="confirm"] button[type="submit"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const form = this.closest('form');
            const itemName = this.dataset.itemName || 'элемент';
            
            showConfirmDialog(
                'Подтверждение удаления',
                `Вы уверены, что хотите удалить ${itemName}? Это действие нельзя отменить.`,
                () => {
                    if (form) {
                        form.submit();
                    }
                }
            );
        });
    });
    
    // Улучшение таблиц
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        // Добавляем сортировку (простая реализация)
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (header.textContent.trim()) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => sortTable(table, index));
            }
        });
    });
    
    // Копирование координат по клику
    const coordinateElements = document.querySelectorAll('code');
    coordinateElements.forEach(element => {
        if (element.textContent.match(/^-?\d+\.\d+,\s*-?\d+\.\d+$/)) {
            element.style.cursor = 'pointer';
            element.title = 'Нажмите, чтобы скопировать';
            element.addEventListener('click', function() {
                navigator.clipboard.writeText(this.textContent).then(() => {
                    showNotification('Координаты скопированы в буфер обмена', 'success');
                });
            });
        }
    });
}

// Функция уведомлений
function showNotification(message, type = 'info', duration = 3000) {
    const alertTypes = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    };
    
    const alert = document.createElement('div');
    alert.className = `alert ${alertTypes[type] || alertTypes.info} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Автоматическое удаление
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, duration);
}

// Диалог подтверждения
function showConfirmDialog(title, message, onConfirm) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                    <button type="button" class="btn btn-danger confirm-btn">Удалить</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    modal.querySelector('.confirm-btn').addEventListener('click', () => {
        onConfirm();
        bsModal.hide();
    });
    
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}

// Простая сортировка таблиц
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isNumeric = rows.every(row => {
        const cell = row.cells[columnIndex];
        return cell && !isNaN(parseFloat(cell.textContent.trim()));
    });
    
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        if (isNumeric) {
            return parseFloat(aText) - parseFloat(bText);
        } else {
            return aText.localeCompare(bText, 'ru');
        }
    });
    
    // Проверяем, была ли таблица уже отсортирована по этому столбцу
    const currentOrder = table.dataset.sortOrder;
    const currentColumn = table.dataset.sortColumn;
    
    if (currentColumn === columnIndex.toString() && currentOrder === 'asc') {
        rows.reverse();
        table.dataset.sortOrder = 'desc';
    } else {
        table.dataset.sortOrder = 'asc';
    }
    
    table.dataset.sortColumn = columnIndex.toString();
    
    // Обновляем таблицу
    rows.forEach(row => tbody.appendChild(row));
}

// Утилиты для работы с картами
const MapUtils = {
    // Создание маркера с кастомным стилем
    createCustomMarker(lat, lng, options = {}) {
        const defaultOptions = {
            color: '#007bff',
            fillColor: '#007bff',
            fillOpacity: 0.7,
            radius: 6,
            weight: 2
        };
        
        return L.circleMarker([lat, lng], { ...defaultOptions, ...options });
    },
    
    // Создание попапа с кастомным содержимым
    createPopup(content, options = {}) {
        return L.popup({
            maxWidth: 300,
            className: 'custom-popup',
            ...options
        }).setContent(content);
    },
    
    // Форматирование координат для отображения
    formatCoordinates(lat, lng, precision = 6) {
        return `${lat.toFixed(precision)}, ${lng.toFixed(precision)}`;
    },
    
    // Расчет расстояния между двумя точками (формула гаверсинуса)
    calculateDistance(lat1, lng1, lat2, lng2) {
        const R = 6371; // Радиус Земли в км
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLng = (lng2 - lng1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLng/2) * Math.sin(dLng/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
};

// Утилиты для работы с датами
const DateUtils = {
    // Форматирование даты для отображения
    formatDate(date, locale = 'ru-RU') {
        return new Date(date).toLocaleString(locale);
    },
    
    // Получение относительного времени
    getRelativeTime(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days} дн. назад`;
        if (hours > 0) return `${hours} ч. назад`;
        if (minutes > 0) return `${minutes} мин. назад`;
        return 'только что';
    }
};

// Экспорт утилит в глобальную область видимости
window.MapUtils = MapUtils;
window.DateUtils = DateUtils;
window.showNotification = showNotification;
window.showConfirmDialog = showConfirmDialog;

