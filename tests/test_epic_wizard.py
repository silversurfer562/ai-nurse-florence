"""
Tests for Epic Integration Wizard - LangChain Agent

Copyright 2025 Deep Study AI, LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

client = TestClient(app)


# =============================================================================
# Wizard API Endpoint Tests
# =============================================================================


class TestEpicWizardAPI:
    """Test Epic Integration Wizard API endpoints"""

    def test_start_wizard(self):
        """Test starting new wizard session"""
        response = client.post("/api/v1/wizard/start", json={"reset_existing": True})

        assert response.status_code == 200
        data = response.json()

        assert (
            data["current_step"] == 1 or data["current_step"] == 2
        )  # After prerequisites check
        assert data["total_steps"] == 7
        assert "progress_percent" in data
        assert "step_name" in data
        assert isinstance(data["errors"], list)
        assert isinstance(data["warnings"], list)

    def test_get_wizard_state(self):
        """Test getting current wizard state"""
        # Start wizard first
        client.post("/api/v1/wizard/start", json={"reset_existing": True})

        # Get state
        response = client.get("/api/v1/wizard/state")

        assert response.status_code == 200
        data = response.json()

        assert "current_step" in data
        assert "completed_steps" in data
        assert "progress_percent" in data
        assert "step_name" in data
        assert "can_proceed" in data

    def test_submit_step_2_credentials(self):
        """Test submitting Epic credentials (Step 2)"""
        # Start wizard
        client.post("/api/v1/wizard/start", json={"reset_existing": True})

        # Submit credentials
        credentials = {
            "epic_client_id": "test_client_id",
            "epic_client_secret": "test_client_secret",
            "epic_fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
            "epic_oauth_token_url": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
            "epic_sandbox_mode": True,
        }

        response = client.post("/api/v1/wizard/step/2", json=credentials)

        assert response.status_code == 200
        data = response.json()

        # Should advance to step 3 (connection test) or stay on step 2 with errors
        assert data["current_step"] in [2, 3]

    def test_navigate_back(self):
        """Test navigating back in wizard"""
        # Start wizard and advance a few steps
        client.post("/api/v1/wizard/start", json={"reset_existing": True})

        # Navigate back
        response = client.post("/api/v1/wizard/navigate", json={"action": "back"})

        assert response.status_code == 200
        data = response.json()

        # Should be at step 1 (can't go back further)
        assert data["current_step"] >= 1

    def test_get_wizard_progress(self):
        """Test getting wizard progress summary"""
        # Start wizard
        client.post("/api/v1/wizard/start", json={"reset_existing": True})

        # Get progress
        response = client.get("/api/v1/wizard/progress")

        assert response.status_code == 200
        data = response.json()

        assert "current_step" in data
        assert "completed_steps" in data
        assert "total_steps" in data
        assert data["total_steps"] == 7
        assert "progress_percent" in data
        assert "integration_activated" in data

    def test_reset_wizard(self):
        """Test resetting wizard to initial state"""
        # Start and advance wizard
        client.post("/api/v1/wizard/start", json={"reset_existing": True})

        # Reset
        response = client.post("/api/v1/wizard/reset")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["state"]["current_step"] == 1
        assert (
            len(data["state"]["completed_steps"]) >= 0
        )  # May have prerequisites completed


# =============================================================================
# Wizard Agent Logic Tests
# =============================================================================


@pytest.mark.asyncio
class TestEpicWizardAgent:
    """Test Epic Integration Wizard agent logic"""

    async def test_create_initial_state(self):
        """Test creating initial wizard state"""
        try:
            from agents.epic_integration_wizard import create_initial_state

            state = create_initial_state()

            assert state["current_step"] == 1
            assert state["completed_steps"] == []
            assert state["prerequisites_checked"] is False
            assert state["integration_activated"] is False
            assert state["errors"] == []
            assert state["warnings"] == []
        except ImportError:
            pytest.skip("LangChain dependencies not installed")

    async def test_step_1_prerequisites(self):
        """Test prerequisites check step"""
        try:
            from agents.epic_integration_wizard import (
                create_initial_state,
                step_1_prerequisites,
            )

            state = create_initial_state()
            result = await step_1_prerequisites(state)

            assert result["prerequisites_checked"] is True
            assert 1 in result["completed_steps"]
            # May pass or fail depending on environment
            assert isinstance(result["prerequisites_passed"], bool)
        except ImportError:
            pytest.skip("LangChain dependencies not installed")

    async def test_step_2_credentials_validation(self):
        """Test credentials validation step"""
        try:
            from agents.epic_integration_wizard import (
                create_initial_state,
                step_2_credentials,
            )

            state = create_initial_state()
            state["current_step"] = 2

            # Test with missing credentials
            result = await step_2_credentials(state)
            assert len(result["errors"]) > 0

            # Test with valid credentials
            state["epic_client_id"] = "test_client"
            state["epic_client_secret"] = "test_secret"
            state["epic_fhir_base_url"] = "https://fhir.epic.com/test"

            result = await step_2_credentials(state)
            assert 2 in result["completed_steps"]
            assert result["current_step"] == 3
        except ImportError:
            pytest.skip("LangChain dependencies not installed")

    async def test_step_4_resource_permissions(self):
        """Test resource permissions selection"""
        try:
            from agents.epic_integration_wizard import (
                create_initial_state,
                step_4_resource_permissions,
            )

            state = create_initial_state()
            state["current_step"] = 4

            # Test with no resources selected
            result = await step_4_resource_permissions(state)
            assert len(result["errors"]) > 0

            # Test with resources selected
            state["selected_resources"] = ["Patient", "Condition", "MedicationRequest"]
            result = await step_4_resource_permissions(state)

            assert 4 in result["completed_steps"]
            assert len(result["resource_scopes"]) == 3
            assert "Patient.Read" in result["resource_scopes"]
            assert "Condition.Read" in result["resource_scopes"]
        except ImportError:
            pytest.skip("LangChain dependencies not installed")

    async def test_wizard_graph_compilation(self):
        """Test that wizard graph compiles successfully"""
        try:
            from agents.epic_integration_wizard import create_epic_wizard_graph

            graph = create_epic_wizard_graph()
            assert graph is not None
        except ImportError:
            pytest.skip("LangChain dependencies not installed")


# =============================================================================
# Integration Tests
# =============================================================================


class TestEpicWizardIntegration:
    """End-to-end integration tests"""

    def test_complete_wizard_flow_happy_path(self):
        """Test complete wizard flow with valid inputs"""
        # Step 1: Start wizard
        response = client.post("/api/v1/wizard/start", json={"reset_existing": True})
        assert response.status_code == 200

        # Step 2: Submit credentials
        credentials = {
            "epic_client_id": "demo_client",
            "epic_client_secret": "demo_secret",
            "epic_fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
            "epic_oauth_token_url": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
            "epic_sandbox_mode": True,
        }
        response = client.post("/api/v1/wizard/step/2", json=credentials)
        assert response.status_code == 200

        # Verify progress
        response = client.get("/api/v1/wizard/progress")
        data = response.json()
        assert data["current_step"] >= 2

    def test_wizard_navigation_flow(self):
        """Test wizard navigation (next, back, jump)"""
        # Start wizard
        client.post("/api/v1/wizard/start", json={"reset_existing": True})

        # Navigate forward
        response = client.post("/api/v1/wizard/navigate", json={"action": "next"})
        # May succeed or fail depending on step completion
        assert response.status_code in [200, 400]

        # Navigate back
        response = client.post("/api/v1/wizard/navigate", json={"action": "back"})
        assert response.status_code == 200

        # Try to jump to incomplete step (should fail)
        response = client.post(
            "/api/v1/wizard/navigate", json={"action": "jump", "target_step": 7}
        )
        assert response.status_code == 400

    def test_wizard_error_handling(self):
        """Test wizard handles errors gracefully"""
        # Start wizard
        client.post("/api/v1/wizard/start", json={"reset_existing": True})

        # Submit invalid credentials (missing fields)
        response = client.post(
            "/api/v1/wizard/step/2",
            json={
                "epic_client_id": "test"
                # Missing other required fields
            },
        )

        # Should return success but with errors in state
        assert response.status_code == 200
        data = response.json()
        assert len(data["errors"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
