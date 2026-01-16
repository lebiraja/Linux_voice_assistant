"""
Intents package - Declarative intent definitions.
"""

from .registry import (
    Intent,
    IntentParameter,
    IntentCategory,
    IntentRegistry,
    create_default_intents,
    create_registry_with_defaults
)

__all__ = [
    'Intent',
    'IntentParameter',
    'IntentCategory',
    'IntentRegistry',
    'create_default_intents',
    'create_registry_with_defaults',
]
