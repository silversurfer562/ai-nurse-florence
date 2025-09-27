# services/model_selector.py
"""
Model Selection Service - AI Nurse Florence
Context-aware OpenAI model selection with GPT-5 migration strategy
Following Service Layer Architecture with Conditional Imports Pattern
"""

import logging
import os
from typing import Dict, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)

class DeploymentMode(Enum):
    """Deployment modes with different model availability"""
    DEVELOPMENT = "development"
    ENTERPRISE_CHATGPT = "enterprise_chatgpt"  
    CHATGPT_STORE = "chatgpt_store"
    PRODUCTION_API = "production_api"

class ModelTier(Enum):
    """Model tiers based on capability and use case"""
    BASIC = "basic"           # Data fetching, simple summarization
    ADVANCED = "advanced"     # Complex reasoning, analysis
    PREMIUM = "premium"       # Future GPT-5 tier for highest complexity

# Current model mapping (will be updated when GPT-5 available)
CURRENT_MODEL_MAP = {
    # GPT-4 family for basic data processing
    "gpt4_basic": "gpt-4-turbo-preview",
    
    # GPT-4o for advanced reasoning (placeholder for GPT-5)
    "gpt4_advanced": "gpt-4o",
    
    # Future GPT-5 (not yet available)
    "gpt5_premium": "gpt-4o"  # Falls back to GPT-4o until GPT-5 released
}

# Enterprise ChatGPT model mapping
ENTERPRISE_MODEL_MAP = {
    "enterprise_standard": "gpt-4",
    "enterprise_turbo": "gpt-4-turbo", 
    "enterprise_omni": "gpt-4o",
    "enterprise_preview": "gpt-4-turbo-preview"
}

# Model selection matrix following your strategy
MODEL_SELECTION_MATRIX: Dict[str, Dict[str, str]] = {
    # Data fetching and basic processing - GPT-4 family
    "medical_summary": {
        "basic": CURRENT_MODEL_MAP["gpt4_basic"],
        "advanced": CURRENT_MODEL_MAP["gpt4_basic"],
        "premium": CURRENT_MODEL_MAP["gpt4_advanced"]
    },
    
    "disease_lookup": {
        "basic": CURRENT_MODEL_MAP["gpt4_basic"],
        "advanced": CURRENT_MODEL_MAP["gpt4_basic"], 
        "premium": CURRENT_MODEL_MAP["gpt4_advanced"]
    },
    
    "drug_lookup": {
        "basic": CURRENT_MODEL_MAP["gpt4_basic"],
        "advanced": CURRENT_MODEL_MAP["gpt4_advanced"],  # Drug interactions need reasoning
        "premium": CURRENT_MODEL_MAP["gpt5_premium"]
    },
    
    "literature_summary": {
        "basic": CURRENT_MODEL_MAP["gpt4_basic"],
        "advanced": CURRENT_MODEL_MAP["gpt4_basic"],
        "premium": CURRENT_MODEL_MAP["gpt4_advanced"]
    },
    
    # Analysis and reasoning - GPT-4o/Future GPT-5
    "symptom_analysis": {
        "basic": CURRENT_MODEL_MAP["gpt4_advanced"],     # All symptom analysis needs reasoning
        "advanced": CURRENT_MODEL_MAP["gpt4_advanced"],
        "premium": CURRENT_MODEL_MAP["gpt5_premium"]
    },
    
    "clinical_reasoning": {
        "basic": CURRENT_MODEL_MAP["gpt4_advanced"],
        "advanced": CURRENT_MODEL_MAP["gpt4_advanced"],
        "premium": CURRENT_MODEL_MAP["gpt5_premium"]
    },
    
    "differential_diagnosis": {
        "basic": CURRENT_MODEL_MAP["gpt4_advanced"],
        "advanced": CURRENT_MODEL_MAP["gpt4_advanced"],
        "premium": CURRENT_MODEL_MAP["gpt5_premium"]
    },
    
    "treatment_planning": {
        "basic": CURRENT_MODEL_MAP["gpt4_advanced"],
        "advanced": CURRENT_MODEL_MAP["gpt4_advanced"],
        "premium": CURRENT_MODEL_MAP["gpt5_premium"]
    },
    
    "drug_interactions": {
        "basic": CURRENT_MODEL_MAP["gpt4_advanced"],     # Safety-critical, always advanced
        "advanced": CURRENT_MODEL_MAP["gpt4_advanced"],
        "premium": CURRENT_MODEL_MAP["gpt5_premium"]
    },
    
    "patient_education": {
        "basic": CURRENT_MODEL_MAP["gpt4_basic"],         # Basic education can use GPT-4
        "advanced": CURRENT_MODEL_MAP["gpt4_basic"],
        "premium": CURRENT_MODEL_MAP["gpt4_advanced"]
    },
    
    # Wizard contexts following Wizard Pattern Implementation
    "wizard_treatment_plan": {
        "basic": CURRENT_MODEL_MAP["gpt4_advanced"],      # Treatment planning needs reasoning
        "advanced": CURRENT_MODEL_MAP["gpt4_advanced"],
        "premium": CURRENT_MODEL_MAP["gpt5_premium"]
    },
    
    "wizard_sbar": {
        "basic": CURRENT_MODEL_MAP["gpt4_basic"],         # SBAR formatting is structured
        "advanced": CURRENT_MODEL_MAP["gpt4_basic"],
        "premium": CURRENT_MODEL_MAP["gpt4_advanced"]
    },
    
    "wizard_patient_education": {
        "basic": CURRENT_MODEL_MAP["gpt4_basic"],
        "advanced": CURRENT_MODEL_MAP["gpt4_advanced"],
        "premium": CURRENT_MODEL_MAP["gpt5_premium"]
    }
}

