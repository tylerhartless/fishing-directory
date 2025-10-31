"""
Data Adapters for ETL Pipeline

Import adapters from this module for easy access.
"""

from .texas_tpwd_adapter import TexasTPWDAdapter
from .california_dfw_adapter import CaliforniaDFWAdapter
from .florida_fwc_adapter import FloridaFWCAdapter
from .generic_csv_adapter import GenericCSVAdapter

__all__ = [
    'TexasTPWDAdapter',
    'CaliforniaDFWAdapter',
    'FloridaFWCAdapter',
    'GenericCSVAdapter'
]
