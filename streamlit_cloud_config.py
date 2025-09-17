#!/usr/bin/env python3
"""
Configuration pour Streamlit Cloud
Ce fichier configure automatiquement l'application pour Streamlit Cloud
"""

import os
import streamlit as st

# Configuration Streamlit Cloud
def configure_streamlit_cloud():
    """Configure l'application pour Streamlit Cloud"""

    # Variables d'environnement Streamlit Cloud
    st.set_page_config(
        page_title="🎯 ValueBet Engine - Football",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Configuration serveur pour le cloud
    if 'STREAMLIT_SERVER_HEADLESS' not in os.environ:
        os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

    if 'STREAMLIT_BROWSER_GATHER_USAGE_STATS' not in os.environ:
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

    # Configuration des secrets (dans Streamlit Cloud)
    # Les secrets sont accessibles via st.secrets
    try:
        # Récupération des clés API depuis les secrets Streamlit Cloud
        football_api_key = st.secrets.get("FOOTBALL_DATA_API_KEY")
        odds_api_key = st.secrets.get("ODDS_API_KEY")

        if football_api_key:
            os.environ['FOOTBALL_DATA_API_KEY'] = football_api_key
        if odds_api_key:
            os.environ['ODDS_API_KEY'] = odds_api_key

    except Exception as e:
        st.warning("⚠️ Secrets non configurés. Utilisez le mode démonstration.")
        st.info("💡 Pour configurer : Settings > Secrets dans Streamlit Cloud")

    return True

# Configuration spécifique pour la production
def setup_production_config():
    """Configuration optimisée pour la production"""

    # Cache Streamlit pour améliorer les performances
    @st.cache_data(ttl=3600)  # Cache 1 heure
    def load_expensive_data():
        # Ici vous pouvez mettre le chargement de données coûteuses
        pass

    # Configuration des sessions
    if 'user_session' not in st.session_state:
        st.session_state.user_session = {
            'authenticated': False,
            'user_id': None,
            'preferences': {}
        }

    return True

if __name__ == "__main__":
    configure_streamlit_cloud()
    setup_production_config()