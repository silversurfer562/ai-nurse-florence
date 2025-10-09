# Epic Integration Wizard - LangChain Agent Guide

**Copyright 2025 Deep Study AI, LLC**

Licensed under the Apache License, Version 2.0

---

## Overview

The Epic Integration Wizard is a **LangChain-powered multi-step agent** that guides users through configuring and testing Epic FHIR integration for AI Nurse Florence.

**Key Features:**
- **7-step Microsoft-style wizard** - Linear progression with back/next navigation
- **LangGraph workflow** - State management and conditional routing
- **Automatic validation** - Each step validates inputs before proceeding
- **Epic FHIR testing** - Live connection tests with Epic sandbox/production
- **Session persistence** - Resume wizard progress across sessions

---

## Architecture

### LangChain Components

```
┌─────────────────────────────────────────────────────────────┐
│                  Epic Integration Wizard                     │
│                    (LangGraph Agent)                         │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼───┐        ┌─────▼─────┐     ┌─────▼─────┐
    │ State │        │   Tools   │     │  Memory   │
    │ Graph │        │(Epic API) │     │ (Session) │
    └───┬───┘        └───────────┘     └───────────┘
        │
┌───────┼────────────────────────────────────────────┐
│  Step 1: Prerequisites → Step 2: Credentials →     │
│  Step 3: Connection Test → Step 4: Permissions →   │
│  Step 5: Patient Test → Step 6: Review →           │
│  Step 7: Complete                                  │
└────────────────────────────────────────────────────┘
```

### Wizard Steps

| Step | Name | Purpose | Validation |
|------|------|---------|------------|
| 1 | Prerequisites | Check system readiness | Environment variables, packages |
| 2 | Epic Credentials | Collect OAuth credentials | URL format, required fields |
| 3 | Connection Test | Validate Epic FHIR connection | OAuth token, endpoint reachable |
| 4 | Resource Permissions | Select FHIR resources | At least one resource selected |
| 5 | Test Patient Lookup | End-to-end patient retrieval | Valid MRN, patient found |
| 6 | Review & Confirm | Summary and confirmation | User confirms settings |
| 7 | Complete | Activate integration | Save configuration |

---

## API Endpoints

### Base URL
```
/api/v1/wizard
```

### 1. Start Wizard

**POST** `/start`

Start new wizard session or reset existing one.

**Request:**
```json
{
  "reset_existing": true
}
```

**Response:**
```json
{
  "current_step": 1,
  "completed_steps": [1],
  "total_steps": 7,
  "progress_percent": 14,
  "step_name": "Prerequisites Check",
  "step_description": "Validating system requirements",
  "can_proceed": true,
  "errors": [],
  "warnings": [],
  "messages": [
    {
      "role": "ai",
      "content": "✅ All prerequisites met. Ready to configure Epic integration."
    }
  ],
  "state_data": {
    "prerequisites_passed": true,
    "epic_sandbox_mode": true
  }
}
```

### 2. Get Current State

**GET** `/state`

Get current wizard state and progress.

**Response:** Same as `/start` endpoint

### 3. Submit Step Data

**POST** `/step/{step_number}`

Submit data for specific wizard step.

**Step 2 Example (Credentials):**
```json
{
  "epic_client_id": "your_client_id",
  "epic_client_secret": "your_client_secret",
  "epic_fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "epic_oauth_token_url": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
  "epic_sandbox_mode": true
}
```

**Step 4 Example (Resources):**
```json
{
  "selected_resources": ["Patient", "Condition", "MedicationRequest"]
}
```

**Step 5 Example (Test Lookup):**
```json
{
  "test_mrn": "12345678"
}
```

**Step 6 Example (Confirm):**
```json
{
  "configuration_confirmed": true
}
```

### 4. Navigate Wizard

**POST** `/navigate`

Navigate between wizard steps.

**Next:**
```json
{
  "action": "next"
}
```

**Back:**
```json
{
  "action": "back"
}
```

**Jump to Step:**
```json
{
  "action": "jump",
  "target_step": 3
}
```

### 5. Get Progress

**GET** `/progress`

Get wizard progress summary.

**Response:**
```json
{
  "current_step": 3,
  "completed_steps": 2,
  "total_steps": 7,
  "progress_percent": 28,
  "integration_activated": false
}
```

### 6. Reset Wizard

**POST** `/reset`

Reset wizard to initial state.

