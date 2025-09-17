#!/bin/bash
# Script de déploiement rapide pour Streamlit Cloud

echo "🚀 Déploiement ValueBet Engine sur Streamlit Cloud"
echo "=================================================="

# Vérification des prérequis
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé"
    exit 1
fi

if ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé"
    exit 1
fi

# Vérification du repository
if [ ! -d ".git" ]; then
    echo "❌ Ce n'est pas un repository Git"
    exit 1
fi

# Vérification des fichiers requis
required_files=("streamlit_app.py" "requirements_streamlit.txt" "README_Streamlit.md")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Fichier manquant: $file"
        exit 1
    fi
done

echo "✅ Prérequis vérifiés"

# Création du fichier de configuration Streamlit
cat > .streamlit/config.toml << EOF
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[theme]
base = "light"
primaryColor = "#1e3c72"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#2c3e50"

[browser]
gatherUsageStats = false
EOF

echo "✅ Configuration Streamlit créée"

# Vérification des secrets (optionnel)
echo ""
echo "🔐 Configuration des Secrets (nécessaire pour la production):"
echo "1. Allez sur https://share.streamlit.io/"
echo "2. Connectez votre repository GitHub"
echo "3. Dans Settings > Secrets, ajoutez:"
echo "   - FOOTBALL_DATA_API_KEY"
echo "   - ODDS_API_KEY"
echo ""

# Instructions de déploiement
echo "📦 Instructions de déploiement:"
echo "1. Poussez vos changements sur GitHub:"
echo "   git add ."
echo "   git commit -m 'Ready for Streamlit Cloud deployment'"
echo "   git push origin main"
echo ""
echo "2. Déployez sur Streamlit Cloud:"
echo "   - Allez sur https://share.streamlit.io/"
echo "   - Connectez votre repository"
echo "   - Cliquez sur 'Deploy'"
echo ""
echo "3. Votre app sera accessible à l'URL fournie par Streamlit Cloud"
echo ""

# Test local optionnel
read -p "🧪 Voulez-vous tester localement avant le déploiement? (y/n): " test_local
if [[ $test_local =~ ^[Yy]$ ]]; then
    echo "🧪 Test local en cours..."
    python -m streamlit run streamlit_app.py --server.headless true --server.port 8501
fi

echo ""
echo "🎉 Configuration terminée!"
echo "📱 Votre ValueBet Engine est prêt pour Streamlit Cloud"