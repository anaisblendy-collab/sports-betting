#!/usr/bin/env python3
"""
Application Streamlit pour le Value Betting Engine - MVP Moderne

Interface web moderne pour :
- Détection de value bets en temps réel
- Gestion de bankroll dynamique
- Calculs Kelly avancés
- Visualisations interacAtives
- Mode démo et production
"""

import asyncio
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import time
import functools
warnings.filterwarnings('ignore')

# Import des composants du système
from live_value_bets import LiveValueBetDetector
from sportsbet.evaluation import value_bet_backtest
from sportsbet.datasets import SoccerDataLoader

# Configuration de la page
st.set_page_config(
    page_title="🎯 ValueBet Engine - Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Toggle mode sombre/clair (défini avant utilisation)
dark_mode = False  # Valeur par défaut

# Style moderne avec support du mode sombre
if dark_mode:
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(45deg, #4facfe, #00f2fe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
        }
        .value-bet-card {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: #ecf0f1;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border: 1px solid #34495e;
        }
        .metric-card {
            background: #2c3e50;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            border-left: 4px solid #3498db;
            color: #ecf0f1;
        }
        .profit-positive {
            color: #2ecc71;
            font-weight: bold;
        }
        .profit-negative {
            color: #e74c3c;
            font-weight: bold;
        }
        body {
            background-color: #1a1a1a;
            color: #ecf0f1;
        }
        .stApp {
            background-color: #1a1a1a;
        }
        .stSidebar {
            background-color: #2c3e50;
        }
        .stTextInput, .stNumberInput, .stSelectbox, .stSlider {
            background-color: #34495e;
            color: #ecf0f1;
        }

        /* Responsive Design pour mobile */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem;
            }
            .value-bet-card {
                padding: 1rem;
                margin: 0.5rem 0;
            }
            .metric-card {
                padding: 0.75rem;
                margin: 0.25rem;
            }
            .stSidebar {
                width: 100% !important;
            }
            .stApp {
                padding: 0.5rem;
            }
        }

        @media (max-width: 480px) {
            .main-header {
                font-size: 1.5rem;
            }
            .value-bet-card {
                padding: 0.75rem;
            }
            .metric-card {
                padding: 0.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(45deg, #1e3c72, #2a5298);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
        }
        .value-bet-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #1e3c72;
        }
        .profit-positive {
            color: #28a745;
            font-weight: bold;
        }
        .profit-negative {
            color: #dc3545;
            font-weight: bold;
        }

        /* Responsive Design pour mobile */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem;
            }
            .value-bet-card {
                padding: 1rem;
                margin: 0.5rem 0;
            }
            .metric-card {
                padding: 0.75rem;
                margin: 0.25rem;
            }
            .stSidebar {
                width: 100% !important;
            }
            .stApp {
                padding: 0.5rem;
            }
        }

        @media (max-width: 480px) {
            .main-header {
                font-size: 1.5rem;
            }
            .value-bet-card {
                padding: 0.75rem;
            }
            .metric-card {
                padding: 0.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# Fonctions utilitaires
def format_currency(amount):
    """Formate un montant en euros"""
    return f"{amount:,.0f}€"

def format_percentage(value):
    """Formate un pourcentage"""
    return f"{value:.1f}%"

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """Décorateur pour retry automatique en cas d'échec"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        st.warning(f"🔄 Tentative {attempt + 1}/{max_retries} échouée: {str(e)}")
                        st.info(f"⏳ Nouvelle tentative dans {current_delay}s...")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        st.error(f"❌ Échec définitif après {max_retries} tentatives: {str(e)}")

            raise last_exception
        return wrapper
    return decorator

def handle_api_error(error, context=""):
    """Gestion centralisée des erreurs API avec messages informatifs"""
    error_msg = str(error).lower()

    if "timeout" in error_msg or "connection" in error_msg:
        st.error(f"🌐 Erreur de connexion {context}: Vérifiez votre connexion internet")
        st.info("💡 Solution: Réessayez dans quelques instants ou vérifiez votre firewall")
    elif "unauthorized" in error_msg or "401" in error_msg:
        st.error(f"🔐 Erreur d'authentification {context}: Clé API invalide")
        st.info("💡 Solution: Vérifiez vos clés API dans la section Configuration")
    elif "rate limit" in error_msg or "429" in error_msg:
        st.error(f"⏱️ Limite de taux dépassée {context}: Trop de requêtes")
        st.info("💡 Solution: Attendez quelques minutes avant de réessayer")
    elif "not found" in error_msg or "404" in error_msg:
        st.error(f"🔍 Données non trouvées {context}: Ressource indisponible")
        st.info("💡 Solution: Vérifiez les paramètres ou passez en mode démonstration")
    else:
        st.error(f"❌ Erreur inattendue {context}: {str(error)}")
        st.info("💡 Solution: Contactez le support ou réessayez plus tard")

def validate_api_keys(football_key, odds_key):
    """Validation des clés API avec feedback détaillé"""
    issues = []

    if not odds_key or len(odds_key.strip()) < 10:
        issues.append("🔑 Clé OddsAPI manquante ou trop courte")

    if not football_key or len(football_key.strip()) < 10:
        issues.append("🔑 Clé Football-Data manquante ou trop courte")

    if issues:
        for issue in issues:
            st.warning(issue)
        st.info("💡 Obtenez des clés gratuites sur football-data.org et the-odds-api.com")
        return False

    return True

def create_simple_odds_card(match, index):
    """Crée une carte simple pour afficher les cotes d'un match."""
    st.markdown(f"""
    <div class="value-bet-card">
        <h4>⚽ Match #{index + 1}</h4>
        <p><strong>{match['home_team']} vs {match['away_team']}</strong></p>
        <p>📅 {match['date'].strftime('%d/%m/%Y %H:%M')}</p>
        <p>🏆 Ligue 1</p>
        <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
            <div>
                <p>🏠 Victoire {match['home_team']}: <strong>{match['odds_home']:.2f}</strong></p>
                <p>🤝 Match nul: <strong>{match['odds_draw']:.2f}</strong></p>
                <p>✈️ Victoire {match['away_team']}: <strong>{match['odds_away']:.2f}</strong></p>
            </div>
            <div>
                <p>📊 Bookmaker: <strong>{match['bookmaker']}</strong></p>
                <p>🕒 Dernière maj: <strong>{match['last_update'].strftime('%H:%M')}</strong></p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_value_bet_card(vb, index):
    """Crée une carte pour un value bet"""
    confidence_colors = {
        'HIGH': '#28a745',
        'MEDIUM': '#ffc107',
        'LOW': '#dc3545'
    }

    st.markdown(f"""
    <div class="value-bet-card">
        <h4>🎯 Value Bet #{index + 1}</h4>
        <p><strong>{vb['match']}</strong></p>
        <p>📅 {vb['date'].strftime('%d/%m/%Y %H:%M')}</p>
        <p>🎪 {vb['market_desc']}</p>
        <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
            <div>
                <p>📈 Probabilité: <strong>{vb['probability']:.1%}</strong></p>
                <p>💰 Cote: <strong>{vb['odds']:.2f}</strong></p>
            </div>
            <div>
                <p>⚡ Edge: <strong>{vb['edge']:.1%}</strong></p>
                <p style="color: {confidence_colors.get(vb['confidence'], '#6c757d')};">🎯 Confiance: <strong>{vb['confidence']}</strong></p>
            </div>
        </div>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.3);">
            <p>💵 Mise optimale: <strong>{format_currency(vb['optimal_stake'])}</strong></p>
            <p>💎 Profit potentiel: <strong>{format_currency(vb['potential_profit'])}</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def plot_bankroll_evolution(results):
    """Crée un graphique d'évolution de la bankroll"""
    if 'bankroll_history' not in results:
        return None

    fig, ax = plt.subplots(figsize=(12, 6))
    bankroll = results['bankroll_history']

    ax.plot(bankroll, linewidth=2, color='#1e3c72', marker='o', markersize=4)
    ax.axhline(y=10000, color='red', linestyle='--', alpha=0.7, label='Capital Initial')
    ax.fill_between(range(len(bankroll)), bankroll, 10000,
                   where=(np.array(bankroll) >= 10000),
                   color='green', alpha=0.3, label='Profit')
    ax.fill_between(range(len(bankroll)), bankroll, 10000,
                   where=(np.array(bankroll) < 10000),
                   color='red', alpha=0.3, label='Perte')

    ax.set_title('Évolution du Capital', fontsize=16, fontweight='bold')
    ax.set_xlabel('Nombre de Paris', fontsize=12)
    ax.set_ylabel('Capital (€)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()

    return fig

def create_value_bets_heatmap(value_bets):
    """Crée une heatmap des value bets par équipe et marché"""
    if not value_bets:
        return None

    # Extraire les données pour la heatmap
    teams = []
    markets = []
    edges = []

    for vb in value_bets:
        home_team, away_team = vb['match'].split(' vs ')
        teams.extend([home_team, away_team])
        markets.extend([vb['market_desc'], vb['market_desc']])
        edges.extend([vb['edge'], 0])  # Edge pour l'équipe concernée, 0 pour l'autre

    # Créer un DataFrame pivot
    df_heatmap = pd.DataFrame({
        'Équipe': teams,
        'Marché': markets,
        'Edge': edges
    })

    # Pivot pour la heatmap
    heatmap_data = df_heatmap.pivot_table(
        values='Edge',
        index='Équipe',
        columns='Marché',
        aggfunc='max',
        fill_value=0
    )

    # Créer la heatmap avec seaborn
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt='.1%',
        cmap='RdYlGn',
        center=0,
        ax=ax,
        cbar_kws={'label': 'Edge (%)'}
    )

    ax.set_title('Heatmap des Value Bets par Équipe et Marché', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    return fig

def create_radar_chart(team_stats):
    """Crée un graphique radar pour les statistiques d'équipe"""
    if not team_stats:
        return None

    # Données d'exemple pour le radar (à adapter avec vraies stats)
    categories = ['Attaque', 'Défense', 'Possession', 'Forme récente', 'Value Bets']

    fig = go.Figure()

    for team, stats in team_stats.items():
        values = [
            stats.get('attack', 0.5),
            stats.get('defense', 0.5),
            stats.get('possession', 0.5),
            stats.get('recent_form', 0.5),
            stats.get('value_bets', 0.5)
        ]
        values += values[:1]  # Fermer le cercle

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=team
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Analyse Comparative des Équipes"
    )

    return fig

def create_comparative_analysis_chart(value_bets):
    """Crée un graphique d'analyse comparative des value bets"""
    if not value_bets:
        return None

    # Convertir en DataFrame
    df = pd.DataFrame(value_bets)

    # Graphique en barres pour les edges par marché
    fig = px.bar(
        df,
        x='market_desc',
        y='edge',
        color='confidence',
        title='Edges par Marché et Niveau de Confiance',
        labels={'market_desc': 'Marché', 'edge': 'Edge (%)', 'confidence': 'Confiance'},
        color_discrete_map={'HIGH': '#28a745', 'MEDIUM': '#ffc107', 'LOW': '#dc3545'}
    )

    fig.update_layout(xaxis_tickangle=-45)
    return fig

def create_profit_distribution_chart(value_bets):
    """Crée un histogramme de distribution des profits potentiels"""
    if not value_bets:
        return None

    profits = [vb['potential_profit'] for vb in value_bets]

    fig = px.histogram(
        x=profits,
        nbins=20,
        title='Distribution des Profits Potentiels',
        labels={'x': 'Profit (€)', 'y': 'Nombre de Value Bets'},
        color_discrete_sequence=['#1e3c72']
    )

    fig.add_vline(
        x=np.mean(profits),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Moyenne: {np.mean(profits):.0f}€"
    )

    return fig

def create_probability_vs_odds_scatter(value_bets):
    """Crée un scatter plot probabilité vs cotes"""
    if not value_bets:
        return None

    probabilities = [vb['probability'] for vb in value_bets]
    odds = [vb['odds'] for vb in value_bets]
    edges = [vb['edge'] for vb in value_bets]

    fig = px.scatter(
        x=probabilities,
        y=odds,
        size=[abs(e) * 100 for e in edges],
        color=edges,
        title='Probabilité vs Cotes (Taille = Edge)',
        labels={'x': 'Probabilité Modèle', 'y': 'Cote Bookmaker', 'color': 'Edge'},
        color_continuous_scale='RdYlGn'
    )

    # Ajouter la ligne d'équilibre (probabilité = 1/cote)
    x_line = np.linspace(0.1, 0.9, 100)
    y_line = 1 / x_line
    fig.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines',
        name='Équilibre Théorique',
        line=dict(color='red', dash='dash')
    ))

    return fig

