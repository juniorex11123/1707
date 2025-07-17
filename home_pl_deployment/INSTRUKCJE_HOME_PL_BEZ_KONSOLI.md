# 🚀 TimeTracker Pro - Instrukcje dla home.pl (BEZ KONSOLI)

## 🎯 GOTOWY DEPLOYMENT - 100% KOMPATYBILNY Z HOME.PL

**Aplikacja jest w pełni przygotowana do wdrożenia na home.pl bez potrzeby dostępu do konsoli!**

## 📋 Co masz w pakiecie:

### ✅ Kompletny system TimeTracker Pro:
- **Frontend**: Responsywna aplikacja React
- **Backend**: Python CGI skrypty (.py3)
- **Baza danych**: SQLite (automatycznie tworzona)
- **Funkcjonalności**: Zarządzanie czasem, QR kody, raporty
- **Bezpieczeństwo**: JWT, bcrypt, HTTPS

## 🔧 WYMAGANIA HOSTINGU HOME.PL:
- ✅ Python 3.6+ (standardowo dostępne)
- ✅ Rozszerzenia .py3 (obsługiwane)
- ✅ SQLite (wbudowane w Python)
- ✅ mod_rewrite (Apache)
- ✅ HTTPS/SSL

## 📁 PLIKI DO UPLOADOWANIA:

### Wgraj te pliki do katalogu `public_html/` Twojej domeny:

**Z folderu `frontend_build/`:**
- `index.html`
- `static/` (cały folder)
- `.htaccess`

**Z folderu `backend_cgi/`:**
- `init.py3`
- `login.py3`
- `employees.py3`
- `companies.py3`
- `users.py3`
- `time_entries.py3`
- `qr_scan.py3`
- `qr_generate.py3`
- `database.py3`
- `auth.py3`
- `utils.py3`

## 🚀 DEPLOYMENT KROK PO KROKU:

### 1. UPLOAD PLIKÓW (przez FTP/Panel home.pl):
```
public_html/
├── index.html              # Frontend
├── static/                 # Frontend assets
├── .htaccess              # Apache config
├── init.py3               # Backend inicjalizacja
├── login.py3              # Backend logowanie
├── employees.py3          # Backend pracownicy
├── companies.py3          # Backend firmy
├── users.py3              # Backend użytkownicy
├── time_entries.py3       # Backend ewidencja
├── qr_scan.py3            # Backend skanowanie
├── qr_generate.py3        # Backend generowanie QR
├── database.py3           # Backend SQLite
├── auth.py3               # Backend uwierzytelnianie
└── utils.py3              # Backend narzędzia
```

### 2. PIERWSZA INICJALIZACJA:
1. Otwórz przeglądarkę
2. Idź do: `https://TWOJA-DOMENA.home.pl/init.py3`
3. Jeśli widzisz komunikat "Database initialized successfully" - GOTOWE!

### 3. TEST APLIKACJI:
1. Otwórz: `https://TWOJA-DOMENA.home.pl/`
2. Kliknij "Zaloguj do panelu"
3. Użyj konta: `owner` / `owner123`

## 👤 KONTA DOMYŚLNE:

Po inicjalizacji dostępne są:
- **owner/owner123** - Administrator systemu (pełny dostęp)
- **admin/admin123** - Administrator firmy (zarządzanie zespołem)
- **user/user123** - Użytkownik firmy (skanowanie QR)

⚠️ **WAŻNE: Zmień hasła po pierwszym logowaniu!**

## 🔍 ENDPOINTY API:

Aplikacja będzie dostępna pod adresami:
- **Strona główna**: `https://TWOJA-DOMENA.home.pl/`
- **Panel logowania**: `https://TWOJA-DOMENA.home.pl/panel`
- **API logowania**: `https://TWOJA-DOMENA.home.pl/login.py3`
- **API pracownicy**: `https://TWOJA-DOMENA.home.pl/employees.py3`
- **API skanowanie QR**: `https://TWOJA-DOMENA.home.pl/qr_scan.py3`
- **API generowanie QR**: `https://TWOJA-DOMENA.home.pl/qr_generate.py3`

## 🎯 FUNKCJONALNOŚCI:

