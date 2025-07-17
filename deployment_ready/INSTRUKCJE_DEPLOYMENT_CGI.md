# 🚀 TimeTracker Pro - Deployment na home.pl (CGI)

## 📋 Przygotowany Package

Aplikacja została w pełni przygotowana do działania na **https://timetrackerpro.pl/** jako skrypty CGI Python.

## 🔧 Architektura CGI

Na hostingu home.pl Python działa jako CGI przez rozszerzenia plików:
- **Python 3.6**: `.py3` rozszerzenie
- **Każdy endpoint**: Osobny plik .py3
- **Baza danych**: SQLite (nie wymaga uprawnień)

## 📁 Struktura deployment

```
deployment_ready/
├── frontend_build/          # Strona główna (React)
│   ├── index.html
│   ├── static/             # CSS, JS, obrazy
│   └── .htaccess          # Konfiguracja Apache
├── backend_cgi/            # Skrypty Python CGI
│   ├── init.py3           # Inicjalizacja bazy danych
│   ├── login.py3          # Logowanie
│   ├── employees.py3      # Zarządzanie pracownikami
│   ├── companies.py3      # Zarządzanie firmami
│   ├── users.py3          # Zarządzanie użytkownikami
│   ├── time_entries.py3   # Ewidencja czasu
│   ├── qr_scan.py3        # Skanowanie QR kodów
│   ├── qr_generate.py3    # Generowanie QR kodów
│   ├── database.py3       # Obsługa SQLite
│   ├── auth.py3           # Uwierzytelnianie
│   └── utils.py3          # Funkcje pomocnicze
└── INSTRUKCJE_DEPLOYMENT_CGI.md
```

## 🚀 Krok po kroku - Deployment

### 1. Upload plików na home.pl

**A) Frontend (katalog główny domeny):**
```
Wgraj zawartość folderu frontend_build/ do:
public_html/
├── index.html
├── static/
├── .htaccess
└── ... (pozostałe pliki)
```

**B) Backend (katalog główny domeny):**
```
Wgraj zawartość folderu backend_cgi/ do:
public_html/
├── init.py3
├── login.py3
├── employees.py3
├── companies.py3
├── users.py3
├── time_entries.py3
├── qr_scan.py3
├── qr_generate.py3
├── database.py3
├── auth.py3
└── utils.py3
```

**Finalna struktura na serwerze:**
```
public_html/
├── index.html              # Frontend
├── static/                 # Frontend assets
├── .htaccess              # Frontend routing
├── init.py3               # Backend endpoint
├── login.py3              # Backend endpoint
├── employees.py3          # Backend endpoint
├── companies.py3          # Backend endpoint
├── users.py3              # Backend endpoint
├── time_entries.py3       # Backend endpoint
├── qr_scan.py3            # Backend endpoint
├── qr_generate.py3        # Backend endpoint
├── database.py3           # Backend library
├── auth.py3               # Backend library
└── utils.py3              # Backend library
```

### 2. Pierwsza inicjalizacja

Po uploadzie plików:
1. Otwórz w przeglądarce: `https://timetrackerpro.pl/init.py3`
2. Powinieneś zobaczyć:
   ```json
   {
     "message": "Database initialized successfully",
     "status": "ready",
     "default_accounts": {
       "owner": "owner/owner123",
       "admin": "admin/admin123",
       "user": "user/user123"
     }
   }
   ```

### 3. Test funkcjonalności

**A) Test strony głównej:**
- Otwórz: `https://timetrackerpro.pl/`
- Strona główna powinna się załadować poprawnie

**B) Test API:**
- Otwórz: `https://timetrackerpro.pl/employees.py3`
- Powinien pokazać błąd 401 (brak autoryzacji) - to jest poprawne

**C) Test logowania:**
- Otwórz: `https://timetrackerpro.pl/` → kliknij "Zaloguj do panelu"
- Użyj konta: `owner` / `owner123`
- Powinieneś zostać zalogowany do panelu

## 🔍 Endpointy API

### Logowanie
- **URL**: `https://timetrackerpro.pl/login.py3`
- **Metoda**: POST
- **Body**: `{"username": "owner", "password": "owner123"}`

