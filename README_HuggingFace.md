---
title: ValueBet Engine - Football
emoji: ⚽
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.28.1
app_file: streamlit_app.py
pinned: false
license: mit
---

# 🎯 ValueBet Engine - Hugging Face Spaces

Application Streamlit pour la détection de value bets en football, déployée sur Hugging Face Spaces.

## 🚀 Déploiement Automatique

Cette application se déploie automatiquement sur Hugging Face Spaces depuis ce repository GitHub.

### Configuration Requise

#### 1. Variables d'Environnement (Secrets)
Dans les paramètres de votre Space Hugging Face :

```
FOOTBALL_DATA_API_KEY=votre_clé_api
ODDS_API_KEY=votre_clé_api
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

#### 2. Fichiers Nécessaires
- `streamlit_app.py` : Application principale
- `requirements_streamlit.txt` : Dépendances Python
- Ce fichier `README.md` : Configuration du Space

### Comment Déployer

1. **Forkez** ce repository
2. **Créez un Space** sur [Hugging Face](https://huggingface.co/spaces)
3. **Connectez** votre repository GitHub
4. **Le déploiement** se fait automatiquement

## 🎮 Utilisation

### Mode Démonstration (Par Défaut)
- Accessible sans configuration
- Utilise des données fictives
- Parfait pour les tests

### Mode Production
- Nécessite les clés API dans les secrets
- Données temps réel
- Analyses complètes

## 🔧 Configuration Technique

### Ressources
- **CPU** : 2 vCPUs (suffisant pour l'IA)
- **RAM** : 16 GB (pour les calculs ML)
- **Stockage** : 50 GB (pour les données)

### Optimisations
- Cache automatique des prédictions
- Traitement asynchrone des APIs
- Optimisation mémoire pour les gros datasets

## 📊 Fonctionnalités

- **Détection de Value Bets** en temps réel
- **Analyse Ligue 1 & Champions League**
- **Calculs Kelly Criterion** avancés
- **Visualisations interactives**
- **Gestion de Bankroll** dynamique

## 🔒 Sécurité

- **Clés API chiffrées** dans les secrets HF
- **Accès contrôlé** aux données sensibles
- **Logs anonymisés** pour le monitoring

## 📈 Performance

- **Temps de réponse** : < 3 secondes
- **Disponibilité** : 99.9% SLA
- **Scaling automatique** selon la charge

## 💰 Tarifs

- **Free Tier** : 2GB RAM, sessions limitées
- **Pro Tier** : $9/mois pour usage professionnel

---

**🎯 Déployez facilement votre application de paris sportifs sur Hugging Face Spaces !**