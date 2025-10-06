# Future Features & Enhancements

**Purpose**: Centralized tracking of planned features and improvements across AI Nurse Florence.

**Last Updated**: 2025-10-06
**Status**: Living document - updated as features are identified or implemented

---

## How to Use This Document

- **Adding Features**: Append new features to the appropriate category
- **Implementing Features**: Move implemented items to a dated "Completed" section at bottom
- **Prioritization**: Use 🔴 High, 🟡 Medium, 🟢 Low, ⭕ Deferred markers
- **Cross-Reference**: Link to related files, docs, or issues

---

## Enhanced Literature Service

### Performance (1 remaining)
- 🟡 **Request batching for multiple PMIDs** - Reduce API calls by batching PMID fetches
  - File: [src/services/enhanced_literature_service.py](../src/services/enhanced_literature_service.py)
  - Estimated effort: 2-3 hours
  - Impact: Further reduce PubMed API calls by 30-40%

### Features
- 🔴 **Full XML parsing** - Replace mock results with actual PubMed XML parsing
  - File: [src/services/enhanced_literature_service.py:615](../src/services/enhanced_literature_service.py#L615)
  - Currently: `_parse_pubmed_xml()` returns mock results
  - Effort: 4-6 hours
  - Dependencies: xml.etree.ElementTree integration

- 🟢 **Citation network analysis** - Co-citation patterns for research connections
  - Effort: 8-12 hours
  - Dependencies: Graph database or NetworkX library
  - Use case: Research-focused queries

- 🟢 **Author expertise scoring** - Rank authors by publication history
  - Effort: 6-8 hours
  - Dependencies: PubMed author API integration
  - Use case: Finding subject matter experts

- 🟢 **Multi-language literature support** - Not just English
  - Effort: 10-15 hours
  - Dependencies: Translation API, language detection
  - Use case: International medical literature

- 🟢 **Export formats** - BibTeX, RIS, EndNote
  - Effort: 3-5 hours
  - Dependencies: Format libraries
  - Use case: Academic research workflows

### Quality
- 🔴 **Retry logic with exponential backoff** - Handle transient API failures
  - File: [src/services/enhanced_literature_service.py](../src/services/enhanced_literature_service.py)
  - Effort: 2-3 hours
  - Pattern: Start 1s, max 32s, 3-5 retries

- 🔴 **Request rate limiting** - PubMed: 3 req/sec limit
  - Effort: 2-3 hours
  - Implementation: Token bucket or leaky bucket algorithm
  - Critical: Prevents API key blocking

- 🟡 **Comprehensive error tracking/metrics** - Monitor service health
  - Effort: 4-6 hours
  - Dependencies: Prometheus, Grafana, or similar
  - Metrics: Error rates, latency, cache hit rates

- 🟢 **Query spell-checking and suggestions** - Help users with typos
  - Effort: 6-8 hours
  - Dependencies: Medical spell-check library
  - Enhancement: Better search accuracy

- 🟢 **MeSH term mapping** - Medical Subject Headings integration
  - Effort: 8-10 hours
  - Dependencies: MeSH database, UMLS integration
  - Impact: Significantly better search accuracy

### Testing
- 🔴 **Unit tests for query processing logic** - Test query enhancement
  - File: Tests for [src/services/enhanced_literature_service.py:381](../src/services/enhanced_literature_service.py#L381)
  - Effort: 3-4 hours
  - Coverage target: 80%+

- 🔴 **Mock PubMed API responses** - Integration tests without API dependency
  - Effort: 4-5 hours
  - Tool: pytest fixtures, responses library
  - Benefits: Faster CI/CD, offline development

- 🟡 **Cache hit/miss scenario tests** - Verify caching behavior
  - Effort: 2-3 hours
  - Test scenarios: Cold cache, warm cache, TTL expiry

- 🟡 **Relevance ranking algorithm accuracy tests** - Validate scoring
  - Effort: 4-6 hours
  - Method: Golden dataset of ranked results

- 🟢 **Performance benchmarks** - Target: <100ms cached, <3s uncached
  - Effort: 2-3 hours
  - Tool: pytest-benchmark
  - CI integration: Regression detection

### Documentation
- 🟡 **Sequence diagrams for complex workflows** - Visual documentation
  - Effort: 3-4 hours
  - Tool: Mermaid.js in markdown
  - Workflows: Search flow, cache flow, error flow

- 🟡 **PubMed API rate limits and best practices** - Developer guide
  - Effort: 1-2 hours
  - File: New doc or append to [docs/MEDICAL_DATA_SOURCES.md](MEDICAL_DATA_SOURCES.md)

- 🟢 **Examples for each specialty type** - Usage documentation
  - Effort: 2-3 hours
  - Specialties: Cardiology, Oncology, Neurology, Pediatrics, Emergency, Nursing

- 🟢 **Evidence level scoring methodology** - Transparent algorithm docs
  - Effort: 2-3 hours
  - Document: Oxford CEBM levels, boost calculations

- 🟢 **Runbook for PubMed API outages** - Operational guide
  - Effort: 1-2 hours
  - Content: Detection, mitigation, recovery steps

### Monitoring/Observability
- 🟡 **Prometheus metrics for cache hit rates** - Performance monitoring
  - Effort: 3-4 hours
  - Dependencies: prometheus_client library
  - Metrics: Cache hits, misses, TTL distribution

- 🟡 **Log slow queries** - Queries >5 seconds
  - Effort: 1-2 hours
  - Implementation: Add timing decorator
  - Use case: Performance optimization

- 🟢 **Track most common search terms** - Usage analytics
  - Effort: 2-3 hours
  - Privacy: Anonymized, aggregated data only
  - Use case: Cache warming, UX improvements

- 🟢 **Monitor API error rates** - Service health
  - Effort: 2-3 hours
  - Alert thresholds: >5% error rate

- 🟢 **Distributed tracing for async operations** - Debug complex flows
  - Effort: 6-8 hours
  - Dependencies: OpenTelemetry, Jaeger
  - Use case: Performance debugging

### Security
- 🔴 **Sanitize user queries** - Prevent injection attacks
  - File: [src/services/enhanced_literature_service.py:381](../src/services/enhanced_literature_service.py#L381)
  - Effort: 2-3 hours
  - Pattern: Whitelist allowed characters, escape special chars

- 🔴 **Rate limiting per user/session** - Prevent abuse
  - Effort: 3-4 hours
  - Implementation: Token bucket per user ID
  - Limits: 100 queries/hour per user

- 🟡 **Request signing for sensitive operations** - Authentication
  - Effort: 4-5 hours
  - Dependencies: JWT or HMAC signing
  - Use case: API security

- 🟡 **Audit logging for literature searches** - Compliance
  - Effort: 2-3 hours
  - Log: User ID, query, timestamp, results count
  - Retention: 90 days

- 🟡 **Validate XML responses before parsing** - Security hardening
  - Effort: 2-3 hours
  - Protection: XML bombs, XXE attacks
  - Library: defusedxml

---

## High-Priority TODOs (From TODO_AUDIT_2025-10-06.md)

### 🔴 Critical
- **Risk Assessment Service Integration** - `src/routers/health.py:359`
  - Effort: 4-6 hours
  - Status: Placeholder exists, needs implementation
  - Impact: Core health assessment feature

- **Rate Limiting Configuration** - `src/middleware/rate_limit.py:60`
  - Effort: 2-3 hours
  - Status: Basic implementation exists, needs production config
  - Impact: API protection, scalability

### 🟡 Medium Priority
- **FDA Drug Database API Integration** - `scripts/build_drug_database.py:22`
  - Effort: 3-4 hours
  - Status: Offline database exists, API integration would be faster
  - Impact: Faster startup, fresher data

- **PDF Merge Optimization** - `src/utils/pdf_generator.py:428`
  - Effort: 2-3 hours
  - Current: Slow for large documents
  - Impact: Better UX for multi-page reports

- **HTML Preview Before PDF** - `src/utils/pdf_generator.py:509`
  - Effort: 3-4 hours
  - Feature: Preview before generating PDF
  - Impact: Better UX, fewer regenerations

---

## Deferred Features (Low Priority / Future Versions)

### ChatGPT Store Integration (18 TODOs - Deferred)
- All ChatGPT Store features deferred until market validation
- Files affected: `src/routers/chatgpt_store.py`, `src/utils/swagger_enhancements.py`
- Estimated total effort: 40-60 hours
- Decision rationale: Focus on core medical features first

### Server-Side Rendering (SSR) Features
- Deferred until performance profiling shows need
- Files: Various frontend components
- Estimated effort: 20-30 hours

### Missing Router Implementations
- **conversation.py** - Chat/conversation history
- **users.py** - User management (beyond basic auth)
- **med_check.py** - Medication checking workflows
- **educational.py** - Educational content management
- Status: Documented in [src/routers/__init__.py:167](../src/routers/__init__.py#L167)
- Effort: 6-10 hours each
- Priority: As user demand emerges

---

## Completed Features

### 2025-10-06
- ✅ **Adaptive cache TTL based on query urgency** - Enhanced Literature Service
  - Commit: `4829c30`
  - Implementation: CACHE_TTL_BY_PRIORITY (30min/1hr/3hrs)

- ✅ **Connection pooling with keep-alive headers** - Enhanced Literature Service
  - Commit: `4829c30`
  - Implementation: httpx.Limits with 10 keepalive connections

- ✅ **Circuit breaker pattern for PubMed API failures** - Enhanced Literature Service
  - Commit: `4829c30`
  - Implementation: 5-failure threshold, 60s timeout

- ✅ **Cache parsed XML to avoid re-parsing** - Enhanced Literature Service
  - Commit: `4829c30`
  - Implementation: 24-hour XML cache with PMID-based keys

---

## Feature Request Process

1. **Identify**: Add feature to appropriate category above
2. **Prioritize**: Assign priority marker (🔴/🟡/🟢/⭕)
3. **Estimate**: Add effort estimate and dependencies
4. **Link**: Reference source files and line numbers
5. **Implement**: When ready, create implementation plan
6. **Complete**: Move to "Completed Features" section with commit hash

---

## Notes

- This document replaces inline TODO comments for feature tracking
- All new features should be added here first before implementation
- Use [docs/TODO_AUDIT_2025-10-06.md](TODO_AUDIT_2025-10-06.md) for technical debt tracking
- Refer to [docs/DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for release planning