# Enterprise ChatGPT selection matrix
ENTERPRISE_SELECTION_MATRIX: Dict[str, Dict[str, str]] = {
    "medical_summary": {
        "basic": ENTERPRISE_MODEL_MAP["enterprise_standard"],
        "advanced": ENTERPRISE_MODEL_MAP["enterprise_turbo"],
        "premium": ENTERPRISE_MODEL_MAP["enterprise_omni"]
    },
    
    "symptom_analysis": {
        "basic": ENTERPRISE_MODEL_MAP["enterprise_turbo"],
        "advanced": ENTERPRISE_MODEL_MAP["enterprise_omni"],
        "premium": ENTERPRISE_MODEL_MAP["enterprise_omni"]
    },
    
    "clinical_reasoning": {
        "basic": ENTERPRISE_MODEL_MAP["enterprise_omni"],    # Always use best for clinical reasoning
        "advanced": ENTERPRISE_MODEL_MAP["enterprise_omni"],
        "premium": ENTERPRISE_MODEL_MAP["enterprise_omni"]
    },
    
    "chatgpt_store_query": {
        "basic": ENTERPRISE_MODEL_MAP["enterprise_standard"],
        "advanced": ENTERPRISE_MODEL_MAP["enterprise_turbo"],
        "premium": ENTERPRISE_MODEL_MAP["enterprise_omni"]
    }
}

def get_deployment_mode() -> DeploymentMode:
    """
    Detect current deployment mode from environment
    Following Configuration Management patterns
    """
    if os.getenv("ENTERPRISE_CHATGPT_MODE", "").lower() == "true":
        return DeploymentMode.ENTERPRISE_CHATGPT
    elif os.getenv("CHATGPT_STORE_MODE", "").lower() == "true":
        return DeploymentMode.CHATGPT_STORE
    elif os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PRODUCTION"):
        return DeploymentMode.PRODUCTION_API
    else:
        return DeploymentMode.DEVELOPMENT

