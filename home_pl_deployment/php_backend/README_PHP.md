# 🚀 TimeTracker Pro - PHP Backend dla home.pl

## 🎯 GOTOWY DO DEPLOYMENT NA HOME.PL!

### 📋 Opis
Aplikacja TimeTracker Pro została przepisana na PHP, aby była w pełni kompatybilna z hostingiem home.pl. PHP jest standardowo obsługiwany przez home.pl, więc nie ma problemów z wykonywaniem skryptów.

### 📁 Pliki PHP Backend:
- `init.php` - Inicjalizacja bazy danych
- `login.php` - Logowanie użytkowników
- `employees.php` - Zarządzanie pracownikami
- `companies.php` - Zarządzanie firmami
- `users.php` - Zarządzanie użytkownikami
- `time_entries.php` - Ewidencja czasu pracy
- `qr_scan.php` - Skanowanie QR kodów
- `qr_generate.php` - Generowanie QR kodów

### 🚀 DEPLOYMENT:

1. **Upload plików** (do public_html/):
   - Wszystkie pliki PHP z folderu `php_backend/`
   - Pliki frontend z folderu `frontend_build/`

2. **Pierwsza inicjalizacja**:
   - Otwórz: `https://timetrackerpro.pl/init.php`
   - Jeśli widzisz "Database initialized successfully" - gotowe!

3. **Test aplikacji**:
   - Otwórz: `https://timetrackerpro.pl/`
   - Zaloguj się: `owner/owner123`

### 🔧 Technologie:
- **PHP 7.4+** (standardowo na home.pl)
- **SQLite** (baza danych)
- **JWT** (uproszczone uwierzytelnianie)
- **CORS** (obsługa żądań z frontendu)

### 👤 Konta domyślne:
- **owner/owner123** - Administrator systemu
- **admin/admin123** - Administrator firmy
- **user/user123** - Użytkownik

### 🎯 Endpointy API:
- `GET /init.php` - Inicjalizacja systemu
- `POST /login.php` - Logowanie
- `GET /employees.php` - Lista pracowników
- `POST /employees.php` - Dodanie pracownika
- `GET /companies.php` - Lista firm
- `POST /companies.php` - Dodanie firmy
- `GET /users.php` - Lista użytkowników
- `POST /users.php` - Dodanie użytkownika
- `GET /time_entries.php` - Lista wpisów czasu
- `POST /qr_scan.php` - Skanowanie QR
- `GET /qr_generate.php?employee_id=X` - Generowanie QR

### 🔐 Bezpieczeństwo:
- Hashowanie haseł (password_hash/password_verify)
- JWT tokens z wygaśnięciem
- CORS protection
- SQL injection protection (prepared statements)

### 📊 Funkcjonalności:
- ✅ Inicjalizacja bazy danych
- ✅ Logowanie użytkowników
- ✅ Zarządzanie firmami
- ✅ Zarządzanie pracownikami
- ✅ Generowanie QR kodów
- ✅ Skanowanie QR kodów
- ✅ Ewidencja czasu pracy
- ✅ Różne poziomy uprawnień

---

**Status: GOTOWY DO PRODUKCJI! 🎉**

Aplikacja została przepisana z Python na PHP, aby była w 100% kompatybilna z hostingiem home.pl.