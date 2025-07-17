#!/bin/bash

# TimeTracker Pro - Skrypt pakowania dla home.pl
# Tworzy gotowy pakiet do uploadowania na hosting

echo "🚀 TimeTracker Pro - Pakowanie dla home.pl"
echo "=========================================="

# Sprawdź czy jesteśmy w odpowiednim katalogu
if [ ! -d "frontend_build" ] || [ ! -d "backend_cgi" ]; then
    echo "❌ Błąd: Brak wymaganych katalogów"
    exit 1
fi

# Utwórz katalog tymczasowy
mkdir -p deployment_files

echo "📁 Kopiowanie plików frontend..."
cp -r frontend_build/* deployment_files/

echo "📁 Kopiowanie plików backend..."
cp -r backend_cgi/* deployment_files/

echo "📝 Tworzenie pliku README..."
cat > deployment_files/README_DEPLOYMENT.txt << 'EOF'
# TimeTracker Pro - Deployment na home.pl

## INSTRUKCJE:

1. Wgraj WSZYSTKIE pliki z tego folderu do katalogu public_html/ na home.pl
2. Otwórz w przeglądarce: https://TWOJA-DOMENA.home.pl/init.py3
3. Otwórz stronę główną: https://TWOJA-DOMENA.home.pl/
4. Kliknij "Zaloguj do panelu" i użyj: owner/owner123

## STRUKTURA PLIKÓW:

- index.html - Strona główna
- static/ - Pliki CSS/JS
- .htaccess - Konfiguracja Apache
- init.py3 - Inicjalizacja bazy danych
- login.py3 - Endpoint logowania
- *.py3 - Pozostałe endpointy API

## KONTA DOMYŚLNE:
- owner/owner123 - Administrator systemu
- admin/admin123 - Administrator firmy  
- user/user123 - Użytkownik

GOTOWY DO WDROŻENIA! 🚀
EOF

echo "📦 Liczenie plików..."
FILE_COUNT=$(find deployment_files -type f | wc -l)
TOTAL_SIZE=$(du -sh deployment_files | cut -f1)

echo "✅ Pakiet gotowy!"
echo "📊 Statystyki:"
echo "   - Pliki: $FILE_COUNT"
echo "   - Rozmiar: $TOTAL_SIZE"
echo "   - Lokalizacja: deployment_files/"
echo ""
echo "🚀 Następne kroki:"
echo "1. Wgraj zawartość folderu 'deployment_files/' do public_html/"
echo "2. Uruchom https://TWOJA-DOMENA.home.pl/init.py3"
echo "3. Otwórz https://TWOJA-DOMENA.home.pl/"
echo ""
echo "🎉 Aplikacja jest gotowa do wdrożenia!"