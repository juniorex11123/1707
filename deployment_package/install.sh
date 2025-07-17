#!/bin/bash

# 🚀 TimeTracker Pro - Skrypt instalacyjny dla home.pl

echo "🚀 TimeTracker Pro - Instalacja na home.pl"
echo "=========================================="

# Sprawdź czy jesteśmy w odpowiednim katalogu
if [ ! -d "backend" ] || [ ! -d "frontend_build" ]; then
    echo "❌ Błąd: Uruchom skrypt w katalogu z plikami deploymentu"
    exit 1
fi

# Konfiguracja
read -p "Podaj domenę (np. yourdomain.home.pl): " DOMAIN
read -p "Ścieżka do public_html (np. /home/username/domains/$DOMAIN/public_html): " PUBLIC_HTML
read -p "Ścieżka do katalogu aplikacji (np. /home/username/apps/timetracker): " APP_DIR

echo "📁 Tworzenie katalogów..."
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/logs"

echo "📋 Kopiowanie plików frontend..."
cp -r frontend_build/* "$PUBLIC_HTML/"

echo "📋 Kopiowanie plików backend..."
cp -r backend/* "$APP_DIR/"

echo "🔧 Konfiguracja środowiska..."
cd "$APP_DIR"

# Aktualizacja konfiguracji
sed -i "s/yourdomain.home.pl/$DOMAIN/g" .env.production

echo "📦 Instalacja wymaganych bibliotek..."
pip install -r requirements.txt

echo "🔐 Ustawienie uprawnień..."
chmod +x run_production.py
chmod 755 "$PUBLIC_HTML"
chmod 644 "$PUBLIC_HTML"/*

echo "✅ Instalacja zakończona!"
echo ""
echo "🔧 Następne kroki:"
echo "1. Skonfiguruj MongoDB w .env.production"
echo "2. Uruchom backend: python run_production.py"
echo "3. Sprawdź domenę: https://$DOMAIN"
echo ""
echo "🔐 Domyślni użytkownicy:"
echo "- Owner: owner/owner123"
echo "- Admin: admin/admin123"
echo "- User: user/user123"