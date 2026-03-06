from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Action(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    FLAG = "FLAG"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CompliancePolicyReference(BaseModel):
    policy_id: str = Field(..., description="ID or reference of the policy rule triggered")
    policy_name: str = Field(..., description="Name or description of the policy")


class Transaction(BaseModel):
    transaction_id: str = Field(..., description="Unique identifier for the transaction")
    user_id: str = Field(..., description="Identifier for the user initiating the transaction")
    amount: float = Field(..., description="Transaction amount (used for SQL threshold rules)")
    merchant_category: str = Field(..., description="Merchant category or code (useful for vector/hybrid search)")
    timestamp: datetime = Field(..., description="When the transaction occurred")
    currency: str = Field(default="USD", description="Currency of the transaction")
    destination_country: str = Field(..., description="ISO 3166-1 alpha-2 country code of the destination")
    description: Optional[str] = Field(default=None, description="Optional textual memo describing the transaction")


class ComplianceReport(BaseModel):
    transaction_id: str = Field(..., description="The ID of the transaction audited")
    action: Action = Field(..., description="The final decision: ALLOW, BLOCK, or FLAG")
    risk_level: RiskLevel = Field(..., description="The assessed overall risk level of this transaction")
    reasoning: str = Field(..., description="Detailed explanation of the decision, supported solely by retrieved context")
    policies_triggered: List[CompliancePolicyReference] = Field(
        default_factory=list, 
        description="List of specific policies that were violated or flagged"
    )
    audited_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        description="Timestamp of when the audit was generated"
    )
