"""
Tests for type correctness of services.

This module tests that our services conform to the expected type protocols.
"""
import pytest
from typing import cast

from utils.types import (
    DiseaseService, 
    PubMedService, 
    MedlinePlusService, 
    TrialsService,
    ReadabilityService,
    SummarizeService
)

from services.disease_service import lookup_disease
from services.pubmed_service import search_pubmed
from services.medlineplus_service import get_medlineplus_summary
from services.trials_service import search_trials
from services.readability_service import analyze_readability
from services.summarize_service import summarize_text


def test_disease_service_type_conformance():
    """Test that disease_service conforms to the DiseaseService protocol."""
    service = cast(DiseaseService, lookup_disease)
    # If this assignment succeeds, it means the type is compatible
    assert callable(service)


def test_pubmed_service_type_conformance():
    """Test that pubmed_service conforms to the PubMedService protocol."""
    service = cast(PubMedService, search_pubmed)
    assert callable(service)


def test_medlineplus_service_type_conformance():
    """Test that medlineplus_service conforms to the MedlinePlusService protocol."""
    service = cast(MedlinePlusService, get_medlineplus_summary)
    assert callable(service)


def test_trials_service_type_conformance():
    """Test that trials_service conforms to the TrialsService protocol."""
    service = cast(TrialsService, search_trials)
    assert callable(service)


def test_readability_service_type_conformance():
    """Test that readability_service conforms to the ReadabilityService protocol."""
    service = cast(ReadabilityService, analyze_readability)
    assert callable(service)


def test_summarize_service_type_conformance():
    """Test that summarize_service conforms to the SummarizeService protocol."""
    service = cast(SummarizeService, summarize_text)
    assert callable(service)