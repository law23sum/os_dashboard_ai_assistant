"""
Billing System - Usage tracking, cost management, and billing operations
Handles subscription management, usage metering, and financial reporting
"""

import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
import logging
from pathlib import Path
import uuid
from collections import defaultdict, Counter
from decimal import Decimal, ROUND_HALF_UP
import calendar

from assistant_core.data_aggregator import CIRDocument, DocumentType, SourceType


class BillingPlan(Enum):
    """Billing plan types"""

    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class UsageMetric(Enum):
    """Usage metrics for billing"""

    API_CALLS = "api_calls"
    DATA_STORAGE_GB = "data_storage_gb"
    COMPUTE_HOURS = "compute_hours"
    AI_REQUESTS = "ai_requests"
    USERS_ACTIVE = "users_active"
    PROJECTS = "projects"
    DOCUMENTS_PROCESSED = "documents_processed"
    INTEGRATIONS = "integrations"
    BANDWIDTH_GB = "bandwidth_gb"
    BACKUP_STORAGE_GB = "backup_storage_gb"


class BillingCycle(Enum):
    """Billing cycle types"""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    USAGE_BASED = "usage_based"


class PaymentStatus(Enum):
    """Payment status"""

    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class SubscriptionStatus(Enum):
    """Subscription status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class PricingTier:
    """Pricing tier definition"""

    tier_id: str
    name: str
    description: str
    base_price: Decimal
    currency: str = "USD"
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    usage_limits: Dict[UsageMetric, int] = field(default_factory=dict)
    overage_rates: Dict[UsageMetric, Decimal] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "base_price": str(self.base_price),
            "billing_cycle": self.billing_cycle.value,
            "usage_limits": {
                metric.value: limit for metric, limit in self.usage_limits.items()
            },
            "overage_rates": {
                metric.value: str(rate) for metric, rate in self.overage_rates.items()
            },
        }


@dataclass
class Subscription:
    """Customer subscription"""

    subscription_id: str
    customer_id: str
    plan: BillingPlan
    pricing_tier_id: str
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    auto_renew: bool = True
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    custom_pricing: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "plan": self.plan.value,
            "status": self.status.value,
            "billing_cycle": self.billing_cycle.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "next_billing_date": self.next_billing_date.isoformat()
            if self.next_billing_date
            else None,
        }


@dataclass
class UsageRecord:
    """Usage tracking record"""

    usage_id: str
    customer_id: str
    subscription_id: str
    metric: UsageMetric
    quantity: Decimal
    timestamp: datetime
    billing_period_start: datetime
    billing_period_end: datetime
    unit_price: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "metric": self.metric.value,
            "quantity": str(self.quantity),
            "timestamp": self.timestamp.isoformat(),
            "billing_period_start": self.billing_period_start.isoformat(),
            "billing_period_end": self.billing_period_end.isoformat(),
            "unit_price": str(self.unit_price) if self.unit_price else None,
            "total_cost": str(self.total_cost) if self.total_cost else None,
        }


@dataclass
class Invoice:
    """Billing invoice"""

    invoice_id: str
    customer_id: str
    subscription_id: str
    invoice_number: str
    billing_period_start: datetime
    billing_period_end: datetime
    issue_date: datetime
    due_date: datetime
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    payment_method: Optional[str] = None
    paid_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "billing_period_start": self.billing_period_start.isoformat(),
            "billing_period_end": self.billing_period_end.isoformat(),
            "issue_date": self.issue_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "subtotal": str(self.subtotal),
            "tax_amount": str(self.tax_amount),
            "total_amount": str(self.total_amount),
            "status": self.status.value,
            "paid_date": self.paid_date.isoformat() if self.paid_date else None,
        }


@dataclass
class Customer:
    """Billing customer"""

    customer_id: str
    name: str
    email: str
    company: Optional[str] = None
    billing_address: Dict[str, str] = field(default_factory=dict)
    tax_id: Optional[str] = None
    payment_methods: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "created_at": self.created_at.isoformat()}


@dataclass
class BillingAlert:
    """Billing alert configuration"""

    alert_id: str
    customer_id: str
    alert_type: str  # usage_threshold, payment_failed, subscription_expiring
    threshold_value: Optional[Decimal] = None
    threshold_metric: Optional[UsageMetric] = None
    is_active: bool = True
    notification_channels: List[str] = field(
        default_factory=list
    )  # email, webhook, sms

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "threshold_value": str(self.threshold_value)
            if self.threshold_value
            else None,
            "threshold_metric": self.threshold_metric.value
            if self.threshold_metric
            else None,
        }


class UsageTracker:
    """Usage tracking and metering"""

    def __init__(self):
        self.usage_records: Dict[str, UsageRecord] = {}
        self.current_usage: Dict[str, Dict[UsageMetric, Decimal]] = defaultdict(
            lambda: defaultdict(Decimal)
        )

        self.logger = logging.getLogger(__name__)

    async def record_usage(
        self,
        customer_id: str,
        subscription_id: str,
        metric: UsageMetric,
        quantity: Decimal,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UsageRecord:
        """Record usage event"""
        try:
            now = datetime.utcnow()

            # Determine billing period
            billing_period_start, billing_period_end = self._get_billing_period(now)

            usage_record = UsageRecord(
                usage_id=str(uuid.uuid4()),
                customer_id=customer_id,
                subscription_id=subscription_id,
                metric=metric,
                quantity=quantity,
                timestamp=now,
                billing_period_start=billing_period_start,
                billing_period_end=billing_period_end,
                metadata=metadata or {},
            )

            # Store usage record
            self.usage_records[usage_record.usage_id] = usage_record

            # Update current usage totals
            period_key = f"{customer_id}_{billing_period_start.strftime('%Y-%m')}"
            self.current_usage[period_key][metric] += quantity

            self.logger.info(
                f"Usage recorded: {customer_id} - {metric.value}: {quantity}"
            )
            return usage_record

        except Exception as e:
            self.logger.error(f"Usage recording failed: {e}")
            raise

    def _get_billing_period(self, timestamp: datetime) -> Tuple[datetime, datetime]:
        """Get billing period for timestamp"""
        # Monthly billing period
        start = timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Last day of month
        last_day = calendar.monthrange(start.year, start.month)[1]
        end = start.replace(
            day=last_day, hour=23, minute=59, second=59, microsecond=999999
        )

        return start, end

    async def get_usage_summary(
        self,
        customer_id: str,
        billing_period_start: datetime,
        billing_period_end: datetime,
    ) -> Dict[UsageMetric, Decimal]:
        """Get usage summary for billing period"""
        try:
            usage_summary = defaultdict(Decimal)

            for record in self.usage_records.values():
                if (
                    record.customer_id == customer_id
                    and record.billing_period_start <= billing_period_start
                    and record.billing_period_end >= billing_period_end
                ):
                    usage_summary[record.metric] += record.quantity

            return dict(usage_summary)

        except Exception as e:
            self.logger.error(f"Usage summary failed: {e}")
            return {}

    async def check_usage_limits(
        self,
        customer_id: str,
        subscription_id: str,
        usage_limits: Dict[UsageMetric, int],
    ) -> Dict[str, Any]:
        """Check if usage exceeds limits"""
        try:
            now = datetime.utcnow()
            billing_period_start, billing_period_end = self._get_billing_period(now)

            current_usage = await self.get_usage_summary(
                customer_id, billing_period_start, billing_period_end
            )

            limit_status = {}
            overages = {}

            for metric, limit in usage_limits.items():
                current = current_usage.get(metric, Decimal("0"))
                usage_percentage = (
                    (current / Decimal(str(limit))) * 100 if limit > 0 else 0
                )

                limit_status[metric.value] = {
                    "current": str(current),
                    "limit": limit,
                    "percentage": float(usage_percentage),
                    "exceeded": current > Decimal(str(limit)),
                }

                if current > Decimal(str(limit)):
                    overages[metric.value] = str(current - Decimal(str(limit)))

            return {
                "billing_period": {
                    "start": billing_period_start.isoformat(),
                    "end": billing_period_end.isoformat(),
                },
                "limits": limit_status,
                "overages": overages,
                "has_overages": bool(overages),
            }

        except Exception as e:
            self.logger.error(f"Usage limit check failed: {e}")
            return {}


class BillingCalculator:
    """Billing calculation engine"""

    def __init__(self):
        self.tax_rates: Dict[str, Decimal] = {
            "US": Decimal("0.08"),  # 8% average US sales tax
            "EU": Decimal("0.20"),  # 20% EU VAT
            "UK": Decimal("0.20"),  # 20% UK VAT
            "CA": Decimal("0.13"),  # 13% Canadian tax
            "default": Decimal("0.00"),
        }

        self.logger = logging.getLogger(__name__)

    async def calculate_invoice(
        self,
        subscription: Subscription,
        pricing_tier: PricingTier,
        usage_summary: Dict[UsageMetric, Decimal],
        billing_period_start: datetime,
        billing_period_end: datetime,
        customer_location: str = "US",
    ) -> Dict[str, Any]:
        """Calculate invoice for billing period"""
        try:
            line_items = []
            subtotal = Decimal("0")

            # Base subscription fee
            base_amount = pricing_tier.base_price
            line_items.append(
                {
                    "description": f"{pricing_tier.name} Plan",
                    "quantity": 1,
                    "unit_price": str(base_amount),
                    "total": str(base_amount),
                    "type": "subscription",
                }
            )
            subtotal += base_amount

            # Usage-based charges (overages)
            for metric, quantity in usage_summary.items():
                limit = pricing_tier.usage_limits.get(metric, 0)
                overage_rate = pricing_tier.overage_rates.get(metric, Decimal("0"))

                if quantity > Decimal(str(limit)) and overage_rate > 0:
                    overage_quantity = quantity - Decimal(str(limit))
                    overage_amount = overage_quantity * overage_rate

                    line_items.append(
                        {
                            "description": f"{metric.value.replace('_', ' ').title()} Overage",
                            "quantity": str(overage_quantity),
                            "unit_price": str(overage_rate),
                            "total": str(overage_amount),
                            "type": "overage",
                        }
                    )
                    subtotal += overage_amount

            # Calculate tax
            tax_rate = self.tax_rates.get(customer_location, self.tax_rates["default"])
            tax_amount = (subtotal * tax_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            # Total amount
            total_amount = subtotal + tax_amount

            return {
                "subtotal": str(subtotal),
                "tax_rate": str(tax_rate),
                "tax_amount": str(tax_amount),
                "total_amount": str(total_amount),
                "line_items": line_items,
                "billing_period": {
                    "start": billing_period_start.isoformat(),
                    "end": billing_period_end.isoformat(),
                },
            }

        except Exception as e:
            self.logger.error(f"Invoice calculation failed: {e}")
            raise

    async def calculate_proration(
        self,
        old_plan_price: Decimal,
        new_plan_price: Decimal,
        days_remaining: int,
        total_days: int,
    ) -> Decimal:
        """Calculate prorated amount for plan changes"""
        try:
            if total_days <= 0:
                return Decimal("0")

            # Refund for unused portion of old plan
            old_plan_refund = (old_plan_price * Decimal(str(days_remaining))) / Decimal(
                str(total_days)
            )

            # Charge for new plan for remaining period
            new_plan_charge = (new_plan_price * Decimal(str(days_remaining))) / Decimal(
                str(total_days)
            )

            # Net amount (positive = charge, negative = credit)
            proration_amount = new_plan_charge - old_plan_refund

            return proration_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        except Exception as e:
            self.logger.error(f"Proration calculation failed: {e}")
            return Decimal("0")


class BillingSystem:
    """Comprehensive billing and subscription management system"""

    def __init__(self):
        # Core components
        self.usage_tracker = UsageTracker()
        self.billing_calculator = BillingCalculator()

        # Data storage
        self.customers: Dict[str, Customer] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.pricing_tiers: Dict[str, PricingTier] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.billing_alerts: Dict[str, BillingAlert] = {}

        # Billing metrics
        self.metrics = {
            "total_customers": 0,
            "active_subscriptions": 0,
            "monthly_recurring_revenue": Decimal("0"),
            "invoices_generated": 0,
            "payments_processed": 0,
            "failed_payments": 0,
        }

        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Initialize billing system"""
        try:
            self.logger.info("Initializing Billing System...")

            # Load default pricing tiers
            await self._load_default_pricing_tiers()

            # Initialize billing schedules
            await self._initialize_billing_schedules()

            self.logger.info("Billing System initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Billing System: {e}")
            raise

    async def _load_default_pricing_tiers(self):
        """Load default pricing tiers"""
        try:
            default_tiers = [
                PricingTier(
                    tier_id="free_tier",
                    name="Free",
                    description="Free tier with basic features",
                    base_price=Decimal("0"),
                    usage_limits={
                        UsageMetric.API_CALLS: 1000,
                        UsageMetric.DATA_STORAGE_GB: 1,
                        UsageMetric.AI_REQUESTS: 100,
                        UsageMetric.USERS_ACTIVE: 1,
                        UsageMetric.PROJECTS: 3,
                    },
                    features=[
                        "Basic AI assistance",
                        "1GB storage",
                        "Community support",
                    ],
                ),
                PricingTier(
                    tier_id="basic_tier",
                    name="Basic",
                    description="Basic plan for individuals",
                    base_price=Decimal("29.99"),
                    usage_limits={
                        UsageMetric.API_CALLS: 10000,
                        UsageMetric.DATA_STORAGE_GB: 10,
                        UsageMetric.AI_REQUESTS: 1000,
                        UsageMetric.USERS_ACTIVE: 5,
                        UsageMetric.PROJECTS: 10,
                    },
                    overage_rates={
                        UsageMetric.API_CALLS: Decimal("0.001"),
                        UsageMetric.DATA_STORAGE_GB: Decimal("2.00"),
                        UsageMetric.AI_REQUESTS: Decimal("0.01"),
                    },
                    features=[
                        "Advanced AI assistance",
                        "10GB storage",
                        "Email support",
                        "Basic integrations",
                    ],
                ),
                PricingTier(
                    tier_id="professional_tier",
                    name="Professional",
                    description="Professional plan for teams",
                    base_price=Decimal("99.99"),
                    usage_limits={
                        UsageMetric.API_CALLS: 100000,
                        UsageMetric.DATA_STORAGE_GB: 100,
                        UsageMetric.AI_REQUESTS: 10000,
                        UsageMetric.USERS_ACTIVE: 25,
                        UsageMetric.PROJECTS: 50,
                    },
                    overage_rates={
                        UsageMetric.API_CALLS: Decimal("0.0008"),
                        UsageMetric.DATA_STORAGE_GB: Decimal("1.50"),
                        UsageMetric.AI_REQUESTS: Decimal("0.008"),
                    },
                    features=[
                        "Premium AI assistance",
                        "100GB storage",
                        "Priority support",
                        "Advanced integrations",
                        "Team collaboration",
                        "Analytics dashboard",
                    ],
                ),
                PricingTier(
                    tier_id="enterprise_tier",
                    name="Enterprise",
                    description="Enterprise plan for organizations",
                    base_price=Decimal("499.99"),
                    usage_limits={
                        UsageMetric.API_CALLS: 1000000,
                        UsageMetric.DATA_STORAGE_GB: 1000,
                        UsageMetric.AI_REQUESTS: 100000,
                        UsageMetric.USERS_ACTIVE: 100,
                        UsageMetric.PROJECTS: 200,
                    },
                    overage_rates={
                        UsageMetric.API_CALLS: Decimal("0.0005"),
                        UsageMetric.DATA_STORAGE_GB: Decimal("1.00"),
                        UsageMetric.AI_REQUESTS: Decimal("0.005"),
                    },
                    features=[
                        "Enterprise AI assistance",
                        "1TB storage",
                        "24/7 dedicated support",
                        "Custom integrations",
                        "Advanced security",
                        "Compliance features",
                        "Custom reporting",
                        "SLA guarantee",
                    ],
                ),
            ]

            for tier in default_tiers:
                self.pricing_tiers[tier.tier_id] = tier

            self.logger.info(f"Loaded {len(default_tiers)} pricing tiers")

        except Exception as e:
            self.logger.error(f"Failed to load pricing tiers: {e}")

    async def _initialize_billing_schedules(self):
        """Initialize billing schedules"""
        try:
            # This would set up recurring billing jobs
            self.logger.info("Billing schedules initialized")

        except Exception as e:
            self.logger.error(f"Billing schedule initialization failed: {e}")

    # Customer management
    async def create_customer(
        self,
        name: str,
        email: str,
        company: Optional[str] = None,
        billing_address: Optional[Dict[str, str]] = None,
    ) -> Customer:
        """Create new customer"""
        try:
            customer = Customer(
                customer_id=str(uuid.uuid4()),
                name=name,
                email=email,
                company=company,
                billing_address=billing_address or {},
            )

            self.customers[customer.customer_id] = customer
            self.metrics["total_customers"] += 1

            self.logger.info(f"Customer created: {name} ({email})")
            return customer

        except Exception as e:
            self.logger.error(f"Customer creation failed: {e}")
            raise

    # Subscription management
    async def create_subscription(
        self,
        customer_id: str,
        plan: BillingPlan,
        pricing_tier_id: str,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
    ) -> Subscription:
        """Create new subscription"""
        try:
            if customer_id not in self.customers:
                raise ValueError(f"Customer not found: {customer_id}")

            if pricing_tier_id not in self.pricing_tiers:
                raise ValueError(f"Pricing tier not found: {pricing_tier_id}")

            now = datetime.utcnow()

            # Calculate next billing date
            if billing_cycle == BillingCycle.MONTHLY:
                next_billing_date = now + timedelta(days=30)
            elif billing_cycle == BillingCycle.QUARTERLY:
                next_billing_date = now + timedelta(days=90)
            elif billing_cycle == BillingCycle.ANNUALLY:
                next_billing_date = now + timedelta(days=365)
            else:
                next_billing_date = None

            subscription = Subscription(
                subscription_id=str(uuid.uuid4()),
                customer_id=customer_id,
                plan=plan,
                pricing_tier_id=pricing_tier_id,
                status=SubscriptionStatus.ACTIVE,
                start_date=now,
                next_billing_date=next_billing_date,
                billing_cycle=billing_cycle,
            )

            self.subscriptions[subscription.subscription_id] = subscription
            self.metrics["active_subscriptions"] += 1

            # Update MRR
            pricing_tier = self.pricing_tiers[pricing_tier_id]
            if billing_cycle == BillingCycle.MONTHLY:
                self.metrics["monthly_recurring_revenue"] += pricing_tier.base_price
            elif billing_cycle == BillingCycle.ANNUALLY:
                self.metrics["monthly_recurring_revenue"] += (
                    pricing_tier.base_price / 12
                )

            self.logger.info(f"Subscription created: {customer_id} - {plan.value}")
            return subscription

        except Exception as e:
            self.logger.error(f"Subscription creation failed: {e}")
            raise

    async def change_subscription_plan(
        self, subscription_id: str, new_pricing_tier_id: str
    ) -> bool:
        """Change subscription plan"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                return False

            old_tier = self.pricing_tiers.get(subscription.pricing_tier_id)
            new_tier = self.pricing_tiers.get(new_pricing_tier_id)

            if not old_tier or not new_tier:
                return False

            # Calculate proration
            if subscription.next_billing_date:
                days_remaining = (
                    subscription.next_billing_date - datetime.utcnow()
                ).days
                total_days = 30  # Assuming monthly billing

                proration_amount = await self.billing_calculator.calculate_proration(
                    old_tier.base_price, new_tier.base_price, days_remaining, total_days
                )

                # Create proration invoice if needed
                if proration_amount != Decimal("0"):
                    await self._create_proration_invoice(subscription, proration_amount)

            # Update subscription
            subscription.pricing_tier_id = new_pricing_tier_id

            # Update MRR
            mrr_change = new_tier.base_price - old_tier.base_price
            if subscription.billing_cycle == BillingCycle.MONTHLY:
                self.metrics["monthly_recurring_revenue"] += mrr_change
            elif subscription.billing_cycle == BillingCycle.ANNUALLY:
                self.metrics["monthly_recurring_revenue"] += mrr_change / 12

            self.logger.info(f"Subscription plan changed: {subscription_id}")
            return True

        except Exception as e:
            self.logger.error(f"Subscription plan change failed: {e}")
            return False

    async def _create_proration_invoice(
        self, subscription: Subscription, amount: Decimal
    ):
        """Create proration invoice"""
        try:
            if amount == Decimal("0"):
                return

            now = datetime.utcnow()

            invoice = Invoice(
                invoice_id=str(uuid.uuid4()),
                customer_id=subscription.customer_id,
                subscription_id=subscription.subscription_id,
                invoice_number=f"PRO-{now.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}",
                billing_period_start=now,
                billing_period_end=now,
                issue_date=now,
                due_date=now + timedelta(days=7),
                subtotal=amount,
                tax_amount=Decimal("0"),  # Simplified - no tax on prorations
                total_amount=amount,
                line_items=[
                    {
                        "description": "Plan Change Proration",
                        "quantity": 1,
                        "unit_price": str(amount),
                        "total": str(amount),
                        "type": "proration",
                    }
                ],
            )

            self.invoices[invoice.invoice_id] = invoice
            self.metrics["invoices_generated"] += 1

            self.logger.info(f"Proration invoice created: {invoice.invoice_id}")

        except Exception as e:
            self.logger.error(f"Proration invoice creation failed: {e}")

    # Usage tracking
    async def record_usage(
        self,
        customer_id: str,
        metric: UsageMetric,
        quantity: Decimal,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Record usage for customer"""
        try:
            # Find active subscription
            subscription = None
            for sub in self.subscriptions.values():
                if (
                    sub.customer_id == customer_id
                    and sub.status == SubscriptionStatus.ACTIVE
                ):
                    subscription = sub
                    break

            if not subscription:
                self.logger.warning(
                    f"No active subscription found for customer: {customer_id}"
                )
                return False

            # Record usage
            await self.usage_tracker.record_usage(
                customer_id, subscription.subscription_id, metric, quantity, metadata
            )

            # Check usage limits and send alerts if needed
            pricing_tier = self.pricing_tiers.get(subscription.pricing_tier_id)
            if pricing_tier:
                await self._check_usage_alerts(
                    customer_id, subscription.subscription_id, pricing_tier
                )

            return True

        except Exception as e:
            self.logger.error(f"Usage recording failed: {e}")
            return False

    async def _check_usage_alerts(
        self, customer_id: str, subscription_id: str, pricing_tier: PricingTier
    ):
        """Check usage alerts"""
        try:
            limit_status = await self.usage_tracker.check_usage_limits(
                customer_id, subscription_id, pricing_tier.usage_limits
            )

            # Check for alerts
            for alert in self.billing_alerts.values():
                if (
                    alert.customer_id == customer_id
                    and alert.is_active
                    and alert.alert_type == "usage_threshold"
                ):
                    if alert.threshold_metric:
                        metric_status = limit_status["limits"].get(
                            alert.threshold_metric.value
                        )
                        if metric_status and metric_status["percentage"] >= float(
                            alert.threshold_value or 80
                        ):
                            await self._send_usage_alert(alert, metric_status)

        except Exception as e:
            self.logger.error(f"Usage alert check failed: {e}")

    async def _send_usage_alert(
        self, alert: BillingAlert, metric_status: Dict[str, Any]
    ):
        """Send usage alert"""
        try:
            # This would send actual notifications
            self.logger.warning(
                f"Usage alert triggered: {alert.alert_id} - {metric_status}"
            )

        except Exception as e:
            self.logger.error(f"Usage alert sending failed: {e}")

    # Invoice generation
    async def generate_invoice(
        self,
        subscription_id: str,
        billing_period_start: datetime,
        billing_period_end: datetime,
    ) -> Optional[Invoice]:
        """Generate invoice for subscription"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                return None

            pricing_tier = self.pricing_tiers.get(subscription.pricing_tier_id)
            if not pricing_tier:
                return None

            customer = self.customers.get(subscription.customer_id)
            if not customer:
                return None

            # Get usage summary
            usage_summary = await self.usage_tracker.get_usage_summary(
                subscription.customer_id, billing_period_start, billing_period_end
            )

            # Calculate invoice
            calculation = await self.billing_calculator.calculate_invoice(
                subscription,
                pricing_tier,
                usage_summary,
                billing_period_start,
                billing_period_end,
                customer.billing_address.get("country", "US"),
            )

            # Create invoice
            now = datetime.utcnow()
            invoice = Invoice(
                invoice_id=str(uuid.uuid4()),
                customer_id=subscription.customer_id,
                subscription_id=subscription_id,
                invoice_number=f"INV-{now.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}",
                billing_period_start=billing_period_start,
                billing_period_end=billing_period_end,
                issue_date=now,
                due_date=now + timedelta(days=30),
                subtotal=Decimal(calculation["subtotal"]),
                tax_amount=Decimal(calculation["tax_amount"]),
                total_amount=Decimal(calculation["total_amount"]),
                line_items=calculation["line_items"],
            )

            self.invoices[invoice.invoice_id] = invoice
            self.metrics["invoices_generated"] += 1

            self.logger.info(f"Invoice generated: {invoice.invoice_number}")
            return invoice

        except Exception as e:
            self.logger.error(f"Invoice generation failed: {e}")
            return None

    async def process_payment(
        self, invoice_id: str, payment_method: str = "card"
    ) -> bool:
        """Process payment for invoice"""
        try:
            invoice = self.invoices.get(invoice_id)
            if not invoice:
                return False

            # Mock payment processing
            # In real implementation, this would integrate with payment processors
            payment_successful = True  # Simulate successful payment

            if payment_successful:
                invoice.status = PaymentStatus.PAID
                invoice.payment_method = payment_method
                invoice.paid_date = datetime.utcnow()

                self.metrics["payments_processed"] += 1

                self.logger.info(f"Payment processed: {invoice.invoice_number}")
                return True
            else:
                invoice.status = PaymentStatus.FAILED
                self.metrics["failed_payments"] += 1

                self.logger.error(f"Payment failed: {invoice.invoice_number}")
                return False

        except Exception as e:
            self.logger.error(f"Payment processing failed: {e}")
            return False

    # Billing alerts
    async def create_billing_alert(
        self,
        customer_id: str,
        alert_type: str,
        threshold_value: Optional[Decimal] = None,
        threshold_metric: Optional[UsageMetric] = None,
        notification_channels: Optional[List[str]] = None,
    ) -> BillingAlert:
        """Create billing alert"""
        try:
            alert = BillingAlert(
                alert_id=str(uuid.uuid4()),
                customer_id=customer_id,
                alert_type=alert_type,
                threshold_value=threshold_value,
                threshold_metric=threshold_metric,
                notification_channels=notification_channels or ["email"],
            )

            self.billing_alerts[alert.alert_id] = alert

            self.logger.info(f"Billing alert created: {alert_type} for {customer_id}")
            return alert

        except Exception as e:
            self.logger.error(f"Billing alert creation failed: {e}")
            raise

    # Reporting and analytics
    async def get_billing_metrics(self) -> Dict[str, Any]:
        """Get comprehensive billing metrics"""
        try:
            now = datetime.utcnow()

            # Revenue metrics
            total_revenue = sum(
                Decimal(invoice.total_amount)
                for invoice in self.invoices.values()
                if invoice.status == PaymentStatus.PAID
            )

            # Subscription metrics
            subscription_status_distribution = Counter(
                sub.status for sub in self.subscriptions.values()
            )

            plan_distribution = Counter(sub.plan for sub in self.subscriptions.values())

            # Recent activity
            recent_invoices = len(
                [
                    inv
                    for inv in self.invoices.values()
                    if inv.issue_date > now - timedelta(days=30)
                ]
            )

            recent_payments = len(
                [
                    inv
                    for inv in self.invoices.values()
                    if inv.paid_date and inv.paid_date > now - timedelta(days=30)
                ]
            )

            return {
                "revenue": {
                    "total_revenue": str(total_revenue),
                    "monthly_recurring_revenue": str(
                        self.metrics["monthly_recurring_revenue"]
                    ),
                    "average_revenue_per_user": str(
                        total_revenue / len(self.customers)
                        if self.customers
                        else Decimal("0")
                    ),
                },
                "customers": {
                    "total": len(self.customers),
                    "with_active_subscriptions": len(
                        [
                            sub
                            for sub in self.subscriptions.values()
                            if sub.status == SubscriptionStatus.ACTIVE
                        ]
                    ),
                },
                "subscriptions": {
                    "total": len(self.subscriptions),
                    "active": self.metrics["active_subscriptions"],
                    "status_distribution": {
                        status.value: count
                        for status, count in subscription_status_distribution.items()
                    },
                    "plan_distribution": {
                        plan.value: count for plan, count in plan_distribution.items()
                    },
                },
                "invoices": {
                    "total": len(self.invoices),
                    "recent_30_days": recent_invoices,
                    "payments_processed": self.metrics["payments_processed"],
                    "failed_payments": self.metrics["failed_payments"],
                    "recent_payments_30_days": recent_payments,
                },
                "usage": {"total_usage_records": len(self.usage_tracker.usage_records)},
                "metrics": {
                    k: str(v) if isinstance(v, Decimal) else v
                    for k, v in self.metrics.items()
                },
                "metrics_timestamp": now.isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Failed to get billing metrics: {e}")
            return {}

    async def get_customer_billing_summary(self, customer_id: str) -> Dict[str, Any]:
        """Get billing summary for customer"""
        try:
            customer = self.customers.get(customer_id)
            if not customer:
                return {}

            # Get customer subscriptions
            customer_subscriptions = [
                sub
                for sub in self.subscriptions.values()
                if sub.customer_id == customer_id
            ]

            # Get customer invoices
            customer_invoices = [
                inv for inv in self.invoices.values() if inv.customer_id == customer_id
            ]

            # Calculate totals
            total_paid = sum(
                Decimal(inv.total_amount)
                for inv in customer_invoices
                if inv.status == PaymentStatus.PAID
            )

            outstanding_balance = sum(
                Decimal(inv.total_amount)
                for inv in customer_invoices
                if inv.status == PaymentStatus.PENDING
            )

            return {
                "customer": customer.to_dict(),
                "subscriptions": [sub.to_dict() for sub in customer_subscriptions],
                "invoices": [
                    inv.to_dict() for inv in customer_invoices[-10:]
                ],  # Last 10 invoices
                "financial_summary": {
                    "total_paid": str(total_paid),
                    "outstanding_balance": str(outstanding_balance),
                    "invoice_count": len(customer_invoices),
                },
            }

        except Exception as e:
            self.logger.error(f"Customer billing summary failed: {e}")
            return {}