**Response:**
```json
{
  "message": "Wizard reset successfully",
  "state": { ... }
}
```

---

## Usage Examples

### Complete Wizard Flow (Python)

```python
import httpx

BASE_URL = "https://ai-nurse-florence-production.up.railway.app/api/v1"

async def setup_epic_integration():
    async with httpx.AsyncClient() as client:
        # Step 1: Start wizard
        response = await client.post(f"{BASE_URL}/wizard/start", json={"reset_existing": True})
        state = response.json()
        print(f"Step {state['current_step']}: {state['step_name']}")

        # Step 2: Submit credentials
        credentials = {
            "epic_client_id": "your_client_id",
            "epic_client_secret": "your_client_secret",
            "epic_fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
            "epic_oauth_token_url": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
            "epic_sandbox_mode": True
        }
        response = await client.post(f"{BASE_URL}/wizard/step/2", json=credentials)
        state = response.json()

        if state["errors"]:
            print(f"Errors: {state['errors']}")
            return

        # Step 3: Connection test (automatic)
        # Step 4: Select resources
        resources = {"selected_resources": ["Patient", "Condition", "MedicationRequest"]}
        response = await client.post(f"{BASE_URL}/wizard/step/4", json=resources)
        state = response.json()

        # Step 5: Test patient lookup
        test_data = {"test_mrn": "12345678"}
        response = await client.post(f"{BASE_URL}/wizard/step/5", json=test_data)
        state = response.json()

        if not state["state_data"]["patient_data_retrieved"]:
            print(f"Patient lookup failed: {state['errors']}")
            return

        # Step 6: Review and confirm
        confirm = {"configuration_confirmed": True}
        response = await client.post(f"{BASE_URL}/wizard/step/6", json=confirm)
        state = response.json()

        # Step 7: Complete (automatic)
        progress = await client.get(f"{BASE_URL}/wizard/progress")
        print(f"✅ Integration activated: {progress.json()['integration_activated']}")
```

### JavaScript/Fetch Example

```javascript
const BASE_URL = 'https://ai-nurse-florence-production.up.railway.app/api/v1';

async function setupEpicIntegration() {
    // Start wizard
    let response = await fetch(`${BASE_URL}/wizard/start`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({reset_existing: true})
    });
    let state = await response.json();

    // Submit credentials
    response = await fetch(`${BASE_URL}/wizard/step/2`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            epic_client_id: 'your_client_id',
            epic_client_secret: 'your_client_secret',
            epic_fhir_base_url: 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4',
            epic_oauth_token_url: 'https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token',
            epic_sandbox_mode: true
        })
    });
    state = await response.json();

    console.log(`Progress: ${state.progress_percent}%`);
}
```

---

## State Management

### WizardState TypedDict

```python
class WizardState(TypedDict):
    # Progress
    current_step: int  # 1-7
    completed_steps: list[int]
    messages: list[BaseMessage]

    # Step 1: Prerequisites
    prerequisites_checked: bool
    prerequisites_passed: bool
    missing_prerequisites: list[str]

    # Step 2: Credentials
    epic_client_id: str
    epic_client_secret: str
    epic_fhir_base_url: str
    epic_oauth_token_url: str
    epic_sandbox_mode: bool

    # Step 3: Connection Test
    connection_test_passed: bool
    oauth_token_obtained: bool

    # Step 4: Resources
    selected_resources: list[str]
    resource_scopes: list[str]

    # Step 5: Patient Test
    test_mrn: str
    patient_data_retrieved: bool
    retrieved_patient_name: str

    # Step 6: Confirmation
    configuration_confirmed: bool

    # Step 7: Complete
    integration_activated: bool
    activation_timestamp: str

    # Error Handling
    errors: list[str]
    warnings: list[str]
```

### Session Persistence

Wizard sessions are stored in-memory (for development) or Redis (for production).

**Session ID:** `"default"` (single-user) or user-specific ID

**Session Data:**
```python
{
    "state": WizardState,
    "created_at": "2025-01-09T12:00:00Z",
    "last_updated": "2025-01-09T12:05:30Z"
}
```

---

## LangGraph Workflow

### Node Functions

Each wizard step is implemented as an async node function:

```python
async def step_1_prerequisites(state: WizardState) -> WizardState:
    """Check system prerequisites"""
    # Validate environment
    # Update state
    # Add messages
    return state

async def step_2_credentials(state: WizardState) -> WizardState:
    """Collect Epic credentials"""
    # Validate credentials
    # Update state
    return state

# ... (7 total step functions)
```

