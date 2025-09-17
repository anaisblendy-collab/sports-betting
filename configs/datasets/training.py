"""Example of configuration file to get the training data."""

from sportsbet.datasets import SoccerDataLoader

DATALOADER_CLASS = SoccerDataLoader
PARAM_GRID = {
    'league': ['Champions League'],
    'division': [1],
    'year': [2023, 2024, 2025],
}
DROP_NA_THRES = 0.8
ODDS_TYPE = 'market_average'
