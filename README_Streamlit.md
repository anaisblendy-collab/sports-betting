# 🎯 ValueBet Engine - Interface Streamlit

Interface web moderne pour la détection de value bets en Ligue 1 avec gestion de bankroll dynamique.

## 🚀 Démarrage Rapide

### Option 1: Déploiement GitHub Spaces (Recommandé)

1. **Forkez** ce repository sur GitHub
2. **Allez dans Settings > Pages** de votre repository
3. **Activez GitHub Spaces** et sélectionnez "Deploy from a branch"
4. **Configurez les secrets** dans Settings > Secrets and variables > Actions :
   - `FOOTBALL_DATA_API_KEY` : Votre clé API Football-Data.org
   - `ODDS_API_KEY` : Votre clé API The Odds API
5. **Pushez** vos changements - le déploiement se fait automatiquement !

### Option 2: Exécution Locale

#### 1. Installation des dépendances
```bash
pip install -r requirements_streamlit.txt
```

#### 2. Configuration des variables d'environnement (optionnel)
```bash
cp .env.example .env
# Éditez .env avec vos clés API
```

#### 3. Lancement de l'application
```bash
streamlit run streamlit_app.py
```

#### 4. Accès à l'application
Ouvrez votre navigateur à l'adresse : `http://localhost:8501`

## 🎮 Utilisation

### Mode Démonstration (Recommandé pour commencer)
1. **Sélectionnez** "🎭 Démonstration" dans la sidebar
2. **Configurez** vos paramètres de bankroll :
   - Capital initial : 10,000€
   - Fraction Kelly : 0.25 (conservateur)
   - Mise max : 2% du capital
3. **Cliquez** sur "🚀 Lancer l'Analyse"
4. **Explorez** les value bets détectés !