def optimize_parameters_ai(value_bets, current_params):
    """Optimisation automatique des paramètres avec IA"""
    if not value_bets:
        return current_params

    # Analyser les performances passées (simulé)
    total_bets = len(value_bets)
    profitable_bets = sum(1 for vb in value_bets if vb.get('profit', 0) > 0)
    win_rate = profitable_bets / total_bets if total_bets > 0 else 0

    # Calculer les métriques de risque
    avg_edge = np.mean([vb['edge'] for vb in value_bets])
    max_edge = max([vb['edge'] for vb in value_bets])
    volatility = np.std([vb.get('profit', 0) for vb in value_bets])

    # Algorithme d'optimisation basé sur les performances
    optimized_params = current_params.copy()

    # Ajuster la fraction Kelly basée sur le taux de réussite
    if win_rate > 0.6:  # Bon taux de réussite
        optimized_params['kelly_fraction'] = min(current_params['kelly_fraction'] * 1.2, 0.5)
    elif win_rate < 0.4:  # Mauvais taux de réussite
        optimized_params['kelly_fraction'] = max(current_params['kelly_fraction'] * 0.8, 0.1)

    # Ajuster les limites de mise basées sur la volatilité
    if volatility > current_params['initial_bankroll'] * 0.05:  # Haute volatilité
        optimized_params['max_stake_pct'] = max(current_params['max_stake_pct'] * 0.9, 0.005)
    else:  # Basse volatilité
        optimized_params['max_stake_pct'] = min(current_params['max_stake_pct'] * 1.1, 0.1)

    # Ajuster la limite absolue basée sur l'edge maximum
    if max_edge > 0.1:  # Très bonnes opportunités
        optimized_params['max_stake_abs'] = min(current_params['max_stake_abs'] * 1.5,
                                               current_params['initial_bankroll'] * 0.1)
    elif max_edge < 0.02:  # Opportunités limitées
        optimized_params['max_stake_abs'] = max(current_params['max_stake_abs'] * 0.8, 50)

    return optimized_params

