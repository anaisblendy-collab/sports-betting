"""Example of configuration file for a classfier-based bettor."""

from sklearn.compose import make_column_transformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.multioutput import MultiOutputClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from sportsbet.datasets import SoccerDataLoader
from sportsbet.evaluation import ClassifierBettor

# Data extraction
DATALOADER_CLASS = SoccerDataLoader
PARAM_GRID={
    'league': ['France'],
    'year': [2023, 2024],
    'division': [1],
}
ODDS_TYPE = 'market_maximum'

# Betting process
BETTOR = ClassifierBettor(
    classifier=make_pipeline(
        make_column_transformer(
            (OneHotEncoder(handle_unknown='ignore'), ['league', 'home_team', 'away_team']), remainder='passthrough',
        ),
        SimpleImputer(),
        MultiOutputClassifier(
            LogisticRegression(solver='liblinear', random_state=7, class_weight='balanced', C=50),
        ),
    ),
    init_cash=10000.0,
    stake=50.0,
)
CV = TimeSeriesSplit(3)
