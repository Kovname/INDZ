# 🚀 Task Management API - CI/CD Demo Project

Повноцінний проект для демонстрації CI/CD пайплайну з FastAPI.

## 📋 Особливості проекту

### CI (Continuous Integration)

- ✅ **4 тригери**: Push, Pull Request, Schedule (щоденно о 6:00), Manual
- ✅ **Статичний аналіз**: Black, isort, flake8, mypy, Bandit
- ✅ **Тестування**: Unit, Integration, E2E/Acceptance tests
- ✅ **Docker**: Multi-stage build, GitHub Container Registry
- ✅ **Slack сповіщення**: Автоматичні нотифікації
- ✅ **GitHub Issues**: Автоматичне створення issue при помилках
- ✅ **SonarQube**: Статичний аналіз коду (опціонально)

### CD (Continuous Delivery)

- ✅ **Staging deployment**: Автоматичний деплой на staging
- ✅ **Production deployment**: Деплой з ручним підтвердженням
- ✅ **Smoke tests**: Автоматичні перевірки після деплою
- ✅ **Rollback**: Можливість відкату
- ✅ **Railway**: Безкоштовний хостинг

### Моніторинг

- ✅ **Prometheus**: Збір метрик
- ✅ **Grafana**: Візуалізація та дашборди
- ✅ **Alerting**: Правила алертів

### Kubernetes (опціонально)

- ✅ **Deployment**: Rolling updates
- ✅ **Service & Ingress**: Load balancing
- ✅ **HPA**: Автомасштабування

---

## 🛠️ Швидкий старт

### 1. Клонування та налаштування

```bash
# Клонуй репозиторій
git clone https://github.com/YOUR_USERNAME/ci-cd-fastapi.git
cd ci-cd-fastapi

# Створи віртуальне середовище
python -m venv venv

# Активуй (Windows)
.\venv\Scripts\activate

# Активуй (Linux/Mac)
source venv/bin/activate

# Встанови залежності
pip install -r requirements-dev.txt
```

### 2. Запуск локально

```bash
# Запуск API
python -m uvicorn src.main:app --reload

# API доступний на http://localhost:8000
# Документація: http://localhost:8000/docs
```

### 3. Запуск тестів

```bash
# Всі тести
pytest

# Unit тести
pytest tests/test_unit.py -v

# Integration тести
pytest tests/test_integration.py -v

# E2E тести
pytest tests/test_e2e.py -v

# З покриттям
pytest --cov=src --cov-report=html
```

### 4. Docker

```bash
# Збірка образу
docker build -t task-api .

# Запуск
docker run -p 8000:8000 task-api

# Docker Compose (з моніторингом)
docker-compose up -d
```

---

## 🔧 Налаштування GitHub

### Секрети (Settings → Secrets and variables → Actions)

| Секрет              | Опис                        | Як отримати                                             |
| ------------------- | --------------------------- | ------------------------------------------------------- |
| `SLACK_WEBHOOK_URL` | Webhook для Slack сповіщень | Див. інструкцію нижче                                   |
| `RAILWAY_TOKEN`     | Токен для Railway деплою    | [Railway Dashboard](https://railway.app/account/tokens) |
| `SONAR_TOKEN`       | Токен SonarCloud (опц.)     | [SonarCloud](https://sonarcloud.io/account/security)    |

### Environments (Settings → Environments)

Створи два environments:

1. **staging** - без protection rules
2. **production** - з "Required reviewers" (додай себе)

---

## 📱 Отримання Slack Webhook

1. Перейди на https://api.slack.com/apps
2. Натисни "Create New App" → "From scratch"
3. Назви додаток (напр. "CI/CD Notifications")
4. Обери свій Workspace
5. У меню зліва: "Incoming Webhooks" → Enable
6. "Add New Webhook to Workspace"
7. Обери канал → "Allow"
8. Скопіюй Webhook URL

---

## 🚂 Налаштування Railway

1. Перейди на https://railway.app
2. "Start a New Project" → "Deploy from GitHub repo"
3. Підключи свій репозиторій
4. Railway автоматично визначить Python проект
5. Отримай токен: Account → Tokens → Create Token

---

## 📁 Структура проекту

```
ci-cd-fastapi/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI пайплайн
│       └── cd.yml              # CD пайплайн
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI додаток
│   ├── database.py             # База даних
│   └── metrics.py              # Prometheus метрики
├── tests/
│   ├── test_unit.py            # Unit тести
│   ├── test_integration.py     # Integration тести
│   └── test_e2e.py             # E2E тести
├── k8s/
│   ├── namespace.yml
│   ├── deployment.yml
│   ├── service.yml
│   └── hpa.yml
├── monitoring/
│   ├── prometheus.yml
│   ├── rules/
│   │   └── alerts.yml
│   └── grafana/
│       ├── provisioning/
│       └── dashboards/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── sonar-project.properties
└── README.md
```

---

## 📊 API Endpoints

| Метод  | Endpoint               | Опис               |
| ------ | ---------------------- | ------------------ |
| GET    | `/`                    | Інформація про API |
| GET    | `/health`              | Health check       |
| GET    | `/metrics`             | Prometheus метрики |
| GET    | `/tasks`               | Список завдань     |
| POST   | `/tasks`               | Створити завдання  |
| GET    | `/tasks/{id}`          | Отримати завдання  |
| PUT    | `/tasks/{id}`          | Оновити завдання   |
| DELETE | `/tasks/{id}`          | Видалити завдання  |
| GET    | `/tasks/stats/summary` | Статистика         |

---

## 📝 Ліцензія

MIT License
