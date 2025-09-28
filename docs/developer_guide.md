# AI Nurse Florence: Developer Guide

This guide provides technical documentation for developers working with the AI Nurse Florence API and codebase.

## Architecture Overview

AI Nurse Florence is a FastAPI-based application that provides healthcare information through various live medical data services:

```
┌───────────────┐     ┌─────────────┐     ┌─────────────────┐
│  API Gateway  │────▶│  FastAPI    │────▶│  Core Services  │
└───────────────┘     └─────────────┘     └─────────────────┘
				    │                      │
				    ▼                      ▼
			    ┌─────────────┐     ┌─────────────────┐
			    │  Middleware │     │ Live Medical    │
			    └─────────────┘     │ APIs Integration│
				    │             └─────────────────┘
				    ▼                      │
			    ┌─────────────┐              ▼
			    │   Caching   │     ┌─────────────────┐
			    └─────────────┘     │ LLM Integration │
							└─────────────────┘
```

### Key Components

- **API Routers**: Endpoint definitions in the `/routers` directory
- **Services**: Core business logic in the `/services` directory with live API integration
- **Live Medical APIs**: Real-time data from `live_mydisease.py`, `live_pubmed.py`, `live_clinicaltrials.py`
- **Middleware**: Request processing, rate limiting, and logging in `/utils/middleware.py`
- **Exception Handling**: Custom exceptions with external service handling in `/utils/exceptions.py`
- **Caching**: Redis-based caching with in-memory fallback in `/utils/cache.py`
- **Monitoring**: Prometheus metrics and health checks in `/utils/metrics.py`

## Live Medical Data Integration

### External APIs

#### MyDisease.info
- **Purpose**: Comprehensive disease information and cross-references
- **File**: `live_mydisease.py`
- **Function**: `lookup(term: str)`
- **Rate Limits**: No authentication required, reasonable use expected
- **Data Fields**: Disease names, definitions, references, cross-database IDs

#### PubMed/NCBI eUtils
- **Purpose**: Medical literature search from 35+ million citations
- **File**: `live_pubmed.py`  
- **Functions**: `search(query, max_results)`, `get_total_count(query)`
- **Rate Limits**: 3/sec (10/sec with API key)
- **API Key**: Set `NCBI_API_KEY` for enhanced rate limits

#### ClinicalTrials.gov
- **Purpose**: Current and completed clinical studies
- **File**: `live_clinicaltrials.py`
- **Function**: `search(condition, status, max_results)`
- **API Version**: v2 (current stable)
- **Rate Limits**: No authentication required

## Getting Started

### Prerequisites

- Python 3.9+
- Redis (for production deployments - optional for development)
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key (required for AI features)
- NCBI API key (optional but recommended for enhanced PubMed rate limits)

## ... (content continues from archived developer_guide.bak)
