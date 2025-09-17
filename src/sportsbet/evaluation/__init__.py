"""It provides the tools to evaluate the performance of predictive models."""

from __future__ import annotations

from ._base import BaseBettor, load_bettor, save_bettor
from ._classifier import ClassifierBettor
from ._model_selection import BettorGridSearchCV, backtest, value_bet_backtest
from ._rules import OddsComparisonBettor

__all__: list[str] = [
    'BaseBettor',
    'BettorGridSearchCV',
    'ClassifierBettor',
    'OddsComparisonBettor',
    'backtest',
    'value_bet_backtest',
    'load_bettor',
    'save_bettor',
]