### Pracownicy
- **Lista**: `https://timetrackerpro.pl/employees.py3` (GET)
- **Dodaj**: `https://timetrackerpro.pl/employees.py3` (POST)

### Skanowanie QR
- **Skan**: `https://timetrackerpro.pl/qr_scan.py3` (POST)
- **Generuj**: `https://timetrackerpro.pl/qr_generate.py3?employee_id=123` (GET)

### Firmy
- **Lista**: `https://timetrackerpro.pl/companies.py3` (GET)
- **Dodaj**: `https://timetrackerpro.pl/companies.py3` (POST)

### Użytkownicy
- **Lista**: `https://timetrackerpro.pl/users.py3` (GET)
- **Dodaj**: `https://timetrackerpro.pl/users.py3` (POST)

### Ewidencja czasu
- **Lista**: `https://timetrackerpro.pl/time_entries.py3` (GET)

## 👤 Konta domyślne

Po inicjalizacji dostępne są:
- **owner / owner123** - Administrator systemu
- **admin / admin123** - Administrator firmy
- **user / user123** - Użytkownik firmy

⚠️ **Zmień hasła po pierwszym logowaniu!**

## 🔧 Rozwiązywanie problemów

### Problem: Strona nie ładuje się
**Rozwiązanie:**
- Sprawdź czy `.htaccess` jest wgrany
- Upewnij się, że `index.html` jest w katalogu głównym

### Problem: Skrypty .py3 nie działają
**Rozwiązanie:**
- Sprawdź czy pliki .py3 mają rozszerzenie `.py3` (nie `.py`)
- Upewnij się, że wszystkie pliki są w katalogu głównym domeny
- Sprawdź czy hosting obsługuje Python 3.6

### Problem: Błąd 500 w skryptach
**Rozwiązanie:**
- Sprawdź uprawnienia plików (powinny być 755)
- Sprawdź logi błędów w panelu home.pl
- Upewnij się, że pierwsze linijki to `#!/usr/bin/env python3`

### Problem: Brak autoryzacji
**Rozwiązanie:**
- Najpierw uruchom `init.py3` aby stworzyć bazę danych
- Użyj kont domyślnych do testów
- Sprawdź czy token JWT jest prawidłowo przesyłany

### Problem: Błędy CORS
**Rozwiązanie:**
- Wszystkie skrypty .py3 mają już odpowiednie headery CORS
- Sprawdź czy domena jest ustawiona na `https://timetrackerpro.pl`

## 📊 Monitoring

### Sprawdzanie stanu systemu
- **Inicjalizacja**: `https://timetrackerpro.pl/init.py3`
- **API Status**: `https://timetrackerpro.pl/api.py3`

### Logi błędów
- W panelu home.pl idź do sekcji "Logi błędów"
- Sprawdź logi Apache dla błędów 500

## 🔒 Bezpieczeństwo

- ✅ **JWT tokens** - 24h wygaśnięcie
- ✅ **HTTPS** - Wymuszone przez .htaccess
- ✅ **CORS** - Tylko dla domeny timetrackerpro.pl
- ✅ **SQLite** - Lokalna baza danych
- ✅ **Bcrypt** - Hashowanie haseł
- ✅ **Security headers** - XSS, CSRF protection

## 🎯 Funkcjonalności

- 👥 **Zarządzanie użytkownikami** - Owner/Admin/User
- 🏢 **Zarządzanie firmami** - Multi-tenant
- 👨‍💼 **Pracownicy** - Dodawanie, QR kody
- ⏰ **Ewidencja czasu** - Check-in/out
- 📱 **Skanowanie QR** - Mobilne śledzenie
- 📊 **Raporty** - Wgląd w czas pracy

## 📞 Wsparcie

W przypadku problemów:
1. Sprawdź logi błędów w panelu home.pl
2. Upewnij się, że wszystkie pliki są wgrane
3. Sprawdź uprawnienia plików (755)
4. Zweryfikuj czy Python 3.6 jest aktywny

---

**Status**: Gotowy do produkcji!  
**Architektura**: CGI Python + SQLite  
**Hosting**: home.pl compatible  
**Wersja**: 3.0 (CGI)  

**Aplikacja działa niezależnie - bez zewnętrznych API! 🚀**