### ✅ Zarządzanie użytkownikami:
- Owner: może zarządzać wszystkimi firmami i użytkownikami
- Admin: może zarządzać swoją firmą i pracownikami
- User: może skanować QR kody i rejestrować czas

### ✅ Ewidencja czasu pracy:
- Automatyczne generowanie QR kodów dla pracowników
- Skanowanie QR kodów (mobile-friendly)
- Rejestracja wejść/wyjść
- Automatyczne liczenie godzin

### ✅ Raporty i zarządzanie:
- Podgląd czasu pracy pracowników
- Zarządzanie firmami
- Eksport danych do PDF
- Statystyki miesięczne

## 🔧 ROZWIĄZYWANIE PROBLEMÓW:

### Problem: Strona nie ładuje się
**Rozwiązanie:**
1. Sprawdź czy wszystkie pliki z `frontend_build/` są wgrane
2. Upewnij się, że `.htaccess` jest w katalogu głównym
3. Sprawdź czy `index.html` jest w katalogu głównym

### Problem: Skrypty .py3 nie działają
**Rozwiązanie:**
1. Upewnij się, że pliki mają rozszerzenie `.py3` (nie `.py`)
2. Sprawdź czy wszystkie pliki z `backend_cgi/` są wgrane
3. Skontaktuj się z home.pl w sprawie obsługi Python 3.6

### Problem: Błąd 500 w API
**Rozwiązanie:**
1. Sprawdź uprawnienia plików (powinny być 755)
2. Sprawdź logi błędów w panelu home.pl
3. Upewnij się, że pierwsze uruchomienie to `init.py3`

### Problem: Nie można się zalogować
**Rozwiązanie:**
1. Uruchom najpierw `init.py3` aby stworzyć bazę danych
2. Użyj kont domyślnych: `owner/owner123`
3. Sprawdź czy frontend łączy się z backend

## 💾 BAZA DANYCH:

- **Typ**: SQLite (automatycznie tworzona)
- **Plik**: `timetracker_pro.db` (tworzy się automatycznie)
- **Lokalizacja**: W katalogu głównym domeny
- **Backup**: Pobierz plik `timetracker_pro.db` przez FTP

## 🔐 BEZPIECZEŃSTWO:

### ✅ Wbudowane zabezpieczenia:
- JWT tokens z 24h wygaśnięciem
- Bcrypt hashing haseł
- HTTPS wymuszony przez .htaccess
- CORS protection
- XSS i CSRF protection
- Security headers

### ✅ Zgodność z RODO:
- Lokalna baza danych
- Brak zewnętrznych API
- Pełna kontrola nad danymi

## 📊 MONITORING:

### Sprawdzanie stanu:
- **Status systemu**: `https://TWOJA-DOMENA.home.pl/init.py3`
- **Test API**: `https://TWOJA-DOMENA.home.pl/employees.py3`

### Logi:
- Panel home.pl → Logi błędów
- Apache error logs
- Python CGI logs

## 🎉 GOTOWE DO UŻYCIA!

Po wykonaniu powyższych kroków aplikacja będzie w pełni funkcjonalna:

1. **Strona główna** - Prezentacja produktu
2. **Panel logowania** - Bezpieczne uwierzytelnianie
3. **Dashboardy** - Różne dla Owner/Admin/User
4. **Zarządzanie** - Firmy, użytkownicy, pracownicy
5. **Ewidencja** - Skanowanie QR, rejestracja czasu
6. **Raporty** - Podgląd i eksport danych

## 📞 WSPARCIE:

W przypadku problemów:
1. Sprawdź logi w panelu home.pl
2. Upewnij się, że wszystkie pliki są wgrane
3. Przetestuj kolejno: init.py3 → strona główna → logowanie

---

**🚀 APLIKACJA JEST W 100% GOTOWA DO WDROŻENIA NA HOME.PL!**

**Rozmiar pakietu**: ~2.5MB  
**Czas wdrożenia**: 5-10 minut  
**Wymagania**: Standardowy hosting home.pl z Python  
**Status**: Gotowy do produkcji!

**Wszystko działa lokalnie - bez potrzeby zewnętrznych API! 🎉**