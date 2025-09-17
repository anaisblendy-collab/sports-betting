"""Example of configuration file to get the odds types."""

from sportsbet.datasets import SoccerDataLoader

DATALOADER_CLASS = SoccerDataLoader
PARAM_GRID = {
    'league': ['Champions League'],
    'division': [1],
    'year': [2023, 2024, 2025],
}