### Graph Structure

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(WizardState)

# Add nodes
workflow.add_node("prerequisites", step_1_prerequisites)
workflow.add_node("credentials", step_2_credentials)
workflow.add_node("connection_test", step_3_connection_test)
workflow.add_node("resource_permissions", step_4_resource_permissions)
workflow.add_node("test_patient_lookup", step_5_test_patient_lookup)
workflow.add_node("review_confirm", step_6_review_confirm)
workflow.add_node("complete", step_7_complete)

# Set entry point
workflow.set_entry_point("prerequisites")

# Linear progression (Microsoft wizard pattern)
workflow.add_edge("prerequisites", "credentials")
workflow.add_edge("credentials", "connection_test")
workflow.add_edge("connection_test", "resource_permissions")
workflow.add_edge("resource_permissions", "test_patient_lookup")
workflow.add_edge("test_patient_lookup", "review_confirm")
workflow.add_edge("review_confirm", "complete")
workflow.add_edge("complete", END)

# Compile graph
epic_wizard_graph = workflow.compile()
```

---

## Error Handling

### Validation Errors

Each step validates inputs and adds errors to `state["errors"]` list:

```python
if not state.get("epic_client_id"):
    state["errors"].append("Epic credentials required")
    return state
```

### Connection Errors

Network/API errors are caught and logged:

```python
try:
    token = await oauth_manager.get_access_token()
    state["oauth_token_obtained"] = True
except Exception as e:
    state["connection_test_error"] = str(e)
    state["errors"].append(f"OAuth token request failed: {str(e)}")
```

### Client-Side Error Display

```javascript
const state = await response.json();

if (state.errors.length > 0) {
    state.errors.forEach(error => {
        console.error(`Error: ${error}`);
        // Display in UI
    });
}

if (state.warnings.length > 0) {
    state.warnings.forEach(warning => {
        console.warn(`Warning: ${warning}`);
        // Display in UI
    });
}
```

---

## Testing

### Run Tests

```bash
# All wizard tests
pytest tests/test_epic_wizard.py -v

# Specific test class
pytest tests/test_epic_wizard.py::TestEpicWizardAPI -v

# Single test
pytest tests/test_epic_wizard.py::TestEpicWizardAPI::test_start_wizard -v
```

### Test Coverage

- **API Endpoint Tests** - All 6 endpoints
- **Agent Logic Tests** - Each step function
- **Integration Tests** - End-to-end wizard flows
- **Error Handling Tests** - Validation and network errors

---

## Production Deployment

### Environment Variables

Required for Epic integration:

```bash
# Epic Credentials
EPIC_CLIENT_ID=your_production_client_id
EPIC_CLIENT_SECRET=your_production_client_secret
EPIC_FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
EPIC_OAUTH_TOKEN_URL=https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token

# Application
SECRET_KEY=your_production_secret_key
DATABASE_URL=postgresql://...
```

### Session Storage

**Development:** In-memory dictionary
**Production:** Redis recommended

```python
# Production session storage (Redis)
import redis.asyncio as redis

redis_client = redis.from_url(os.getenv("REDIS_URL"))

async def get_or_create_session(session_id: str):
    data = await redis_client.get(f"wizard:{session_id}")
    if data:
        return json.loads(data)
    # Create new session
```

---

## Frontend Integration

See [EPIC_WIZARD_UI.md](./EPIC_WIZARD_UI.md) for Microsoft-style wizard UI implementation guide.

---

## Troubleshooting

### Prerequisites Check Fails

**Issue:** Missing environment variables
**Solution:** Set `OPENAI_API_KEY` and `SECRET_KEY` in environment

### Connection Test Fails

**Issue:** OAuth token request denied
**Solution:** Verify Epic credentials are correct, check sandbox mode setting

### Patient Lookup Fails

**Issue:** Patient not found with MRN
**Solution:** Use valid Epic sandbox test patient MRNs (e.g., Epic's test patients)

### Recursion Limit Error

**Issue:** Graph enters infinite loop
**Solution:** Check that each step properly updates `current_step` and `completed_steps`

---

## Related Documentation

- [Epic FHIR Integration Guide](./EPIC_INTEGRATION.md)
- [Epic Sandbox Setup](./epic-sandbox-setup.md)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

---

## License

Copyright 2025 Deep Study AI, LLC

Licensed under the Apache License, Version 2.0
