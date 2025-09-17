"""Example of configuration file to get the fixtures data."""

from sportsbet.datasets import SoccerDataLoader

DATALOADER_CLASS = SoccerDataLoader
PARAM_GRID = {
    'league': ['Champions League'],
    'year': [2023, 2024, 2025],  # Mets toutes les années souhaitées
}
ODDS_TYPE = 'market_maximum'
