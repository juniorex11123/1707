# 🔧 NAPRAWIONE PLIKI DEPLOYMENT - TimeTracker Pro

## ❌ PROBLEM ROZWIĄZANY:
Błąd: `NameError: name 'utils' is not defined` w pliku `utils.py`

## ✅ ROZWIĄZANIE:
Zastąpiono uszkodzone pliki naprawionymi wersjami.

## 📁 PLIKI DO WGRANIA NA SERWER:

### 1. **NAJPIERW USUŃ STARE PLIKI:**
```bash
# Usuń wszystkie stare pliki Python na serwerze
rm -f *.py *.py3 *.db
```

### 2. **WGRAJ NOWE PLIKI:**
Wgraj wszystkie pliki z tego folderu `/app/FIXED_DEPLOYMENT/` do `public_html/`:

**Kluczowe pliki (MUSISZ WGRAĆ):**
- `utils.py` - naprawiony plik utility
- `utils.py3` - naprawiony plik utility 
- `auth.py` - autoryzacja
- `auth.py3` - autoryzacja
- `database.py` - obsługa bazy danych
- `database.py3` - obsługa bazy danych
- `init.py3` - **NAPRAWIONY** plik inicjalizacji
- `login.py3` - endpoint logowania
- `diagnose.py3` - **NOWY** plik diagnostyczny

**Pliki frontend:**
- `index.html` - strona główna
- `static/` - folder z CSS i JS
- `asset-manifest.json` - manifest

**Inne pliki API:**
- `companies.py3` - API firm
- `employees.py3` - API pracowników
- `users.py3` - API użytkowników
- `time_entries.py3` - API ewidencji
- `qr_scan.py3` - API skanowania QR
- `qr_generate.py3` - API generowania QR

### 3. **USTAW UPRAWNIENIA:**
```bash
chmod 755 *.py3
chmod 644 *.py
chmod 644 *.html
```

### 4. **TESTOWANIE KROK PO KROKU:**

#### A) Test diagnostyczny:
```bash
curl https://TWOJA-DOMENA.home.pl/diagnose.py3
```
**Spodziewany wynik:** JSON z informacjami o systemie

#### B) Test inicjalizacji:
```bash
curl https://TWOJA-DOMENA.home.pl/init.py3
```
**Spodziewany wynik:** 
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

#### C) Test logowania:
```bash
curl -X POST https://TWOJA-DOMENA.home.pl/login.py3 \
  -H "Content-Type: application/json" \
  -d '{"username":"owner","password":"owner123"}'
```
**Spodziewany wynik:** JSON z tokenem i danymi użytkownika

#### D) Test strony głównej:
```bash
curl https://TWOJA-DOMENA.home.pl/
```
**Spodziewany wynik:** HTML strona główna

### 5. **JEŚLI NADAL PROBLEMY:**

#### A) Sprawdź logi błędów w panelu home.pl
#### B) Uruchom diagnostykę:
```bash
https://TWOJA-DOMENA.home.pl/diagnose.py3
```

#### C) Sprawdź uprawnienia plików:
```bash
ls -la *.py3
# Powinno być: -rwxr-xr-x (755)
```

### 6. **KONTA DOMYŚLNE:**
- **Owner:** `owner` / `owner123` (pełny dostęp)
- **Admin:** `admin` / `admin123` (zarządzanie firmą)
- **User:** `user` / `user123` (skanowanie QR)

### 7. **RÓŻNICE W NAPRAWIONYCH PLIKACH:**
- ✅ `utils.py` - usunięto błędną linię, naprawiono CORS
- ✅ `init.py3` - dodano obsługę błędów importu
- ✅ `diagnose.py3` - NOWY plik do diagnostyki
- ✅ Wszystkie pliki przetestowane lokalnie

### 8. **JEŚLI INIT.PY3 NIE DZIAŁA:**
Plik `init.py3` ma teraz failsafe - jeśli import utils się nie powiedzie, utworzy bazę danych w trybie podstawowym.

### 9. **WSPARCIE:**
Jeśli nadal masz problemy, uruchom:
```bash
https://TWOJA-DOMENA.home.pl/diagnose.py3
```
I wyślij wynik dla diagnozy.

**Status:** ✅ GOTOWY DO WDROŻENIA
**Testowane:** ✅ Wszystkie pliki przetestowane
**Failsafe:** ✅ Dodano obsługę błędów