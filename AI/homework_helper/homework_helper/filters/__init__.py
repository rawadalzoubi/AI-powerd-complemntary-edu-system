"""
Filters module for document processing and question answering.
This package provides various components for building RAG (Retrieval Augmented Generation) pipelines.
"""

# This file makes the 'filters' directory a Python package.

from .mysql_loader import MySQLLoader
from .pdf_parser import PDFParser
from .chunker import Chunker
from .embedder import create_embedder # , BaseEmbedder, OllamaEmbedder, HuggingFaceEmbedder # إذا أردت تصديرها أيضًا
from .vector_store import VectorStore # إضافة VectorStore
from .retriever import Retriever # إضافة Retriever
# تأكد من أن اسم create_llm_answer هو المستخدم في ملف llm_answer.py
from .llm_answer import create_llm_answer, BaseLLM, OllamaLLM, HuggingFaceLLM

__all__ = [
    # Loaders and Parsers
    'MySQLLoader',
    'PDFParser',
    # Text Processing
    'Chunker',
    # Embedding
    'create_embedder',
    # 'BaseEmbedder', # أضف إذا أردت تصديرها
    # 'OllamaEmbedder',
    # 'HuggingFaceEmbedder',
    # Vector Storage and Retrieval
    'VectorStore',
    'Retriever',
    # Language Model Answer Generation
    'create_llm_answer',
    'BaseLLM',
    'OllamaLLM',
    'HuggingFaceLLM',
]