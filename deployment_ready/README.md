# TimeTracker Pro - Deployment Package

## 🎯 Gotowy do hostingu home.pl

Aplikacja została w pełni przygotowana do działania na **https://timetrackerpro.pl/** z lokalną bazą danych SQLite.

## 📦 Co zawiera package

- **Frontend**: Zoptymalizowany build React z routingiem
- **Backend**: FastAPI z SQLite database
- **Konfiguracja**: .htaccess, .env, WSGI entry point
- **Instrukcje**: Szczegółowy przewodnik deployment

## 🚀 Jak wdrożyć

1. **Upload plików**:
   - `frontend_build/` → katalog główny domeny
   - `backend/` → folder `api/` na serwerze

2. **Konfiguracja Python** w panelu home.pl:
   - Plik startowy: `api/app.py`
   - Katalog roboczy: `api/`

3. **Instalacja zależności**:
   ```bash
   pip install -r api/requirements.txt
   ```

4. **Uruchomienie aplikacji** w panelu administracyjnym

## 👤 Konta domyślne

- `owner/owner123` - Administrator systemu
- `admin/admin123` - Administrator firmy  
- `user/user123` - Użytkownik firmy

## 🔧 Technologie

- **Frontend**: React + Tailwind CSS
- **Backend**: FastAPI + SQLite
- **Hosting**: home.pl compatible
- **Database**: SQLite (lokalna, bez uprawnień)

## 📋 Wymagania

- Python 3.8+ ✅
- SQLite ✅  
- mod_rewrite ✅
- HTTPS ✅

Wszystko dostępne na home.pl!

Zobacz **INSTRUKCJE_DEPLOYMENT.md** dla szczegółów.