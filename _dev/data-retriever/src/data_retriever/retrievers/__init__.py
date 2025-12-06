"""Data retriever implementations."""

from data_retriever.retrievers.file_retriever import FileRetriever
from data_retriever.retrievers.api_retriever import APIRetriever

try:
    from data_retriever.retrievers.yahoo_finance_retriever import YahooFinanceRetriever
except ImportError:
    YahooFinanceRetriever = None

try:
    from data_retriever.retrievers.sec_retriever import SECRetriever
except ImportError:
    SECRetriever = None

try:
    from data_retriever.retrievers.database_retriever import DatabaseRetriever
except ImportError:
    DatabaseRetriever = None

__all__ = [
    "FileRetriever",
    "APIRetriever",
    "YahooFinanceRetriever",
    "SECRetriever",
    "DatabaseRetriever",
]

