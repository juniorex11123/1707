# 🚀 INSTRUKCJE WGRANIA - JEDEN FOLDER NA HOSTING

## 📁 Zawartość tego folderu
Ten folder zawiera WSZYSTKIE niezbędne pliki do uruchomienia TimeTracker Pro na hostingu home.pl.

## 🔧 Jak wgrać na hosting:

### 1. Wgraj WSZYSTKIE pliki z tego folderu do katalogu głównego domeny (public_html/)

```
public_html/
├── index.html               # Strona główna
├── static/                  # Pliki CSS, JS, obrazy
├── .htaccess               # Konfiguracja Apache
├── init.py3                # Inicjalizacja bazy danych
├── login.py3               # API logowania
├── employees.py3           # API pracowników
├── companies.py3           # API firm
├── users.py3               # API użytkowników
├── time_entries.py3        # API ewidencji czasu
├── qr_scan.py3             # API skanowania QR
├── qr_generate.py3         # API generowania QR
├── database.py3            # Obsługa SQLite
├── auth.py3                # Uwierzytelnianie
├── utils.py3               # Funkcje pomocnicze
└── timetracker_pro.db      # Baza danych (opcjonalnie)
```

### 2. Pierwsza inicjalizacja

Po wgraniu plików:
1. Otwórz w przeglądarce: `https://twoja-domena.pl/init.py3`
2. Powinieneś zobaczyć komunikat: "Database initialized successfully"
3. Otwórz: `https://twoja-domena.pl/`
4. Kliknij "Zaloguj do panelu"
5. Użyj konta: `owner` / `owner123`

### 3. Konta domyślne

Po inicjalizacji dostępne są:
- **owner / owner123** - Administrator systemu
- **admin / admin123** - Administrator firmy  
- **user / user123** - Użytkownik firmy

⚠️ **Zmień hasła po pierwszym logowaniu!**

## 🔧 Wymagania hostingu:

✅ Python 3.6+ (obsługiwane przez home.pl)
✅ SQLite (wbudowane w Python)
✅ Rozszerzenia .py3 (obsługiwane przez home.pl)
✅ mod_rewrite (Apache)
✅ HTTPS/SSL

## 🎯 Funkcjonalności:

✅ Zarządzanie firmami i użytkownikami
✅ Ewidencja czasu pracy
✅ Generowanie i skanowanie QR kodów
✅ Różne poziomy uprawnień
✅ Responsywny design

## 🔍 Rozwiązywanie problemów:

### Problem: Strona nie ładuje się
- Sprawdź czy `.htaccess` jest wgrany
- Upewnij się, że `index.html` jest w katalogu głównym

### Problem: Skrypty .py3 nie działają
- Sprawdź czy pliki .py3 mają rozszerzenie `.py3` (nie `.py`)
- Upewnij się, że hosting obsługuje Python 3.6

### Problem: Błąd 500 w skryptach
- Sprawdź uprawnienia plików (powinny być 755)
- Sprawdź logi błędów w panelu hostingu

## 📞 Wsparcie:

W przypadku problemów:
1. Sprawdź logi błędów w panelu hostingu
2. Upewnij się, że wszystkie pliki są wgrane
3. Sprawdź uprawnienia plików (755)

---

**Status**: Gotowy do produkcji!
**Wszystko w jednym folderze - wystarczy wgrać pliki! 🚀**