# 🚀 TimeTracker Pro - Instrukcja Deploymentu na home.pl

## 📋 Zawartość paczki:
- `frontend_build/` - Zbudowana aplikacja React (pliki statyczne)
- `backend/` - Aplikacja FastAPI (Python)
- `DEPLOYMENT_GUIDE.md` - Ta instrukcja

## 🔧 Wymagania systemu:
- Python 3.8+
- MongoDB (lokalny lub zdalny)
- Node.js (opcjonalnie dla frontend development)

## 📁 Struktura po deploymencie:
```
/domains/yourdomain.home.pl/
├── public_html/              # Frontend (React build)
│   ├── index.html
│   ├── static/
│   └── .htaccess
├── backend/                  # Backend (FastAPI)
│   ├── server.py
│   ├── requirements.txt
│   ├── .env.production
│   └── run_production.py
└── logs/                     # Logi aplikacji
```

## 🚀 Instrukcja deploymentu:

### 1. Frontend (React) - Statyczne pliki
1. Skopiuj wszystkie pliki z `frontend_build/` do katalogu `public_html/` na serwerze
2. Upewnij się, że plik `.htaccess` jest w katalogu głównym
3. Sprawdź, czy serwer obsługuje mod_rewrite (dla React Router)

### 2. Backend (FastAPI) - Aplikacja Python
1. Skopiuj katalog `backend/` poza `public_html/` (ze względów bezpieczeństwa)
2. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```
3. Skonfiguruj zmienne środowiskowe w `.env.production`:
   ```
   MONGO_URL="mongodb://localhost:27017"
   DB_NAME="timetracker_production"
   JWT_SECRET="your-super-secret-jwt-key-for-production-2025"
   CORS_ORIGINS=["https://yourdomain.home.pl"]
   ```
4. Uruchom aplikację:
   ```bash
   python run_production.py
   ```

### 3. Konfiguracja MongoDB
1. Zainstaluj MongoDB lokalnie lub użyj zdalnej usługi
2. Zaktualizuj `MONGO_URL` w `.env.production`
3. Aplikacja automatycznie utworzy domyślnych użytkowników przy pierwszym uruchomieniu

### 4. Konfiguracja domeny
1. Zaktualizuj `CORS_ORIGINS` w `.env.production` z właściwą domeną
2. Sprawdź, czy subdomena API jest skonfigurowana (np. api.yourdomain.home.pl)

## 🔐 Domyślni użytkownicy:
- **Owner**: username: `owner`, password: `owner123`
- **Admin**: username: `admin`, password: `admin123`
- **User**: username: `user`, password: `user123`

## 🌐 Konfiguracja URL API:
Frontend domyślnie próbuje połączyć się z API na porcie 8001. 
Zaktualizuj `REACT_APP_BACKEND_URL` w pliku `.env` frontendu przed buildem:
```
REACT_APP_BACKEND_URL=https://api.yourdomain.home.pl
```

## 📊 Monitorowanie:
1. Sprawdź logi aplikacji w katalogu `logs/`
2. Monitoruj status procesów Python
3. Sprawdź połączenie z MongoDB

## 🛠️ Rozwiązywanie problemów:
- **Frontend nie ładuje się**: Sprawdź `.htaccess` i mod_rewrite
- **API nie działa**: Sprawdź czy Python proces działa i porty są otwarte
- **MongoDB błędy**: Sprawdź connection string w `.env.production`
- **CORS błędy**: Zaktualizuj `CORS_ORIGINS` z właściwą domeną

## 📧 Wsparcie:
W razie problemów sprawdź logi lub skontaktuj się z administratorem.

---
**TimeTracker Pro** v1.0 - System zarządzania czasem pracy