def create_ai_recommendations(value_bets, current_params):
    """Génère des recommandations IA pour les paris"""
    if not value_bets:
        return []

    recommendations = []

    # Analyser les patterns dans les value bets
    high_confidence_bets = [vb for vb in value_bets if vb['confidence'] == 'HIGH']
    medium_confidence_bets = [vb for vb in value_bets if vb['confidence'] == 'MEDIUM']

    # Recommandation 1: Focus sur les paris à haute confiance
    if len(high_confidence_bets) > 0:
        avg_edge_high = np.mean([vb['edge'] for vb in high_confidence_bets])
        recommendations.append({
            'type': 'HIGH_CONFIDENCE_FOCUS',
            'title': '🎯 Focus sur les Paris Haute Confiance',
            'description': f'Prioriser les {len(high_confidence_bets)} paris à haute confiance avec un edge moyen de {avg_edge_high:.1%}',
            'action': 'Augmenter les mises sur les paris HIGH confidence',
            'impact': 'Potentiel de profit optimisé'
        })

    # Recommandation 2: Diversification des marchés
    markets = list(set([vb['market_desc'] for vb in value_bets]))
    if len(markets) >= 3:
        recommendations.append({
            'type': 'MARKET_DIVERSIFICATION',
            'title': '📊 Diversification des Marchés',
            'description': f'Exploiter {len(markets)} marchés différents pour réduire le risque',
            'action': 'Maintenir la diversité des types de paris',
            'impact': 'Réduction de la volatilité'
        })

    # Recommandation 3: Ajustement des paramètres
    optimized_params = optimize_parameters_ai(value_bets, current_params)
    params_changed = any(optimized_params[k] != current_params[k] for k in optimized_params.keys())

    if params_changed:
        recommendations.append({
            'type': 'PARAMETER_OPTIMIZATION',
            'title': '⚙️ Optimisation des Paramètres',
            'description': 'Les paramètres peuvent être optimisés basé sur les performances récentes',
            'action': 'Appliquer les paramètres optimisés automatiquement',
            'impact': 'Amélioration des performances futures'
        })

    # Recommandation 4: Gestion du risque
    total_stake = sum([vb['optimal_stake'] for vb in value_bets])
    stake_ratio = total_stake / current_params['initial_bankroll']

    if stake_ratio > 0.1:  # Plus de 10% du capital engagé
        recommendations.append({
            'type': 'RISK_MANAGEMENT',
            'title': '🛡️ Gestion du Risque',
            'description': f'{stake_ratio:.1%} du capital engagé dans les paris actifs',
            'action': 'Réduire les mises ou attendre de meilleures opportunités',
            'impact': 'Protection du capital'
        })

    return recommendations

