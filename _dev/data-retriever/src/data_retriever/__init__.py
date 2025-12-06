"""
Data Retrieval Abstraction Layer

Provides a unified interface for retrieving data from various sources:
- Yahoo Finance (browser automation or API)
- SEC EDGAR database
- Generic REST APIs
- SQL databases
- Local file system
"""

from data_retriever.base import DataRetriever, RetrievalResult
from data_retriever.schema import Schema, Field, FieldType
from data_retriever.cache import DataCache
from data_retriever.metrics import MetricsCollector

# Retrievers
from data_retriever.retrievers.file_retriever import FileRetriever
from data_retriever.retrievers.api_retriever import APIRetriever

try:
    from data_retriever.retrievers.yahoo_finance_retriever import YahooFinanceRetriever
except ImportError:
    # Browser automation dependencies optional
    YahooFinanceRetriever = None

try:
    from data_retriever.retrievers.sec_retriever import SECRetriever
except ImportError:
    # SEC dependencies optional
    SECRetriever = None

try:
    from data_retriever.retrievers.database_retriever import DatabaseRetriever
except ImportError:
    # Database dependencies optional
    DatabaseRetriever = None

__all__ = [
    "DataRetriever",
    "RetrievalResult",
    "Schema",
    "Field",
    "FieldType",
    "DataCache",
    "MetricsCollector",
    "FileRetriever",
    "APIRetriever",
    "YahooFinanceRetriever",
    "SECRetriever",
    "DatabaseRetriever",
]

__version__ = "0.1.0"