def select_model_for_context(
    context: str, 
    complexity: str = "basic",
    deployment_override: Optional[DeploymentMode] = None,
    safety_critical: bool = False
) -> str:
    """
    Select appropriate OpenAI model based on context and complexity
    Following user strategy: GPT-4 for basic data, GPT-4o/GPT-5 for analysis
    
    Args:
        context: Task context (e.g., 'symptom_analysis', 'medical_summary')
        complexity: Complexity level ('basic', 'advanced', 'premium')
        deployment_override: Override detected deployment mode
        safety_critical: Force premium model for safety-critical tasks
        
    Returns:
        Model name string for OpenAI API
    """
    mode = deployment_override or get_deployment_mode()
    
    logger.info(f"Selecting model for context: {context}, complexity: {complexity}, mode: {mode.value}")
    
    # Safety-critical tasks always use premium model
    if safety_critical:
        complexity = "premium"
        logger.info("Safety-critical task, upgrading to premium complexity")
    
    # Enterprise ChatGPT / ChatGPT Store model selection
    if mode in [DeploymentMode.ENTERPRISE_CHATGPT, DeploymentMode.CHATGPT_STORE]:
        context_models = ENTERPRISE_SELECTION_MATRIX.get(context, ENTERPRISE_SELECTION_MATRIX.get("medical_summary", {}))
        selected_model = context_models.get(complexity, ENTERPRISE_MODEL_MAP["enterprise_standard"])
        
        logger.info(f"Enterprise mode - selected: {selected_model}")
        return selected_model
    
    # Production API model selection (your existing strategy)
    else:
        context_models = MODEL_SELECTION_MATRIX.get(context, MODEL_SELECTION_MATRIX.get("medical_summary", {}))
        selected_model = context_models.get(complexity, CURRENT_MODEL_MAP["gpt4_basic"])
        
        logger.info(f"Production API mode - selected: {selected_model}")
        return selected_model

def get_enterprise_model(task_type: str) -> str:
    """
    Get Enterprise ChatGPT model for specific medical tasks
    Optimized for Enterprise ChatGPT and ChatGPT Store deployment
    """
    mode = get_deployment_mode()
    
    if mode == DeploymentMode.ENTERPRISE_CHATGPT:
        # Enterprise ChatGPT - use best available models
        enterprise_task_map = {
            "medical_summary": ENTERPRISE_MODEL_MAP["enterprise_standard"],
            "symptom_analysis": ENTERPRISE_MODEL_MAP["enterprise_omni"],     # Best model for clinical analysis
            "clinical_reasoning": ENTERPRISE_MODEL_MAP["enterprise_omni"],
            "treatment_planning": ENTERPRISE_MODEL_MAP["enterprise_omni"],
            "drug_interactions": ENTERPRISE_MODEL_MAP["enterprise_omni"],    # Safety-critical
            "patient_education": ENTERPRISE_MODEL_MAP["enterprise_turbo"],
            "literature_summary": ENTERPRISE_MODEL_MAP["enterprise_standard"],
            "chatgpt_interaction": ENTERPRISE_MODEL_MAP["enterprise_turbo"]  # For ChatGPT Store conversations
        }
        
        selected = enterprise_task_map.get(task_type, ENTERPRISE_MODEL_MAP["enterprise_standard"])
        logger.info(f"Enterprise ChatGPT - Task: {task_type}, Model: {selected}")
        return selected
    
    elif mode == DeploymentMode.CHATGPT_STORE:
        # ChatGPT Store - optimize for user interaction
        store_task_map = {
            "medical_summary": ENTERPRISE_MODEL_MAP["enterprise_standard"],
            "symptom_analysis": ENTERPRISE_MODEL_MAP["enterprise_turbo"],    # Good balance for store users
            "clinical_reasoning": ENTERPRISE_MODEL_MAP["enterprise_turbo"],
            "patient_education": ENTERPRISE_MODEL_MAP["enterprise_standard"],
            "gpt_conversation": ENTERPRISE_MODEL_MAP["enterprise_turbo"],    # Interactive conversations
            "user_query": ENTERPRISE_MODEL_MAP["enterprise_standard"]        # Basic user queries
        }
        
        selected = store_task_map.get(task_type, ENTERPRISE_MODEL_MAP["enterprise_standard"])
        logger.info(f"ChatGPT Store - Task: {task_type}, Model: {selected}")
        return selected
    
    # Fallback to production API selection
    else:
        return select_model_for_context(task_type, "advanced")