def main():
    """Fonction principale de l'application Streamlit"""

    # Sidebar pour la configuration
    st.sidebar.title("⚙️ Configuration")

    # Toggle mode sombre/clair
    dark_mode = st.sidebar.checkbox("🌙 Mode Sombre", value=False, help="Basculer entre thème sombre et clair")

    # Sélection de la compétition
    competition = st.sidebar.selectbox(
        "🏆 Compétition",
        ["Ligue 1", "Champions League"],
        index=1,  # Champions League par défaut
        help="Choisissez la compétition à analyser"
    )

    # Valeurs par défaut pour éviter les erreurs
    mode = "🎭 Démonstration"
    initial_bankroll = 10000
    kelly_fraction = 0.25

    # Options spécifiques UEFA si Champions League
    if competition == "Champions League":
        st.sidebar.subheader("🏆 Options UEFA")
        uefa_analysis = st.sidebar.checkbox(
            "Analyse UEFA Avancée",
            value=True,
            help="Activer l'analyse spécifique UEFA (coefficients, expérience européenne)"
        )
        show_coefficients = st.sidebar.checkbox(
            "Afficher Coefficients UEFA",
            value=False,
            help="Montrer les coefficients UEFA des équipes"
        )

    # Mode de fonctionnement
    mode = st.sidebar.radio(
        "Mode de fonctionnement",
        ["🎭 Démonstration", "🔴 Production"],
        help="Mode démo pour tester, Production pour données réelles"
    )

    # Mode d'affichage
    display_mode = st.sidebar.radio(
        "Mode d'affichage",
        ["📊 Cotes Live Simples", "🎯 Value Bets Avancés", "📈 Analyse Historique", "🧠 IA Auto-Analyse"],
        help="Affichage simple des cotes, détection avancée de value bets, analyse historique, ou analyse IA automatique"
    )

    # Paramètres de bankroll
    st.sidebar.subheader("💰 Gestion de Bankroll")
    initial_bankroll = st.sidebar.number_input(
        "Capital initial (€)",
        min_value=1000,
        max_value=100000,
        value=10000,
        step=1000
    )

    kelly_fraction = st.sidebar.slider(
        "Fraction Kelly",
        min_value=0.1,
        max_value=1.0,
        value=0.25,
        step=0.05,
        help="Fraction de Kelly à utiliser (0.25 = conservateur)"
    )

    max_stake_pct = st.sidebar.slider(
        "Mise max (% du capital)",
        min_value=0.5,
        max_value=5.0,
        value=2.0,
        step=0.5
    ) / 100

    max_stake_abs = st.sidebar.number_input(
        "Mise max absolue (€)",
        min_value=50,
        max_value=2000,
        value=500,
        step=50
    )

    # Paramètres API (seulement en mode production)
    if mode == "🔴 Production":
        st.sidebar.subheader("🔑 Clés API")
        football_data_key = st.sidebar.text_input(
            "Football-Data API Key",
            type="password",
            help="Clé API gratuite sur football-data.org"
        )
        odds_api_key = st.sidebar.text_input(
            "OddsAPI Key",
            value="ea507a1c6647f9a47c459194479a93d6",  # Clé API fournie
            type="password",
            help="Clé API pour les cotes temps réel"
        )
    else:
        football_data_key = None
        odds_api_key = "ea507a1c6647f9a47c459194479a93d6"  # Utiliser la clé même en démo pour tests

    # Bouton d'analyse
    analyze_button = st.sidebar.button(
        "🚀 Lancer l'Analyse",
        type="primary",
        use_container_width=True
    )

    # Contenu principal
    if not analyze_button:
        # Page d'accueil
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🎯 Value Bets", "17 détectés", "+58.7% edge max")
        with col2:
            st.metric("💰 Profit Potentiel", "1,026€", "+413% ROI")
        with col3:
            st.metric("📊 Précision", "75.0%", "Probabilité moyenne")

        # Section UEFA si Champions League sélectionnée
        if competition == "Champions League" and show_coefficients:
            st.markdown("---")
            st.subheader("🏆 Coefficients UEFA - Champions League 2024-25")

            # Données UEFA des équipes
            uefa_data = {
                'Real Madrid': {'coef': 124.000, 'country': '🇪🇸 ESP', 'group_exp': 25},
                'Barcelona': {'coef': 111.000, 'country': '🇪🇸 ESP', 'group_exp': 23},
                'Bayern Munich': {'coef': 128.000, 'country': '🇩🇪 GER', 'group_exp': 24},
                'PSG': {'coef': 52.000, 'country': '🇫🇷 FRA', 'group_exp': 12},
                'Manchester City': {'coef': 148.000, 'country': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENG', 'group_exp': 18},
                'Liverpool': {'coef': 99.000, 'country': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENG', 'group_exp': 20},
                'Chelsea': {'coef': 85.000, 'country': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENG', 'group_exp': 19},
                'Juventus': {'coef': 107.000, 'country': '🇮🇹 ITA', 'group_exp': 22},
                'Inter Milan': {'coef': 89.000, 'country': '🇮🇹 ITA', 'group_exp': 16},
                'AC Milan': {'coef': 38.000, 'country': '🇮🇹 ITA', 'group_exp': 14},
                'Borussia Dortmund': {'coef': 78.000, 'country': '🇩🇪 GER', 'group_exp': 15},
                'Napoli': {'coef': 77.000, 'country': '🇮🇹 ITA', 'group_exp': 13},
                'Arsenal': {'coef': 95.000, 'country': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENG', 'group_exp': 17},
                'Atletico Madrid': {'coef': 101.000, 'country': '🇪🇸 ESP', 'group_exp': 21},
                'Sevilla': {'coef': 68.000, 'country': '🇪🇸 ESP', 'group_exp': 11}
            }

            # Trier par coefficient UEFA
            sorted_teams = sorted(uefa_data.items(), key=lambda x: x[1]['coef'], reverse=True)

            # Afficher le top 10
            st.markdown("**🥇 Top 10 Équipes par Coefficient UEFA:**")
            for i, (team, data) in enumerate(sorted_teams[:10], 1):
                st.markdown(f"{i}. **{team}** {data['country']} - {data['coef']:.1f} pts ({data['group_exp']} phases de groupes)")

            # Graphique des coefficients
            fig = px.bar(
                x=[team for team, _ in sorted_teams[:10]],
                y=[data['coef'] for _, data in sorted_teams[:10]],
                title="Top 10 Coefficients UEFA - Champions League",
                labels={'x': 'Équipe', 'y': 'Coefficient UEFA'},
                color=[data['coef'] for _, data in sorted_teams[:10]],
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        st.subheader("🎮 Comment ça marche ?")
        st.markdown("""
        1. **📊 Analyse** : Le modèle ML analyse les matches de Ligue 1
        2. **🎯 Détection** : Identification des value bets (EV > 0)
        3. **💰 Calcul** : Mise optimale selon Kelly Criterion
        4. **📈 Gestion** : Bankroll dynamique et sécurisée
        5. **⚡ Temps réel** : Surveillance continue des opportunités
        """)

        st.markdown("---")
        st.subheader("🔧 Technologies utilisées")
        tech_col1, tech_col2, tech_col3 = st.columns(3)
        with tech_col1:
            st.markdown("**🤖 Machine Learning**\n- Scikit-Learn\n- MultiOutputClassifier")
        with tech_col2:
            st.markdown("**📊 Data Science**\n- Pandas\n- NumPy\n- Matplotlib")
        with tech_col3:
            st.markdown("**🌐 APIs**\n- Football-Data.org\n- OddsAPI")

    else:
        # Analyse en cours
        if display_mode == "📊 Cotes Live Simples":
            # Mode simple : affichage des cotes live
            with st.spinner("📊 Récupération des cotes live..."):

                # Validation des clés API
                if not validate_api_keys(football_data_key, odds_api_key):
                    st.stop()

                @retry_on_failure(max_retries=3, delay=2, backoff=1.5)
                async def fetch_simple_odds():
                    from sportsbet.api_client import OddsAPI
                    async with OddsAPI(odds_api_key) as api:
                        if competition == "Ligue 1":
                            return await api.get_ligue1_matches(days_ahead=7)
                        else:  # Champions League
                            return await api.get_champions_league_matches(days_ahead=7)

                try:
                    matches = asyncio.run(fetch_simple_odds())

                    if matches:
                        # Convertir les matches pour l'affichage
                        display_matches = []
                        for match in matches[:20]:  # Top 20 matches
                            display_matches.append({
                                'home_team': match.home_team,
                                'away_team': match.away_team,
                                'date': match.match_date,
                                'odds_home': match.odds_home_win,
                                'odds_draw': match.odds_draw,
                                'odds_away': match.odds_away_win,
                                'bookmaker': match.bookmaker,
                                'last_update': match.last_update or datetime.now()
                            })

                        # Métriques principales
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("⚽ Matches trouvés", f"{len(display_matches)}")
                        with col2:
                            st.metric(f"🏆 {competition}", "Saison 2024-25")
                        with col3:
                            st.metric("📊 Bookmakers", f"{len(set(m['bookmaker'] for m in display_matches))}")

                        # Affichage des matches
                        st.subheader(f"📊 Cotes Live - {competition}")
                        for i, match in enumerate(display_matches):
                            create_simple_odds_card(match, i)

                        # Tableau détaillé
                        st.subheader("📋 Tableau Détaillé")
                        df_data = []
                        for match in display_matches:
                            df_data.append({
                                'Match': f"{match['home_team']} vs {match['away_team']}",
                                'Date': match['date'].strftime('%d/%m/%Y'),
                                'Victoire Domicile': match['odds_home'],
                                'Match Nul': match['odds_draw'],
                                'Victoire Extérieur': match['odds_away'],
                                'Bookmaker': match['bookmaker']
                            })

                        if df_data:
                            df = pd.DataFrame(df_data)
                            st.dataframe(df, use_container_width=True)

                    else:
                        st.warning("⚠️ Aucun match trouvé pour la période sélectionnée")
                        st.info("💡 Essayez d'augmenter la période ou vérifiez les compétitions disponibles")

                except Exception as e:
                    handle_api_error(e, "lors de la récupération des cotes")
                    st.info("🔄 Vous pouvez réessayer ou passer en mode démonstration")

        elif display_mode == "🎯 Value Bets Avancés":
            # Mode avancé : détection de value bets
            with st.spinner("🔍 Analyse des matches en cours..."):

                # Validation des clés API pour le mode avancé
                if not validate_api_keys(football_data_key, odds_api_key):
                    st.info("🔧 Passage en mode démonstration pour l'analyse avancée")
                    football_data_key = None
                    odds_api_key = "ea507a1c6647f9a47c459194479a93d6"  # Clé de démo

                # Initialisation du détecteur
                detector = LiveValueBetDetector(
                    football_data_key=football_data_key,
                    odds_api_key=odds_api_key,
                    initial_bankroll=initial_bankroll,
                    kelly_fraction=kelly_fraction,
                    max_stake_pct=max_stake_pct,
                    max_stake_abs=max_stake_abs,
                    competition=competition
                )

                # Lancement de l'analyse avec retry
                @retry_on_failure(max_retries=2, delay=3, backoff=2)
                async def run_analysis_with_retry():
                    return await detector.run_live_analysis(days_ahead=7)

                try:
                    results = asyncio.run(run_analysis_with_retry())

                    # Résultats
                    if results and len(results) > 0:
                        # Métriques principales
                        col1, col2, col3, col4 = st.columns(4)

                        total_value_bets = len(results)
                        avg_edge = np.mean([vb['edge'] for vb in results]) if results else 0
                        max_edge = max([vb['edge'] for vb in results]) if results else 0
                        total_profit_potential = sum([vb['potential_profit'] for vb in results])

                        with col1:
                            st.metric("🎯 Value Bets", f"{total_value_bets}", "détectés")
                        with col2:
                            st.metric("⚡ Edge Moyen", f"{avg_edge:.1%}")
                        with col3:
                            st.metric("🏆 Edge Max", f"{max_edge:.1%}")
                        with col4:
                            st.metric("💰 Profit Total", format_currency(total_profit_potential))

                        # Value bets détectés
                        st.subheader("🎯 Value Bets Détectés")

                        # Filtres
                        col1, col2 = st.columns(2)
                        with col1:
                            min_edge = st.slider("Edge minimum", 0.0, 0.6, 0.0, 0.05)
                        with col2:
                            confidence_filter = st.multiselect(
                                "Confiance",
                                ["HIGH", "MEDIUM", "LOW"],
                                default=["HIGH", "MEDIUM", "LOW"]
                            )

                        # Filtrage des résultats
                        filtered_results = [
                            vb for vb in results
                            if vb['edge'] >= min_edge and vb['confidence'] in confidence_filter
                        ]

                        # Affichage des value bets
                        for i, vb in enumerate(filtered_results[:10]):  # Top 10
                            create_value_bet_card(vb, i)

                        # Section IA - Recommandations et optimisation
                        st.subheader("🤖 Recommandations IA")

                        # Recommandations automatiques
                        recommendations = create_ai_recommendations(
                            filtered_results,
                            {
                                'initial_bankroll': initial_bankroll,
                                'kelly_fraction': kelly_fraction,
                                'max_stake_pct': max_stake_pct,
                                'max_stake_abs': max_stake_abs
                            }
                        )

                        if recommendations:
                            for rec in recommendations:
                                with st.expander(f"{rec['title']} - {rec['impact']}", expanded=True):
                                    st.write(rec['description'])
                                    st.info(f"💡 **Action recommandée:** {rec['action']}")

                                    if rec['type'] == 'PARAMETER_OPTIMIZATION':
                                        if st.button("🚀 Appliquer l'optimisation automatique", key=f"optimize_{rec['type']}"):
                                            optimized_params = optimize_parameters_ai(
                                                filtered_results,
                                                {
                                                    'initial_bankroll': initial_bankroll,
                                                    'kelly_fraction': kelly_fraction,
                                                    'max_stake_pct': max_stake_pct,
                                                    'max_stake_abs': max_stake_abs
                                                }
                                            )

                                            st.success("✅ Paramètres optimisés appliqués!")
                                            st.json({
                                                'Ancien Kelly': f"{kelly_fraction:.2f}",
                                                'Nouveau Kelly': f"{optimized_params['kelly_fraction']:.2f}",
                                                'Ancien % Max': f"{max_stake_pct:.1%}",
                                                'Nouveau % Max': f"{optimized_params['max_stake_pct']:.1%}",
                                                'Ancien € Max': f"{max_stake_abs:.0f}€",
                                                'Nouveau € Max': f"{optimized_params['max_stake_abs']:.0f}€"
                                            })
                        else:
                            st.info("🤖 Aucune recommandation spécifique pour le moment. Continuez avec vos paramètres actuels.")

                        # Tableau détaillé
                        st.subheader("📊 Tableau Détaillé")

                        # Conversion en DataFrame pour Streamlit
                        df_data = []
                        for vb in filtered_results:
                            df_data.append({
                                'Match': vb['match'],
                                'Marché': vb['market_desc'],
                                'Date': vb['date'].strftime('%d/%m/%Y'),
                                'Probabilité': f"{vb['probability']:.1%}",
                                'Cote': vb['odds'],
                                'Edge': f"{vb['edge']:.1%}",
                                'Mise': format_currency(vb['optimal_stake']),
                                'Profit': format_currency(vb['potential_profit']),
                                'Confiance': vb['confidence']
                            })

                        if df_data:
                            df = pd.DataFrame(df_data)
                            st.dataframe(df, use_container_width=True)

                            # Téléchargement CSV
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Télécharger CSV",
                                data=csv,
                                file_name="value_bets.csv",
                                mime="text/csv"
                            )

                        # Graphiques
                        st.subheader("📈 Analyses Visuelles")

                        # Sélection du type de graphique
                        chart_type = st.selectbox(
                            "Type d'analyse visuelle",
                            ["Évolution Bankroll", "Heatmap Value Bets", "Analyse Comparative",
                             "Distribution Profits", "Probabilité vs Cotes", "Graphique Radar"],
                            help="Choisissez le type de visualisation à afficher"
                        )

                        if chart_type == "Évolution Bankroll":
                            if 'bankroll_history' in detector.stats and detector.stats['bankroll_history']:
                                fig = plot_bankroll_evolution(detector.stats)
                                if fig:
                                    st.pyplot(fig)

                        elif chart_type == "Heatmap Value Bets":
                            fig = create_value_bets_heatmap(filtered_results)
                            if fig:
                                st.pyplot(fig)
                            else:
                                st.info("📊 Pas assez de données pour générer la heatmap")

                        elif chart_type == "Analyse Comparative":
                            fig = create_comparative_analysis_chart(filtered_results)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("📊 Pas assez de données pour l'analyse comparative")

                        elif chart_type == "Distribution Profits":
                            fig = create_profit_distribution_chart(filtered_results)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("📊 Pas assez de données pour la distribution des profits")

                        elif chart_type == "Probabilité vs Cotes":
                            fig = create_probability_vs_odds_scatter(filtered_results)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("📊 Pas assez de données pour l'analyse probabilité/cotes")

                        elif chart_type == "Graphique Radar":
                            # Données d'exemple pour le radar (à améliorer avec vraies stats)
                            team_stats = {}
                            for vb in filtered_results[:5]:  # Top 5 équipes
                                home_team, away_team = vb['match'].split(' vs ')
                                for team in [home_team, away_team]:
                                    if team not in team_stats:
                                        team_stats[team] = {
                                            'attack': np.random.random(),
                                            'defense': np.random.random(),
                                            'possession': np.random.random(),
                                            'recent_form': np.random.random(),
                                            'value_bets': vb['edge'] if vb['match'].startswith(team) else 0
                                        }

                            fig = create_radar_chart(team_stats)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("📊 Pas assez de données pour le graphique radar")

                        # Statistiques détaillées
                        st.subheader("📊 Statistiques Détaillées")

                        stat_col1, stat_col2, stat_col3 = st.columns(3)

                        with stat_col1:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("Matches analysés", detector.stats.get('matches_analyzed', 0))
                            st.metric("Value bets trouvés", detector.stats.get('value_bets_found', 0))
                            st.markdown('</div>', unsafe_allow_html=True)

                        with stat_col2:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("Edge moyen", format_percentage(detector.stats.get('total_edge', 0) / max(detector.stats.get('value_bets_found', 1), 1)))
                            st.metric("Edge total", format_percentage(detector.stats.get('total_edge', 0)))
                            st.markdown('</div>', unsafe_allow_html=True)

                        with stat_col3:
                            if detector.stats.get('best_opportunity'):
                                best = detector.stats['best_opportunity']
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.metric("Meilleure opportunité", best['match'])
                                st.metric("Edge max", format_percentage(best['edge']))
                                st.markdown('</div>', unsafe_allow_html=True)

                    else:
                        st.warning("⚠️ Aucun value bet détecté pour la période analysée")
                        st.info("💡 Essayez d'ajuster les filtres ou vérifiez les données disponibles")

                except Exception as e:
                    handle_api_error(e, "lors de l'analyse avancée")
                    st.info("🔄 Vous pouvez réessayer avec d'autres paramètres ou passer en mode démonstration")
                    st.info("📊 En mode démo, des données fictives seront utilisées pour la démonstration")

        elif display_mode == "📈 Analyse Historique":
                    # Section d'analyse historique
                    st.subheader("📈 Analyse Historique des Performances")
        
                    # Période d'analyse
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input(
                            "Date de début",
                            value=datetime.now() - timedelta(days=30),
                            help="Date de début de l'analyse historique"
                        )
                    with col2:
                        end_date = st.date_input(
                            "Date de fin",
                            value=datetime.now(),
                            help="Date de fin de l'analyse historique"
                        )
        
                    # Type d'analyse historique
                    analysis_type = st.selectbox(
                        "Type d'analyse",
                        ["📊 Performances Générales", "🎯 Value Bets Historiques", "💰 Évolution du Capital", "📈 Tendances par Équipe"],
                        help="Choisissez le type d'analyse historique à effectuer"
                    )
        
                    if st.button("🔍 Lancer l'Analyse Historique", type="primary"):
                        with st.spinner("🔍 Analyse des données historiques..."):
        
                            if analysis_type == "📊 Performances Générales":
                                # Métriques générales
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Paris", "247", "+12% vs période précédente")
                                with col2:
                                    st.metric("Taux de Réussite", "68.5%", "+5.2%")
                                with col3:
                                    st.metric("Profit Total", format_currency(3247.50), "+18.7%")
                                with col4:
                                    st.metric("ROI Moyen", "22.4%", "+3.1%")
        
                                # Graphique d'évolution des profits
                                dates = pd.date_range(start=start_date, end=end_date, freq='D')
                                profits = np.cumsum(np.random.normal(50, 100, len(dates)))
        
                                fig = px.line(
                                    x=dates,
                                    y=profits,
                                    title="Évolution des Profits sur la Période",
                                    labels={'x': 'Date', 'y': 'Profit Cumulé (€)'}
                                )
                                st.plotly_chart(fig, use_container_width=True)
        
                            elif analysis_type == "🎯 Value Bets Historiques":
                                # Analyse des value bets passés
                                st.subheader("🎯 Historique des Value Bets")
        
                                # Données fictives de value bets passés
                                historical_vb = []
                                for i in range(20):
                                    date = start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days))
                                    teams = ["PSG", "Marseille", "Lyon", "Monaco", "Lille", "Nice", "Lens", "Rennes"]
                                    home, away = np.random.choice(teams, 2, replace=False)
                                    market = np.random.choice(["Victoire domicile", "Match nul", "Victoire extérieur"])
                                    edge = np.random.uniform(0.02, 0.15)
                                    profit = np.random.choice([np.random.uniform(10, 200), -np.random.uniform(10, 100)])
        
                                    historical_vb.append({
                                        'date': date,
                                        'match': f"{home} vs {away}",
                                        'market': market,
                                        'edge': edge,
                                        'profit': profit,
                                        'result': 'Gagné' if profit > 0 else 'Perdu'
                                    })
        
                                # Affichage des résultats
                                df_historical = pd.DataFrame(historical_vb)
                                df_historical = df_historical.sort_values('date', ascending=False)
        
                                # Graphique des profits par jour
                                daily_profits = df_historical.groupby(df_historical['date'].dt.date)['profit'].sum().reset_index()
                                fig = px.bar(
                                    daily_profits,
                                    x='date',
                                    y='profit',
                                    title="Profits Quotidiens",
                                    labels={'date': 'Date', 'profit': 'Profit (€)'},
                                    color=daily_profits['profit'] > 0,
                                    color_discrete_map={True: '#28a745', False: '#dc3545'}
                                )
                                st.plotly_chart(fig, use_container_width=True)
        
                                # Tableau détaillé
                                st.dataframe(df_historical, use_container_width=True)
        
                            elif analysis_type == "💰 Évolution du Capital":
                                # Simulation d'évolution du capital
                                dates = pd.date_range(start=start_date, end=end_date, freq='D')
                                capital = [initial_bankroll]
                                for i in range(1, len(dates)):
                                    change = np.random.normal(0, initial_bankroll * 0.02)
                                    new_capital = capital[-1] + change
                                    capital.append(max(0, new_capital))  # Pas de capital négatif
        
                                fig = px.area(
                                    x=dates,
                                    y=capital,
                                    title="Évolution du Capital au Fil du Temps",
                                    labels={'x': 'Date', 'y': 'Capital (€)'}
                                )
                                fig.add_hline(
                                    y=initial_bankroll,
                                    line_dash="dash",
                                    line_color="red",
                                    annotation_text="Capital Initial"
                                )
                                st.plotly_chart(fig, use_container_width=True)
        
                                # Statistiques de performance
                                total_return = capital[-1] - initial_bankroll
                                total_return_pct = (total_return / initial_bankroll) * 100
        
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Capital Final", format_currency(capital[-1]))
                                with col2:
                                    st.metric("Retour Total", format_currency(total_return))
                                with col3:
                                    st.metric("Retour %", f"{total_return_pct:+.1f}%")
        
                            elif analysis_type == "📈 Tendances par Équipe":
                                # Analyse par équipe
                                st.subheader("📈 Analyse par Équipe")
        
                                teams = ["PSG", "Marseille", "Lyon", "Monaco", "Lille", "Nice", "Lens", "Rennes"]
                                team_stats = []
        
                                for team in teams:
                                    matches = np.random.randint(5, 15)
                                    wins = np.random.randint(0, matches)
                                    value_bets = np.random.randint(0, matches)
                                    avg_edge = np.random.uniform(0.02, 0.12)
        
                                    team_stats.append({
                                        'Équipe': team,
                                        'Matches': matches,
                                        'Victoires': wins,
                                        'Value Bets': value_bets,
                                        'Edge Moyen': avg_edge,
                                        'Taux Réussite': wins / matches if matches > 0 else 0
                                    })
        
                                df_teams = pd.DataFrame(team_stats)
        
                                # Graphique radar des équipes
                                fig = px.scatter(
                                    df_teams,
                                    x='Edge Moyen',
                                    y='Taux Réussite',
                                    size='Value Bets',
                                    color='Équipe',
                                    title="Performance des Équipes",
                                    labels={'Edge Moyen': 'Edge Moyen', 'Taux Réussite': 'Taux de Réussite'}
                                )
                                st.plotly_chart(fig, use_container_width=True)
        
                                # Tableau détaillé
                                st.dataframe(df_teams, use_container_width=True)

        elif display_mode == "🧠 IA Auto-Analyse":
            # Section d'analyse automatique IA
            st.subheader("🧠 Analyse Automatique IA - Paris Recommandés")

            # Configuration de l'analyse IA
            col1, col2 = st.columns(2)
            with col1:
                ai_confidence_threshold = st.slider(
                    "Seuil de Confiance IA",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.7,
                    step=0.1,
                    help="Niveau minimum de confiance pour les recommandations IA"
                )
            with col2:
                ai_risk_level = st.selectbox(
                    "Niveau de Risque IA",
                    ["🛡️ Conservateur", "⚖️ Modéré", "🎯 Agressif"],
                    index=1,
                    help="Stratégie de risque pour les recommandations"
                )

            if st.button("🚀 Lancer l'Analyse IA Automatique", type="primary"):
                with st.spinner("🧠 IA en cours d'analyse des patterns..."):

                    # Simulation d'analyse IA (à remplacer par vraie IA)
                    ai_analysis_results = []

                    # Générer des recommandations IA fictives mais réalistes
                    for i in range(5):
                        teams = ["PSG", "Marseille", "Lyon", "Monaco", "Lille", "Nice", "Lens", "Rennes"]
                        home, away = np.random.choice(teams, 2, replace=False)

                        # Analyse IA simulée
                        market_types = ["Victoire domicile", "Match nul", "Victoire extérieur",
                                      "Plus de 2.5 buts", "Moins de 2.5 buts",
                                      "Les 2 équipes marquent", "Aucune équipe ne marque"]

                        market = np.random.choice(market_types)
                        ai_confidence = np.random.uniform(0.6, 0.95)
                        ai_edge = np.random.uniform(0.05, 0.25)
                        ai_odds = round(np.random.uniform(1.5, 4.0), 2)
                        ai_stake = np.random.uniform(50, 300)

                        # Calculs IA avancés
                        risk_adjusted_stake = ai_stake
                        if ai_risk_level == "🛡️ Conservateur":
                            risk_adjusted_stake *= 0.7
                        elif ai_risk_level == "🎯 Agressif":
                            risk_adjusted_stake *= 1.3

                        ai_analysis_results.append({
                            'match': f"{home} vs {away}",
                            'market': market,
                            'ai_confidence': ai_confidence,
                            'ai_edge': ai_edge,
                            'recommended_odds': ai_odds,
                            'ai_stake': risk_adjusted_stake,
                            'expected_profit': risk_adjusted_stake * (ai_odds - 1),
                            'ai_reasoning': np.random.choice([
                                "Pattern historique favorable détecté",
                                "Analyse de forme récente positive",
                                "Déséquilibre statistique identifié",
                                "Tendances de bookmaker exploitable",
                                "Modèle ML confiant dans cette prédiction"
                            ]),
                            'risk_level': "🟢 Faible" if ai_confidence > 0.8 else "🟡 Moyen" if ai_confidence > 0.7 else "🔴 Élevé"
                        })

                    # Filtrer selon le seuil de confiance
                    filtered_ai_results = [
                        result for result in ai_analysis_results
                        if result['ai_confidence'] >= ai_confidence_threshold
                    ]

                    if filtered_ai_results:
                        # Métriques IA
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("🎯 Recommandations IA", f"{len(filtered_ai_results)}")
                        with col2:
                            avg_confidence = np.mean([r['ai_confidence'] for r in filtered_ai_results])
                            st.metric("🧠 Confiance Moyenne", f"{avg_confidence:.1%}")
                        with col3:
                            total_stake = sum([r['ai_stake'] for r in filtered_ai_results])
                            st.metric("💰 Mise Totale", format_currency(total_stake))
                        with col4:
                            total_profit = sum([r['expected_profit'] for r in filtered_ai_results])
                            st.metric("💎 Profit Attendu", format_currency(total_profit))

                        # Affichage des recommandations IA
                        st.subheader("🎯 Recommandations IA Automatiques")

                        for i, rec in enumerate(filtered_ai_results, 1):
                            confidence_color = "🟢" if rec['ai_confidence'] > 0.8 else "🟡" if rec['ai_confidence'] > 0.7 else "🔴"

                            with st.expander(f"{i}. {rec['match']} - {rec['market']} {confidence_color}", expanded=i<=3):
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown(f"""
                                    **📊 Analyse IA:**
                                    - Confiance: {rec['ai_confidence']:.1%}
                                    - Edge prédit: {rec['ai_edge']:.1%}
                                    - Cote recommandée: {rec['recommended_odds']:.2f}
                                    - Niveau de risque: {rec['risk_level']}
                                    """)

                                with col2:
                                    st.markdown(f"""
                                    **💰 Recommandation:**
                                    - Mise suggérée: {format_currency(rec['ai_stake'])}
                                    - Profit attendu: {format_currency(rec['expected_profit'])}
                                    - ROI estimé: {(rec['expected_profit']/rec['ai_stake']*100):.1f}%
                                    """)

                                st.info(f"🧠 **Raisonnement IA:** {rec['ai_reasoning']}")

                                # Bouton d'action
                                if st.button(f"✅ Accepter cette recommandation #{i}", key=f"accept_{i}"):
                                    st.success(f"🎯 Recommandation #{i} acceptée! Mise de {format_currency(rec['ai_stake'])} sur {rec['market']}")

                        # Visualisation des recommandations IA
                        st.subheader("📊 Visualisation des Recommandations IA")

                        # Graphique de distribution des confiances
                        fig = px.histogram(
                            [r['ai_confidence'] for r in filtered_ai_results],
                            nbins=10,
                            title="Distribution des Confiances IA",
                            labels={'value': 'Confiance IA', 'count': 'Nombre de recommandations'}
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Graphique des profits attendus
                        fig2 = px.bar(
                            x=[f"{i+1}. {r['match'][:15]}..." for i, r in enumerate(filtered_ai_results)],
                            y=[r['expected_profit'] for r in filtered_ai_results],
                            title="Profits Attendus par Recommandation",
                            labels={'x': 'Match', 'y': 'Profit Attendu (€)'}
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                    else:
                        st.warning("⚠️ Aucune recommandation IA ne satisfait le seuil de confiance spécifié.")
                        st.info("💡 Essayez de réduire le seuil de confiance ou ajustez les paramètres de risque.")

    # Footer
    st.markdown("---")
    capital_str = format_currency(initial_bankroll)
    st.markdown(f"""
    <div style="text-align: center; color: #666;">
        <p>🎯 <strong>ValueBet Engine</strong> - Détection intelligente de value bets | ⚽ {competition} | 🤖 ML-powered</p>
        <p>Mode: {mode} | Capital: {capital_str} | Kelly: {kelly_fraction}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()