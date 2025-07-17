# 🚀 TimeTracker Pro - Instrukcje Deployment na home.pl

## 📋 Przygotowany Package

Aplikacja została przygotowana do działania na **https://timetrackerpro.pl/** z lokalną bazą danych SQLite.

## 📁 Zawartość pakietu

```
deployment_ready/
├── frontend_build/          # Gotowy build React (strona główna)
│   ├── index.html
│   ├── static/             # CSS, JS, obrazy
│   ├── .htaccess          # Konfiguracja Apache
│   └── ...
├── backend/                # Aplikacja FastAPI (API)
│   ├── server.py          # Główna aplikacja
│   ├── database.py        # Obsługa SQLite
│   ├── app.py             # WSGI entry point
│   ├── requirements.txt   # Zależności Python
│   └── .env               # Konfiguracja
└── INSTRUKCJE_DEPLOYMENT.md
```

## 🔧 Wymagania hostingu home.pl

- ✅ **Python 3.8+** (obsługiwane przez home.pl)
- ✅ **SQLite** (wbudowane w Python)
- ✅ **mod_rewrite** (Apache)
- ✅ **HTTPS** (SSL)

## 🚀 Krok po kroku - Deployment

### 1. Upload plików

**Frontend (strona główna):**
- Wgraj zawartość folderu `frontend_build/` do katalogu głównego domeny
- Wszystkie pliki (.html, .css, .js, .htaccess) powinny być w root directory

**Backend (API):**
- Utwórz podfolder `api/` w katalogu głównym domeny
- Wgraj zawartość folderu `backend/` do katalogu `api/`

**Finalna struktura na serwerze:**
```
/public_html/
├── index.html              # Z frontend_build
├── static/                 # Z frontend_build
├── .htaccess              # Z frontend_build
├── api/                   # Nowy folder
│   ├── server.py          # Z backend
│   ├── database.py        # Z backend
│   ├── app.py             # Z backend
│   ├── requirements.txt   # Z backend
│   └── .env               # Z backend
```

### 2. Konfiguracja Python na home.pl

W panelu administracyjnym home.pl:
1. Idź do **"Konfiguracja Python"**
2. Wybierz **Python 3.8+**
3. Jako **"Plik startowy"** ustaw: `api/app.py`
4. Jako **"Katalog robocze"** ustaw: `api/`
5. Kliknij **"Zapisz"**

### 3. Instalacja zależności

W panelu **"Konsola Python"** (jeśli dostępna) lub przez panel administracyjny:
```bash
pip install -r api/requirements.txt
```

**Jeśli nie masz dostępu do konsoli:**
- Skontaktuj się z supportem home.pl
- Poproś o instalację pakietów z pliku `requirements.txt`

### 4. Uruchomienie aplikacji

W panelu administracyjnym:
1. Idź do **"Aplikacje Python"**
2. Kliknij **"Uruchom"** dla Twojej aplikacji
3. Sprawdź czy status to **"Aktywna"**

### 5. Testowanie

Otwórz https://timetrackerpro.pl/ i sprawdź:
- ✅ Strona główna ładuje się poprawnie
- ✅ Panel logowania działa
- ✅ API responds (spróbuj zalogować się)

## 👤 Domyślne konta

Po uruchomieniu aplikacji dostępne są konta:
- **owner / owner123** - Administrator systemu
- **admin / admin123** - Administrator firmy
- **user / user123** - Użytkownik firmy

⚠️ **Zmień hasła po pierwszym logowaniu!**

## 🔍 Rozwiązywanie problemów

### Problem: Strona nie ładuje się
**Rozwiązanie:**
- Sprawdź czy plik `.htaccess` jest wgrany
- Upewnij się, że `mod_rewrite` jest włączony

### Problem: API nie odpowiada
**Rozwiązanie:**
- Sprawdź status aplikacji Python w panelu
- Sprawdź logi błędów w panelu administracyjnym
- Upewnij się, że wszystkie zależności są zainstalowane

### Problem: Błędy bazy danych
**Rozwiązanie:**
- Sprawdź czy folder `api/` ma uprawnienia do zapisu
- Plik `timetracker_pro.db` utworzy się automatycznie

### Problem: CORS błędy
**Rozwiązanie:**
- Sprawdź plik `api/.env`
- Upewnij się, że domeny są poprawnie skonfigurowane

## 📞 Wsparcie

W przypadku problemów:
1. Sprawdź logi w panelu administracyjnym home.pl
2. Skontaktuj się z supportem home.pl
3. Wszystkie błędy będą widoczne w logach Python

## 🔒 Bezpieczeństwo

- ✅ JWT authentication
- ✅ HTTPS enforced
- ✅ CORS protection
- ✅ SQLite database (lokalna, bezpieczna)
- ✅ Security headers w .htaccess

## 🎯 Funkcjonalności

- 👥 **Zarządzanie użytkownikami** - różne poziomy dostępu
- 🏢 **Zarządzanie firmami** - multi-tenant system
- 👨‍💼 **Zarządzanie pracownikami** - dodawanie, edycja, QR kody
- ⏰ **Ewidencja czasu** - check-in/check-out
- 📱 **Skanowanie QR** - mobilne śledzenie czasu
- 📊 **Raporty** - miesięczne podsumowania

**Aplikacja jest gotowa do production!** 🚀

---

**Przygotowane:** $(date)
**Wersja:** 2.0 (SQLite)
**Kompatybilność:** home.pl hosting