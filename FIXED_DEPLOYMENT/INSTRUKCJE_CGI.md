# 🔧 INSTRUKCJE NAPRAWY CGI - TimeTracker Pro

## ❌ PROBLEM:
Serwer wyświetla kod źródłowy zamiast wykonywać pliki Python jako CGI

## ✅ ROZWIĄZANIE KROK PO KROKU:

### **1. WGRAJ WSZYSTKIE PLIKI Z FOLDERU NA SERWER**

### **2. USTAW UPRAWNIENIA:**
```bash
chmod 755 *.py3 *.cgi *.py
chmod 644 *.html *.json
chmod 644 .htaccess
```

### **3. PRZETESTUJ RÓŻNE ROZSZERZENIA:**

#### **A) Test podstawowy CGI:**
```bash
curl https://TWOJA-DOMENA.home.pl/test.py3
curl https://TWOJA-DOMENA.home.pl/test.cgi
curl https://TWOJA-DOMENA.home.pl/test.py
```
**Cel:** Znaleźć które rozszerzenie działa

#### **B) Test inicjalizacji (wypróbuj w kolejności):**
```bash
curl https://TWOJA-DOMENA.home.pl/init_simple.py3
curl https://TWOJA-DOMENA.home.pl/init_simple.cgi
curl https://TWOJA-DOMENA.home.pl/init_simple.py
```

#### **C) Test oryginalnego init:**
```bash
curl https://TWOJA-DOMENA.home.pl/init.py3
curl https://TWOJA-DOMENA.home.pl/init.cgi
```

### **4. JEŚLI NADAL NIE DZIAŁA:**

#### **A) Sprawdź panel home.pl:**
1. Idź do "Ustawienia" → "Skrypty CGI"
2. Sprawdź czy Python jest włączony
3. Sprawdź dozwolone rozszerzenia

#### **B) Sprawdź logi błędów:**
Panel administracyjny → Logi → Błędy

#### **C) Skontaktuj się z supportem home.pl:**
Zapytaj: "Jak włączyć skrypty Python CGI? Jakie rozszerzenia są obsługiwane?"

### **5. ALTERNATYWNE ROZWIĄZANIA:**

#### **A) Jeśli CGI nie działa, użyj PHP:**
Możemy przepisać na PHP (prosty wariant)

#### **B) Użyj innego hostingu:**
Np. PythonAnywhere, Heroku, DigitalOcean

### **6. STRUKTURA PLIKÓW NA SERWERZE:**
```
public_html/
├── .htaccess              # Konfiguracja Apache
├── index.html             # Strona główna
├── static/               # CSS, JS, obrazy
├── test.py3              # Test CGI
├── test.cgi              # Test CGI
├── test.py               # Test CGI
├── init_simple.py3       # Uproszczona inicjalizacja
├── init_simple.cgi       # Uproszczona inicjalizacja
├── init.py3              # Pełna inicjalizacja
├── init.cgi              # Pełna inicjalizacja
└── [inne pliki API]
```

### **7. SPODZIEWANE WYNIKI:**

#### **Test CGI (test.py3):**
```json
{
  "message": "CGI Test Successful",
  "status": "working",
  "python_version": "3.x",
  "request_method": "GET"
}
```

#### **Test inicjalizacji (init_simple.py3):**
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

### **8. KOLEJNOŚĆ TESTOWANIA:**
1. 🔍 `test.py3` → `test.cgi` → `test.py`
2. 🔍 `init_simple.py3` → `init_simple.cgi` → `init_simple.py`
3. 🔍 `init.py3` → `init.cgi`
4. 🔍 Sprawdź panel home.pl
5. 🔍 Sprawdź logi błędów
6. 📞 Skontaktuj się z supportem

### **9. JEŚLI WSZYSTKO ZAWIEDZIE:**
- Użyj hostingu z pełną obsługą Python (np. PythonAnywhere)
- Lub przepisz na PHP
- Lub użyj statycznego hostingu + zewnętrznego API

**Status:** 🔧 DIAGNOSTIC MODE
**Cel:** Znaleźć działające rozszerzenie plików