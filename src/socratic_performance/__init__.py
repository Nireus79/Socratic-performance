"""
Socratic Performance - Performance Monitoring and Subscription Management

Extracted from Socrates v1.3.3
"""

from .checker import SubscriptionChecker
from .tiers import SubscriptionTier

__version__ = "1.3.3"
__all__ = ["SubscriptionChecker", "SubscriptionTier"]
