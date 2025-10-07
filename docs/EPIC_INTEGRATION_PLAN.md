# Epic FHIR Integration Plan
## AI Nurse Florence - EHR Integration Architecture

**Status**: Planning Phase
**Last Updated**: 2025-10-07
**Target Completion**: TBD based on Epic credentials availability

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current Architecture Analysis](#current-architecture-analysis)
3. [Epic Integration Requirements](#epic-integration-requirements)
4. [Implementation Phases](#implementation-phases)
5. [Technical Architecture](#technical-architecture)
6. [Security & Compliance](#security--compliance)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Plan](#deployment-plan)

---

## Executive Summary

### Vision
Transform AI Nurse Florence from standalone mode to full Epic EHR integration, enabling:
- **Real-time patient data retrieval** via FHIR R4 APIs
- **Automated form pre-population** from Epic chart data
- **Bidirectional documentation** (write discharge notes back to Epic)
- **MRN barcode scanning** for instant patient lookup
- **Reduced data entry burden** for nursing staff

### Business Value
- **Time Savings**: Eliminate duplicate data entry (~5-10 minutes per patient)
- **Accuracy**: Reduce transcription errors with direct EHR integration
- **Workflow Integration**: Seamless nurse experience within existing Epic environment
- **Compliance**: Maintain HIPAA compliance with session-only data storage

### Current State
✅ **Infrastructure Ready**: Well-architected placeholder code exists
✅ **FHIR Models Defined**: Patient, Condition, MedicationRequest schemas complete
✅ **Configuration System**: IntegrationMode enum and settings framework in place
⏸️ **Awaiting Epic Credentials**: Need App Orchard registration and sandbox access

---

## Current Architecture Analysis

### Existing Foundation (Already Built)

#### 1. **EHR Integration Service** (`services/ehr_integration_service.py`)
- ✅ Complete service structure with stub implementations
- ✅ Methods for all major FHIR operations:
  - `fetch_patient_by_mrn()` - Patient lookup
  - `fetch_active_medications()` - MedicationRequest retrieval
  - `fetch_active_conditions()` - Diagnosis/Condition retrieval
  - `fetch_encounter_context()` - Visit/encounter details
  - `write_discharge_note()` - DocumentReference creation
  - `scan_patient_wristband()` - Barcode scanning
- ✅ Integration mode switching (standalone vs epic_integrated)
- ✅ Detailed Epic FHIR examples in comments

#### 2. **FHIR Data Models** (`src/models/patient_document_schemas.py`)
- ✅ `FHIRPatientIdentifier` - Patient demographics with MRN
- ✅ `FHIRCondition` - Diagnoses with ICD-10 and SNOMED codes
- ✅ `FHIRMedicationRequest` - Medications with RxNorm codes
- ✅ `FHIREncounter` - Visit context and location
- ✅ Proper field naming aligned with HL7 FHIR R4 standard

#### 3. **Configuration System** (`src/config.py`)
```python
# Integration mode control
integration_mode: IntegrationMode = IntegrationMode.STANDALONE

# Epic FHIR settings (awaiting credentials)
epic_fhir_base_url: Optional[str] = None
epic_client_id: Optional[str] = None
epic_client_secret: Optional[str] = None
epic_oauth_enabled: bool = False
epic_sandbox_mode: bool = False

# Feature flags
enable_mrn_scanning: bool = False
enable_epic_write_back: bool = False
```

#### 4. **What's Missing** (Implementation Needed)
- ❌ OAuth 2.0 authentication flow
- ❌ HTTP client for Epic FHIR API calls
- ❌ FHIR resource parsing logic
- ❌ Error handling and retry mechanisms
- ❌ Token management and refresh
- ❌ Frontend UI for Epic integration features
- ❌ MRN barcode scanning implementation

---

## Epic Integration Requirements

### Epic App Orchard Registration

#### Step 1: Create Developer Account
- **URL**: https://fhir.epic.com/
- **Requirements**:
  - Valid email address
  - Organization information
  - App description and purpose
- **Timeline**: Immediate (free account)

#### Step 2: Register Application
- **Portal**: https://fhir.epic.com/Developer/Apps
- **Required Information**:
  - App name: "AI Nurse Florence"
  - App type: Backend Systems (OAuth 2.0 client credentials)
  - Redirect URIs: Production and development URLs
  - FHIR scopes needed (see below)
  - Privacy policy URL
  - Terms of service URL
  - Support contact information

#### Step 3: Request FHIR Scopes
**Read Scopes** (Patient data retrieval):
- `Patient.Read` - Demographics and MRN
- `Condition.Read` - Active diagnoses
- `MedicationRequest.Read` - Active medications
- `Encounter.Read` - Visit context
- `Observation.Read` - Vital signs (optional)

**Write Scopes** (Documentation):
- `DocumentReference.Write` - Discharge notes/instructions

**Special Scopes**:
- `launch/patient` - Patient context launch
- `openid fhirUser` - User identity

#### Step 4: Sandbox Access
- **Sandbox URL**: `https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/`
- **Test Patients**: Epic provides sample MRNs for testing
- **OAuth Endpoint**: Public sandbox available for development
- **Timeline**: Immediate access after app registration

#### Step 5: Production Credentials
- **Requirements**:
  - Complete sandbox testing
  - Security review
  - Privacy policy compliance
  - App Orchard submission
- **Timeline**: 2-3 business days for review
- **Hospital Deployment**: Each Epic customer must approve app installation

### Technical Requirements

#### FHIR R4 Compliance
- **Standard**: HL7 FHIR Release 4 (R4)
- **Format**: JSON (XML supported but not recommended)
- **Authentication**: OAuth 2.0 (Backend Services or SMART on FHIR)
- **Transport**: HTTPS only (TLS 1.2+)

#### OAuth 2.0 Flow
**Backend Services (Server-to-Server)**:
1. Client Credentials Grant
2. JWT assertion for authentication
3. Access token with 1-hour expiration
4. No refresh token (re-authenticate as needed)

**Alternative: SMART on FHIR Launch**:
1. User authorization flow
2. Patient context from launch parameters
3. Refresh token support for persistent access

#### Network Requirements
- **Outbound HTTPS**: Port 443 to Epic FHIR endpoints
- **IP Whitelisting**: May be required by hospital IT
- **Rate Limiting**: Epic throttles API calls (typical: 100 req/min)
- **Timeout Handling**: 30-second timeout recommended

---

## Implementation Phases

### Phase 1: Foundation & Mock Integration (No Epic Credentials Needed)
**Timeline**: 1-2 weeks
**Goal**: Build core infrastructure that can be tested without Epic access

#### Tasks:
1. **Create Mock FHIR Server** 📋
   - Build local FHIR server with sample responses
   - Implement Patient, Condition, MedicationRequest endpoints
   - Use realistic Epic FHIR response formats
   - Support local development and testing

2. **Build HTTP Client Library** 📋
   - Create `EpicFHIRClient` class with httpx
   - Implement OAuth 2.0 client credentials flow (placeholder)
   - Add request/response logging
   - Error handling with exponential backoff
   - Rate limiting support

3. **Implement FHIR Resource Parsers** 📋
   - `_parse_patient_resource()` - Extract demographics from Patient resource
   - `_parse_condition_resource()` - Parse Condition to FHIRCondition
   - `_parse_medication_resource()` - Parse MedicationRequest
   - `_parse_encounter_resource()` - Extract encounter details
   - Handle missing fields gracefully

4. **Write Comprehensive Tests** 📋
   - Unit tests for each parser method
   - Integration tests with mock FHIR server
   - Test error handling and edge cases
   - Validate FHIR R4 compliance

5. **Create Integration Dashboard** 📋
   - Admin page showing integration status
   - Display: connection state, last sync, error logs
   - Configuration form for Epic settings
   - Test connection button

#### Deliverables:
- ✅ Fully functional mock integration
- ✅ Complete test suite (90%+ coverage)
- ✅ Documentation for testing procedures
- ✅ Integration status UI

---

### Phase 2: Epic Sandbox Integration (Requires Sandbox Credentials)
**Timeline**: 1-2 weeks after sandbox access
**Goal**: Connect to Epic sandbox and validate real FHIR interactions

#### Prerequisites:
- Epic App Orchard developer account created
- Sandbox client credentials obtained
- Test MRNs from Epic sandbox documentation

#### Tasks:
1. **Configure Sandbox Connection** 📋
   ```bash
   # .env configuration
   INTEGRATION_MODE=epic_integrated
   EPIC_SANDBOX_MODE=true
   EPIC_CLIENT_ID=<sandbox_client_id>
   EPIC_CLIENT_SECRET=<sandbox_secret>
   EPIC_FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
   ```

2. **Implement OAuth 2.0 Authentication** 📋
   - JWT assertion creation and signing
   - Token endpoint integration
   - Token caching and expiration handling
   - Automatic token refresh logic

3. **Test Patient Lookup** 📋
   - Use sandbox test MRNs
   - Validate Patient.Read API
   - Parse and display patient demographics
   - Handle "patient not found" errors

4. **Test Condition/Medication Retrieval** 📋
   - Fetch active diagnoses for test patients
   - Retrieve current medications
   - Validate ICD-10, SNOMED, RxNorm code mappings
   - Test pagination for patients with many conditions

5. **Test DocumentReference Creation** 📋
   - Generate sample discharge note
   - POST to DocumentReference endpoint
   - Validate write-back success
   - Test error handling (permissions, invalid encounter)

#### Deliverables:
- ✅ Working sandbox integration
- ✅ Documented test results with screenshots
- ✅ Integration health monitoring
- ✅ Error handling for common failure modes

---

### Phase 3: Production Readiness (Requires Production Credentials)
**Timeline**: 2-3 weeks
**Goal**: Production-ready Epic integration with security hardening

#### Prerequisites:
- Sandbox testing complete
- Epic App Orchard submission approved
- Production client credentials from customer hospital

#### Tasks:
1. **Security Hardening** 📋
   - Implement secrets management (AWS Secrets Manager / HashiCorp Vault)
   - Add request signing for data integrity
   - Enable audit logging for all Epic API calls
   - Implement role-based access control

2. **Production OAuth Flow** 📋
   - Configure production token endpoint
   - Hospital-specific OAuth customizations
   - Multi-tenant support (different hospitals)

3. **Performance Optimization** 📋
   - Implement response caching (5-minute TTL)
   - Batch API requests where possible
   - Connection pooling for Epic API client
   - Async processing for write operations

4. **Error Recovery** 📋
   - Retry logic with exponential backoff
   - Circuit breaker for Epic API failures
   - Graceful degradation to standalone mode
   - Error notification system for admins

5. **Monitoring & Alerting** 📋
   - Prometheus metrics for Epic API calls
   - Grafana dashboards for integration health
   - Alerts for authentication failures
   - Performance tracking (response times, error rates)

#### Deliverables:
- ✅ Production-ready Epic integration
- ✅ Security audit passed
- ✅ Performance benchmarks documented
- ✅ Runbook for ops team

---

### Phase 4: Enhanced Features
**Timeline**: Ongoing
**Goal**: Advanced integration features

#### Features:
1. **MRN Barcode Scanning** 📋
   - Camera-based barcode reader
   - Barcode format parsing (Code 128, QR)
   - Auto-lookup patient on scan
   - Mobile device support

2. **Real-Time Sync** 📋
   - WebSocket connection to Epic (if supported)
   - Poll for updates on active encounter
   - Notify nurse of medication changes
   - Alert on new diagnoses

3. **Encounter Context** 📋
   - Detect current encounter from Epic session
   - Auto-select patient if already in chart
   - Show visit location (ED, ICU, etc.)
   - Display attending provider

4. **Advanced Write-Back** 📋
   - Write care plan to Epic Problem List
   - Create medication instructions as MedicationRequest
   - Update patient education completion flags
   - Link generated PDFs to encounter

---

## Technical Architecture

### System Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Nurse Florence                         │
│                                                                   │
│  ┌───────────────────┐          ┌──────────────────────┐        │
│  │   Frontend UI     │          │   Backend API        │        │
│  │                   │          │                      │        │
│  │  - MRN Input      │◄────────►│  - Session Mgmt      │        │
│  │  - Pre-filled     │          │  - Business Logic    │        │
│  │    Forms          │          │  - Document Gen      │        │
│  └───────────────────┘          └──────────┬───────────┘        │
│                                             │                     │
│                                             │                     │
│                                  ┌──────────▼───────────┐        │
│                                  │ EHR Integration      │        │
│                                  │ Service Layer        │        │
│                                  │                      │        │
│                                  │ - EpicFHIRClient     │        │
│                                  │ - OAuth Manager      │        │
│                                  │ - FHIR Parsers       │        │
│                                  └──────────┬───────────┘        │
│                                             │                     │
└─────────────────────────────────────────────┼─────────────────────┘
                                              │
                                              │ HTTPS + OAuth 2.0
                                              │
                          ┌───────────────────▼───────────────────┐
                          │         Epic FHIR R4 API              │
                          │                                       │
                          │  Patient  │ Condition │ MedicationReq │
                          │  Encounter│  Observation│ DocReference│
                          └───────────────────────────────────────┘
                                             │
                                             │
                                   ┌─────────▼──────────┐
                                   │  Hospital Epic EHR │
                                   │  (Customer System) │
                                   └────────────────────┘
```

### Component Details

#### EpicFHIRClient (To Be Built)
```python
class EpicFHIRClient:
    """HTTP client for Epic FHIR R4 API with OAuth 2.0"""

    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url
        self.oauth_manager = OAuthManager(client_id, client_secret)
        self.session = httpx.AsyncClient(timeout=30.0)

    async def get(self, endpoint: str, params: dict = None) -> dict:
        """Make authenticated GET request to Epic FHIR endpoint"""
        token = await self.oauth_manager.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/fhir+json"
        }
        response = await self.session.get(
            f"{self.base_url}{endpoint}",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def post(self, endpoint: str, data: dict) -> dict:
        """Make authenticated POST request to Epic FHIR endpoint"""
        token = await self.oauth_manager.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/fhir+json"
        }
        response = await self.session.post(
            f"{self.base_url}{endpoint}",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
```

#### OAuth Manager (To Be Built)
```python
class OAuthManager:
    """Manage OAuth 2.0 tokens for Epic FHIR API"""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = None

    async def get_access_token(self) -> str:
        """Get valid access token (cached or refreshed)"""
        if self.access_token and self.token_expiry > datetime.now():
            return self.access_token

        # Request new token using client credentials
        return await self._request_token()

    async def _request_token(self) -> str:
        """Request new access token from Epic OAuth endpoint"""
        # JWT assertion creation
        # POST to token endpoint
        # Cache token with expiry
        pass
```

---

## Security & Compliance

### HIPAA Compliance Measures

1. **No PHI Persistence**
   - Session-only patient data storage
   - Redis for session management (encrypted at rest)
   - Data cleared on logout or timeout (15 minutes)
   - No database storage of patient information

2. **Encryption**
   - TLS 1.2+ for all Epic API communication
   - Secrets encrypted in environment variables
   - Redis connection encrypted with SSL
   - Generated documents encrypted in transit

3. **Access Control**
   - User authentication required before Epic integration
   - Role-based access (only authenticated nurses)
   - Audit logging of all Epic API calls
   - IP whitelisting for production environment

4. **Data Minimization**
   - Only fetch required FHIR resources
   - No bulk data exports
   - Session scoped to single patient
   - Automatic data expiration

### Security Best Practices

1. **OAuth Token Security**
   - Store client secrets in AWS Secrets Manager
   - Never log access tokens
   - Rotate credentials quarterly
   - Revoke tokens on security incidents

2. **Error Handling**
   - Never expose Epic credentials in error messages
   - Log errors without PHI
   - Rate limit authentication attempts
   - Circuit breaker for repeated failures

3. **Network Security**
   - Whitelist Epic IP ranges only
   - Use VPC for production deployment
   - Enable AWS WAF for DDoS protection
   - Monitor for unusual API call patterns

---

## Testing Strategy

### Phase 1: Mock Testing (No Credentials)
```python
# test_epic_integration.py
import pytest
from services.mock_fhir_server import MockFHIRServer
from services.ehr_integration_service import EHRIntegrationService

@pytest.fixture
def mock_epic():
    """Start mock FHIR server for testing"""
    server = MockFHIRServer()
    server.start()
    yield server
    server.stop()

@pytest.mark.asyncio
async def test_fetch_patient_by_mrn(mock_epic):
    """Test patient lookup with mock Epic server"""
    ehr_service = EHRIntegrationService()
    patient = await ehr_service.fetch_patient_by_mrn("12345678")

    assert patient is not None
    assert patient.patient_mrn == "12345678"
    assert patient.patient_family_name == "Smith"
    assert patient.patient_given_name == "John"

@pytest.mark.asyncio
async def test_fetch_active_conditions(mock_epic):
    """Test condition retrieval with mock Epic server"""
    ehr_service = EHRIntegrationService()
    conditions = await ehr_service.fetch_active_conditions("eXYZ123")

    assert len(conditions) > 0
    assert any(c.condition_code_icd10 == "E11.9" for c in conditions)
    assert all(c.condition_clinical_status == "active" for c in conditions)
```

### Phase 2: Sandbox Testing (Sandbox Credentials)
```python
@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_sandbox_patient_lookup():
    """Test against real Epic sandbox"""
    # Use Epic-provided test MRN
    test_mrn = "EPIC.E4190"  # Epic sandbox test patient

    ehr_service = EHRIntegrationService()
    patient = await ehr_service.fetch_patient_by_mrn(test_mrn)

    assert patient is not None
    assert patient.patient_mrn == test_mrn
    # Validate against known sandbox patient data
```

### Phase 3: Integration Testing
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test complete workflow from MRN to document generation"""
    # 1. Lookup patient
    patient = await ehr_service.fetch_patient_by_mrn("12345678")

    # 2. Fetch conditions and medications
    conditions = await ehr_service.fetch_active_conditions(patient.patient_fhir_id)
    medications = await ehr_service.fetch_active_medications(patient.patient_fhir_id)

    # 3. Generate discharge instructions
    document = await generate_discharge_instructions(
        patient=patient,
        conditions=conditions,
        medications=medications
    )

    # 4. Write back to Epic
    success = await ehr_service.write_discharge_note(
        encounter_fhir_id="eXYZ999",
        document_content=document,
        document_format="pdf"
    )

    assert success is True
```

---

## Deployment Plan

### Environment Configuration

#### Development
```bash
# .env.development
INTEGRATION_MODE=standalone  # No Epic connection for local dev
EPIC_SANDBOX_MODE=false
ENABLE_EPIC_WRITE_BACK=false
```

#### Staging (Sandbox)
```bash
# .env.staging
INTEGRATION_MODE=epic_integrated
EPIC_SANDBOX_MODE=true
EPIC_FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
EPIC_CLIENT_ID=${SANDBOX_CLIENT_ID}  # From App Orchard
EPIC_CLIENT_SECRET=${SANDBOX_CLIENT_SECRET}
EPIC_OAUTH_ENABLED=true
ENABLE_EPIC_WRITE_BACK=true
ENABLE_MRN_SCANNING=false
```

#### Production
```bash
# .env.production (via Railway secrets)
INTEGRATION_MODE=epic_integrated
EPIC_SANDBOX_MODE=false
EPIC_FHIR_BASE_URL=https://hospital.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
EPIC_CLIENT_ID=${PROD_CLIENT_ID}  # From hospital IT
EPIC_CLIENT_SECRET=${PROD_CLIENT_SECRET}
EPIC_OAUTH_ENABLED=true
ENABLE_EPIC_WRITE_BACK=true
ENABLE_MRN_SCANNING=true
```

### Deployment Checklist

#### Pre-Production
- [ ] All sandbox tests passing
- [ ] Security review completed
- [ ] Epic App Orchard submission approved
- [ ] Hospital IT approval obtained
- [ ] Production credentials received
- [ ] Firewall rules configured
- [ ] Secrets stored in AWS Secrets Manager
- [ ] Monitoring dashboards created

#### Go-Live
- [ ] Deploy to production with `INTEGRATION_MODE=standalone` first
- [ ] Validate application startup and core functionality
- [ ] Switch to `INTEGRATION_MODE=epic_integrated`
- [ ] Test patient lookup with real MRN
- [ ] Validate condition/medication retrieval
- [ ] Test write-back with sample document
- [ ] Monitor logs for errors
- [ ] Gather nurse feedback

#### Post-Go-Live
- [ ] Monitor Epic API call metrics
- [ ] Review error logs daily for first week
- [ ] Conduct nurse training sessions
- [ ] Document common troubleshooting steps
- [ ] Plan Phase 4 enhancements based on usage

---

## Next Steps (Immediate Actions)

### 1. Epic App Orchard Registration
**Owner**: Project Lead
**Timeline**: This week
**Action Items**:
- [ ] Create developer account at https://fhir.epic.com/
- [ ] Register "AI Nurse Florence" application
- [ ] Request sandbox credentials
- [ ] Document client_id and client_secret in secure location

### 2. Build Mock FHIR Server
**Owner**: Development Team
**Timeline**: 1-2 weeks
**Action Items**:
- [ ] Create `tests/mock_fhir_server.py`
- [ ] Implement Patient, Condition, MedicationRequest endpoints
- [ ] Add realistic Epic FHIR response data
- [ ] Write integration tests using mock server

### 3. Implement EpicFHIRClient
**Owner**: Development Team
**Timeline**: 1-2 weeks
**Action Items**:
- [ ] Create `src/integrations/epic_fhir_client.py`
- [ ] Implement OAuth 2.0 flow (placeholder for now)
- [ ] Add GET/POST methods with error handling
- [ ] Write unit tests for client methods

### 4. Parse FHIR Resources
**Owner**: Development Team
**Timeline**: 1 week
**Action Items**:
- [ ] Implement `_parse_patient_resource()`
- [ ] Implement `_parse_condition_resource()`
- [ ] Implement `_parse_medication_resource()`
- [ ] Add validation and error handling
- [ ] Write tests with real Epic FHIR examples

---

## Questions & Answers

**Q: Can we start development without Epic credentials?**
A: Yes! Phase 1 can be completed entirely with a mock FHIR server. This allows development and testing of all integration logic before Epic access.

**Q: How long does Epic App Orchard approval take?**
A: Sandbox access is immediate. Production approval typically takes 2-3 business days for standard apps.

**Q: Do we need separate credentials for each hospital?**
A: Yes. Each Epic customer (hospital) must approve app installation and provide production credentials.

**Q: What if Epic API is down?**
A: The system gracefully degrades to standalone mode. Nurses can manually enter patient data without Epic integration.

**Q: Is barcode scanning required for Phase 1?**
A: No. MRN can be manually entered. Barcode scanning is Phase 4 enhancement.

**Q: How do we handle multi-tenant deployment?**
A: Store Epic credentials per hospital in database. Switch credentials based on user's hospital affiliation.

---

## Resources

### Epic Documentation
- **Epic on FHIR**: https://fhir.epic.com/
- **App Orchard**: https://orchard.epic.com/
- **FHIR R4 Spec**: https://hl7.org/fhir/R4/
- **SMART on FHIR**: https://docs.smarthealthit.org/

### Development Tools
- **FHIR Validator**: https://validator.fhir.org/
- **Postman Collection**: Epic provides FHIR API collection
- **JWT Debugger**: https://jwt.io/

### Contact
- **Epic Vendor Services**: vendorservices@epic.com
- **Technical Support**: https://fhir.epic.com/Support

---

*This document is a living plan and will be updated as we progress through implementation phases.*
