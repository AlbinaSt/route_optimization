// Инициализация карты
const map = L.map('map', {
    attributionControl: false  // Отключаем стандартную атрибуцию
}).setView([45.03547, 38.97529], 13)

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

let selectedPoints = [];
let currentRoute = null;

// Функция обновления списка точек
function updatePointsList() {
    const listEl = document.getElementById('points-list');
    const calculateBtn = document.getElementById('calculate-btn');

    if (selectedPoints.length === 0) {
        listEl.innerHTML = '<li class="empty">Пока нет выбранных точек</li>';
        calculateBtn.disabled = true;
        document.getElementById('metrics').style.display = 'none';
    } else {
        listEl.innerHTML = selectedPoints.map((point, index) => `
            <li>
                Точка ${index + 1}: ${point.lat.toFixed(4)}, ${point.lng.toFixed(4)}
                <span class="delete-point" onclick="removePoint(${index})">✖</span>
            </li>
        `).join('');
        calculateBtn.disabled = false;
    }
}

// Удаление точки
window.removePoint = function(index) {
    const marker = selectedPoints[index].marker;
    map.removeLayer(marker);
    selectedPoints.splice(index, 1);
    updatePointsList();

    if (currentRoute) {
        map.removeLayer(currentRoute);
        currentRoute = null;
        document.getElementById('metrics').style.display = 'none';
    }
}

// Добавление точки на карту
function addPoint(lat, lng) {
    const marker = L.marker([lat, lng], {
        draggable: true
    }).addTo(map);

    marker.on('dragend', function(e) {
        const pos = marker.getLatLng();
        const point = selectedPoints.find(p => p.marker === marker);
        if (point) {
            point.lat = pos.lat;
            point.lng = pos.lng;
            updatePointsList();

            if (currentRoute) {
                map.removeLayer(currentRoute);
                currentRoute = null;
                document.getElementById('metrics').style.display = 'none';
            }
        }
    });

    selectedPoints.push({
        lat: lat,
        lng: lng,
        marker: marker
    });

    updatePointsList();

    // Если точки выбраны, перецентрируем карту
    if (selectedPoints.length === 1) {
        map.setView([lat, lng], 14);
    }
}

// Очистка всех точек
document.getElementById('clear-btn').addEventListener('click', () => {
    selectedPoints.forEach(point => {
        map.removeLayer(point.marker);
    });
    selectedPoints = [];
    if (currentRoute) {
        map.removeLayer(currentRoute);
        currentRoute = null;
    }
    updatePointsList();
    document.getElementById('metrics').style.display = 'none';
});

// Обработчик клика по карте
map.on('click', (e) => {
    addPoint(e.latlng.lat, e.latlng.lng);
});

// Расчет маршрута
document.getElementById('calculate-btn').addEventListener('click', async () => {
    if (selectedPoints.length < 2) {
        alert('Выберите минимум 2 точки для построения маршрута');
        return;
    }

    const loading = document.getElementById('loading');
    loading.style.display = 'flex';

    try {
        const points = selectedPoints.map(p => [p.lat, p.lng]);

        const response = await axios.post('/calculate', {
            points: points
        });

        if (response.data.success) {
            // Удаляем старый маршрут
            if (currentRoute) {
                map.removeLayer(currentRoute);
            }

            // Рисуем новый маршрут
            const routeCoords = response.data.route;
            currentRoute = L.polyline(routeCoords, {
                color: '#667eea',
                weight: 4,
                opacity: 0.8,
                lineJoin: 'round'
            }).addTo(map);

            // Адаптируем карту к маршруту
            map.fitBounds(currentRoute.getBounds(), { padding: [50, 50] });

            // Обновляем метрики
            document.getElementById('time-value').textContent = response.data.time;
            document.getElementById('distance-value').textContent = response.data.distance;
            const speed = (response.data.distance / response.data.time).toFixed(1);
            document.getElementById('speed-value').textContent = speed;
            document.getElementById('metrics').style.display = 'block';

            // Показываем уведомление
            showNotification('Маршрут успешно построен!', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.response?.data?.error || 'Ошибка при расчете маршрута', 'error');
    } finally {
        loading.style.display = 'none';
    }
});

// Уведомления
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        border-radius: 8px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}