### Mode Production
1. **Obtenez des clés API gratuites** :
   - [Football-Data.org](https://www.football-data.org/) (gratuit)
   - [OddsAPI](https://the-odds-api.com/) (freemium)
2. **Configurez les variables d'environnement** :
   ```bash
   export FOOTBALL_DATA_API_KEY="votre_clé"
   export ODDS_API_KEY="votre_clé"
   ```
3. **Sélectionnez** "🔴 Production" et entrez vos clés
4. **Lancez l'analyse** avec des données réelles !

## ☁️ Déploiement GitHub Spaces

### Configuration Automatique

1. **Workflow GitHub Actions** : Le déploiement se fait automatiquement à chaque push sur `main`
2. **Configuration Spaces** : Le fichier `spaces.json` définit l'environnement de déploiement
3. **Tests intégrés** : Les tests sont exécutés avant chaque déploiement

### Variables d'Environnement

Configurez ces secrets dans **Settings > Secrets and variables > Actions** :

| Secret | Description | Exemple |
|--------|-------------|---------|
| `FOOTBALL_DATA_API_KEY` | Clé API Football-Data.org | `abc123...` |
| `ODDS_API_KEY` | Clé API The Odds API | `def456...` |

### Fichiers de Configuration

- **`spaces.json`** : Configuration du déploiement GitHub Spaces
- **`.github/workflows/deploy-spaces.yml`** : Workflow de déploiement automatisé
- **`.env.example`** : Exemple des variables d'environnement

### URL de Production

Une fois déployé, votre application sera accessible à :
```
https://[votre-username].github.io/[nom-du-repo]/
```

## 🎯 Fonctionnalités

### 📊 Dashboard Interactif
- **Métriques principales** : Value bets détectés, edges, profits
- **Filtres dynamiques** : Par edge minimum et niveau de confiance
- **Tableaux détaillés** : Tous les value bets avec calculs complets

### 💰 Gestion de Bankroll
- **Calculs Kelly avancés** avec fraction configurable
- **Limites de sécurité** : % du capital et montant absolu
- **Visualisation** de l'évolution du capital

### 🎪 Analyse des Marchés
- **Victoire domicile/extérieur**
- **Match nul**
- **Over/Under 2.5 buts** (bientôt disponible)

### 📈 Visualisations
- **Graphiques d'évolution** de la bankroll
- **Distributions** des profits/pertes
- **Métriques de performance** détaillées

## 🛠️ Architecture Technique

### Composants Principaux
```
streamlit_app.py          # Interface web principale
├── LiveValueBetDetector  # Moteur de détection
├── WagerBrain           # Calculs Kelly avancés
├── APIs intégrées       # Football-Data + OddsAPI
└── Modèles ML           # Scikit-Learn classifiers
```

### Flux de Données
1. **Récupération** des matches via APIs
2. **Prédiction** des probabilités par le modèle ML
3. **Calcul EV** : Expected Value = (Prob × Cote) - 1
4. **Filtrage** : Seulement EV > 0 (value bets)
5. **Sizing** : Mise optimale selon Kelly Criterion
6. **Affichage** : Interface interactive avec visualisations

## 🎨 Interface Utilisateur

### Design Moderne
- **Thème professionnel** avec dégradés et animations
- **Responsive design** adapté mobile/desktop
- **Cartes interactives** pour chaque value bet
- **Métriques colorées** pour une lecture rapide

### Navigation Intuitive
- **Sidebar** pour la configuration
- **Boutons principaux** clairement identifiés
- **Filtres** faciles à utiliser
- **Téléchargements** CSV des résultats

## 📊 Exemple de Résultats

### Value Bet Détecté
```
🏆 Nantes vs Rennes - Victoire extérieur
📅 20/09/2025 21:16
🎪 Victoire extérieur
📈 Probabilité: 75.0%
💰 Cote: 6.13
⚡ Edge: 58.7%
💵 Mise optimale: 200€
💎 Profit potentiel: 1,026€
🎯 Confiance: HIGH
```

### Métriques Globales
- **17 value bets** détectés
- **Edge moyen** : 25.0%
- **Edge maximum** : 58.7%
- **Profit total potentiel** : 3,500€

## 🔧 Configuration Avancée

### Paramètres de Risque
```python
kelly_fraction = 0.25    # 25% de Kelly (conservateur)
max_stake_pct = 0.02     # 2% du capital max par pari
max_stake_abs = 500      # 500€ maximum absolu
```

### Seuils de Détection
```python
min_edge_threshold = 0.03  # Edge minimum 3%
confidence_levels = ['HIGH', 'MEDIUM', 'LOW']
```

## 🚨 Conseils d'Utilisation

### Pour les Débutants
1. **Commencez** en mode démonstration
2. **Ajustez** progressivement les paramètres
3. **Observez** les résultats avant d'investir

### Pour les Confirmés
1. **Utilisez** des vraies clés API
2. **Ajustez** la fraction Kelly selon votre tolérance au risque
3. **Surveillez** régulièrement les performances

## 🔒 Sécurité et Limites

### Gestion des Risques
- **Limites intégrées** pour éviter les pertes importantes
- **Stop-loss automatique** à 30% de drawdown
- **Validation** de toutes les entrées utilisateur

### Limitations
- **Données fictives** en mode démo
- **APIs gratuites** avec limites de taux
- **Modèle ML** à entraîner régulièrement

## 🎯 Roadmap

### Prochaines Fonctionnalités
- [ ] **Notifications temps réel** (email, Telegram)
- [ ] **Backtesting historique** intégré
- [ ] **Plus de championnats** (Premier League, La Liga, etc.)
- [ ] **Analyse de sentiment** des réseaux sociaux
- [ ] **Optimisation automatique** des paramètres

## 📞 Support

### Ressources
- **Documentation** : Ce README
- **Code source** : Scripts Python commentés
- **Exemples** : Données de démonstration

### Debugging
```bash
# Vérifier les logs
streamlit run streamlit_app.py --logger.level=debug

# Mode développement
streamlit run streamlit_app.py --server.headless=true
```

---

**🎯 Prêt à découvrir vos premiers value bets ? Lancez l'application et commencez votre analyse !**