def get_model_capabilities(model_name: str) -> Dict[str, Union[str, list, dict, bool]]:
    """Get capabilities metadata for a model"""
    capabilities = {
        "gpt-4-turbo-preview": {
            "family": "GPT-4",
            "tier": "basic",
            "strengths": ["data_summarization", "structured_output", "cost_efficient"],
            "use_cases": ["medical_summaries", "literature_review", "basic_analysis"],
            "max_tokens": 4096,
            "context_window": 128000,
            "cost_per_1k_tokens": {"input": 0.01, "output": 0.03}
        },
        
        "gpt-4o": {
            "family": "GPT-4o", 
            "tier": "advanced",
            "strengths": ["advanced_reasoning", "clinical_analysis", "complex_patterns"],
            "use_cases": ["symptom_analysis", "differential_diagnosis", "treatment_planning"],
            "max_tokens": 4096,
            "context_window": 128000,
            "cost_per_1k_tokens": {"input": 0.005, "output": 0.015}
        },
        
        "gpt-4": {
            "family": "GPT-4",
            "tier": "enterprise_standard",
            "strengths": ["reliable_reasoning", "enterprise_ready", "balanced_performance"],
            "use_cases": ["enterprise_queries", "medical_summaries", "clinical_documentation"],
            "max_tokens": 8192,
            "context_window": 32000,
            "cost_per_1k_tokens": {"input": 0.03, "output": 0.06}
        },
        
        "gpt-4-turbo": {
            "family": "GPT-4-Turbo",
            "tier": "enterprise_advanced",
            "strengths": ["enhanced_reasoning", "longer_context", "improved_accuracy"],
            "use_cases": ["complex_analysis", "clinical_reasoning", "comprehensive_summaries"],
            "max_tokens": 4096,
            "context_window": 128000,
            "cost_per_1k_tokens": {"input": 0.01, "output": 0.03}
        },
        
        "gpt-5-turbo": {  # Future model
            "family": "GPT-5",
            "tier": "premium", 
            "strengths": ["superior_reasoning", "medical_expertise", "multimodal"],
            "use_cases": ["complex_diagnosis", "research_analysis", "expert_consultation"],
            "max_tokens": 8192,
            "context_window": 200000,
            "cost_per_1k_tokens": {"input": 0.02, "output": 0.06},  # Estimated
            "available": False  # Will be True when released
        }
    }
    
    return capabilities.get(model_name, {
        "family": "Unknown",
        "tier": "basic",
        "strengths": [],
        "use_cases": [],
        "max_tokens": 4096,
        "context_window": 8192,
        "cost_per_1k_tokens": {"input": 0.01, "output": 0.03}
    })

def check_gpt5_availability() -> bool:
    """
    Check if GPT-5 is available via environment flag or API test
    """
    # Environment flag method (manual override)
    if os.getenv("GPT5_AVAILABLE", "").lower() == "true":
        logger.info("GPT-5 marked as available via environment flag")
        return True
    
    # TODO: Add actual API availability check when GPT-5 is released
    # This would make a test call to OpenAI API to check model availability
    
    logger.info("GPT-5 not yet available")
    return False

def prepare_for_gpt5_migration():
    """
    Prepare system for GPT-5 migration when it becomes available
    This function will update model mappings
    """
    logger.info("Preparing GPT-5 migration strategy")
    
    gpt5_available = check_gpt5_availability()
    
    if gpt5_available:
        logger.info("GPT-5 detected - updating model mappings")
        
        # Update global model mapping for GPT-5
        global CURRENT_MODEL_MAP
        CURRENT_MODEL_MAP["gpt5_premium"] = "gpt-5-turbo"
        
        # Update selection matrix for premium tasks
        premium_contexts = [
            "symptom_analysis", "clinical_reasoning", "differential_diagnosis",
            "treatment_planning", "drug_interactions", "wizard_treatment_plan"
        ]
        
        for context in premium_contexts:
            if context in MODEL_SELECTION_MATRIX:
                MODEL_SELECTION_MATRIX[context]["premium"] = "gpt-5-turbo"
        
        logger.info("Model selection matrix updated for GPT-5")
        return True
    
    logger.info("GPT-5 not yet available - using GPT-4o for premium tasks")
    return False

def validate_model_for_task(context: str, model_name: str) -> bool:
    """Validate if selected model is appropriate for the task"""
    capabilities = get_model_capabilities(model_name)
    
    # Safety-critical contexts should use advanced models
    safety_critical_contexts = [
        "drug_interactions", 
        "symptom_analysis", 
        "differential_diagnosis",
        "treatment_planning"
    ]
    
    if context in safety_critical_contexts:
        return capabilities.get("tier") in ["advanced", "premium", "enterprise_advanced", "enterprise_omni"]
    
    return True  # Other contexts can use any model

# Context-specific helper functions following Service Layer Architecture
def select_medical_model(task_type: str, clinical_complexity: str = "basic") -> str:
    """Helper for medical-specific model selection"""
    medical_context_map = {
        "summarize": "medical_summary",
        "analyze": "symptom_analysis", 
        "diagnose": "differential_diagnosis",
        "treat": "treatment_planning",
        "educate": "patient_education",
        "lookup": "disease_lookup"
    }
    
    context = medical_context_map.get(task_type, "medical_summary")
    return select_model_for_context(context, clinical_complexity)

def select_wizard_model(wizard_type: str, step_complexity: str = "basic") -> str:
    """Helper for wizard-specific model selection following Wizard Pattern Implementation"""
    wizard_context = f"wizard_{wizard_type}"
    return select_model_for_context(wizard_context, step_complexity)

def get_chatgpt_store_capabilities() -> Dict[str, Union[list, dict, bool, str]]:
    """Get ChatGPT Store specific capabilities and limitations"""
    return {
        "supported_models": list(ENTERPRISE_MODEL_MAP.values()),
        "features": {
            "conversation_memory": True,
            "function_calling": True,
            "custom_instructions": True,
            "file_uploads": True,         # If supported in your store config
            "web_browsing": False,        # Typically disabled for medical apps
            "code_interpreter": False     # May not be needed for medical info
        },
        "limitations": {
            "max_conversation_length": "Context window dependent",
            "rate_limits": "Enterprise tier limits",
            "data_retention": "Per enterprise policy"
        },
        "medical_disclaimers": {
            "required": True,
            "banner": "Educational use only - not medical advice. No PHI stored.",
            "liability": "Healthcare professional review required"
        }
    }

def format_for_chatgpt_store(response: Dict[str, Union[str, dict, list]]) -> Dict[str, Union[str, dict, list, bool]]:
    """Format response for optimal ChatGPT Store display"""
    return {
        **response,
        "chatgpt_store_optimized": True,
        "display_format": "conversational",
        "medical_disclaimer": "🏥 Educational information for healthcare professionals only",
        "interaction_context": "chatgpt_store"
    }

def get_store_conversation_context(user_message: str) -> str:
    """Determine conversation context for ChatGPT Store interactions"""
    medical_keywords = ["symptom", "disease", "drug", "treatment", "diagnosis", "patient", "medication", "condition"]
    
    if any(keyword in user_message.lower() for keyword in medical_keywords):
        return "medical_query"
    else:
        return "general_query"

def validate_enterprise_config() -> Dict[str, bool]:
    """Validate Enterprise ChatGPT configuration following Configuration Management"""
    return {
        "enterprise_mode_enabled": get_deployment_mode() == DeploymentMode.ENTERPRISE_CHATGPT,
        "chatgpt_store_mode_enabled": get_deployment_mode() == DeploymentMode.CHATGPT_STORE,
        "api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        "enterprise_org_configured": bool(os.getenv("OPENAI_ORG_ID")),
        "medical_disclaimers_enabled": True,  # Always required for medical content
        "gpt5_ready": check_gpt5_availability()
    }

# Initialize migration check on module load
try:
    prepare_for_gpt5_migration()
except Exception as e:
    logger.warning(f"GPT-5 migration preparation failed: {e}")
