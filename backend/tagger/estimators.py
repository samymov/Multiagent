"""
Estimator Integration Layer for Goal Planner Agent.
Connects identified intents to relevant existing estimators.
"""

from typing import Dict, Any, Optional
import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)


class EstimatorIntegration:
    """Interface to existing estimators in the codebase."""
    
    def __init__(self, portfolio_data: Optional[Dict[str, Any]] = None, 
                 user_data: Optional[Dict[str, Any]] = None):
        """
        Initialize estimator integration.
        
        Args:
            portfolio_data: User's portfolio data (accounts, positions, instruments)
            user_data: User profile data (age, retirement goals, etc.)
        """
        self.portfolio_data = portfolio_data or {}
        self.user_data = user_data or {}
    
    def calculate_portfolio_value(self) -> float:
        """Calculate current portfolio value (from retirement agent)."""
        total_value = 0.0
        
        for account in self.portfolio_data.get("accounts", []):
            cash_balance = account.get("cash_balance") or 0
            cash = float(cash_balance)
            total_value += cash
            
            for position in account.get("positions", []):
                quantity_val = position.get("quantity") or 0
                quantity = float(quantity_val)
                instrument = position.get("instrument", {})
                price_val = instrument.get("current_price") or 100
                price = float(price_val)
                total_value += quantity * price
        
        return total_value
    
    def calculate_asset_allocation(self) -> Dict[str, float]:
        """Calculate asset allocation percentages (from retirement agent)."""
        total_equity = 0.0
        total_bonds = 0.0
        total_real_estate = 0.0
        total_commodities = 0.0
        total_cash = 0.0
        total_value = 0.0
        
        for account in self.portfolio_data.get("accounts", []):
            cash_balance = account.get("cash_balance") or 0
            cash = float(cash_balance)
            total_cash += cash
            total_value += cash
            
            for position in account.get("positions", []):
                quantity_val = position.get("quantity") or 0
                quantity = float(quantity_val)
                instrument = position.get("instrument", {})
                price_val = instrument.get("current_price") or 100
                price = float(price_val)
                value = quantity * price
                total_value += value
                
                asset_allocation = instrument.get("allocation_asset_class", {})
                if asset_allocation:
                    total_equity += value * asset_allocation.get("equity", 0) / 100
                    total_bonds += value * asset_allocation.get("fixed_income", 0) / 100
                    total_real_estate += value * asset_allocation.get("real_estate", 0) / 100
                    total_commodities += value * asset_allocation.get("commodities", 0) / 100
        
        if total_value == 0:
            return {"equity": 0, "bonds": 0, "real_estate": 0, "commodities": 0, "cash": 0}
        
        return {
            "equity": total_equity / total_value,
            "bonds": total_bonds / total_value,
            "real_estate": total_real_estate / total_value,
            "commodities": total_commodities / total_value,
            "cash": total_cash / total_value,
        }
    
    def estimate_retirement_readiness(self) -> Dict[str, Any]:
        """
        Estimate retirement readiness (leverages retirement agent logic).
        
        Returns:
            Dictionary with retirement readiness metrics
        """
        portfolio_value = self.calculate_portfolio_value()
        allocation = self.calculate_asset_allocation()
        
        years_until_retirement = self.user_data.get("years_until_retirement", 30)
        target_income = float(self.user_data.get("target_retirement_income", 80000) or 80000)
        current_age = self.user_data.get("current_age", 40)
        
        # Calculate expected portfolio value at retirement
        expected_return = (
            allocation["equity"] * 0.07
            + allocation["bonds"] * 0.04
            + allocation["real_estate"] * 0.06
            + allocation["cash"] * 0.02
        )
        
        expected_value_at_retirement = portfolio_value
        annual_contribution = 10000  # Default assumption
        
        for _ in range(years_until_retirement):
            expected_value_at_retirement *= 1 + expected_return
            expected_value_at_retirement += annual_contribution
        
        # Calculate projected annual income (4% rule)
        projected_annual_income = expected_value_at_retirement * 0.04
        
        # Calculate gap
        income_gap = target_income - projected_annual_income
        
        # Calculate required contribution to meet goal
        required_contribution = self._calculate_required_contribution(
            portfolio_value,
            years_until_retirement,
            target_income,
            expected_return
        )
        
        return {
            "current_portfolio_value": portfolio_value,
            "expected_value_at_retirement": expected_value_at_retirement,
            "projected_annual_income": projected_annual_income,
            "target_annual_income": target_income,
            "income_gap": income_gap,
            "years_until_retirement": years_until_retirement,
            "current_annual_contribution": annual_contribution,
            "required_annual_contribution": required_contribution,
            "on_track": income_gap <= 0,
            "success_probability": self._estimate_success_probability(
                portfolio_value,
                years_until_retirement,
                target_income,
                allocation
            )
        }
    
    def estimate_401k_contribution_adequacy(self) -> Dict[str, Any]:
        """
        Estimate if 401k contributions are adequate.
        
        Returns:
            Dictionary with contribution analysis
        """
        # Get 401k account data
        accounts = self.portfolio_data.get("accounts", [])
        retirement_accounts = [
            acc for acc in accounts 
            if "401" in acc.get("account_name", "").upper() or 
               "retirement" in acc.get("account_name", "").lower()
        ]
        
        # Estimate current contribution (would need actual contribution data)
        # For now, use portfolio growth as proxy
        portfolio_value = self.calculate_portfolio_value()
        years_until_retirement = self.user_data.get("years_until_retirement", 30)
        current_age = self.user_data.get("current_age", 40)
        
        # Standard recommendation: 15% of income or max contribution
        # 2024 401k limit: $23,000 (under 50), $30,500 (50+)
        age_50_plus = current_age >= 50
        max_contribution = 30500 if age_50_plus else 23000
        
        # Estimate current contribution based on portfolio value
        # Rough estimate: assume 10 years of contributions
        estimated_current_contribution = portfolio_value / 10 if years_until_retirement > 10 else portfolio_value / years_until_retirement
        
        recommended_contribution = max(max_contribution * 0.8, estimated_current_contribution * 1.2)
        
        return {
            "current_estimated_contribution": estimated_current_contribution,
            "recommended_contribution": recommended_contribution,
            "max_contribution_limit": max_contribution,
            "is_contributing_enough": estimated_current_contribution >= recommended_contribution,
            "gap": recommended_contribution - estimated_current_contribution,
            "percentage_of_max": (estimated_current_contribution / max_contribution) * 100 if max_contribution > 0 else 0
        }
    
    def estimate_hsa_contribution(self) -> Dict[str, Any]:
        """
        Estimate optimal HSA contribution.
        
        Returns:
            Dictionary with HSA contribution recommendations
        """
        # 2024 HSA limits: $4,150 (individual), $8,300 (family)
        # Assume individual for now (would need user data)
        max_hsa_contribution = 4150
        
        # Check if user has HSA account
        accounts = self.portfolio_data.get("accounts", [])
        hsa_accounts = [
            acc for acc in accounts 
            if "hsa" in acc.get("account_name", "").lower() or
               "health savings" in acc.get("account_name", "").lower()
        ]
        
        has_hsa = len(hsa_accounts) > 0
        
        # Recommended: max out HSA if possible
        recommended_contribution = max_hsa_contribution
        
        return {
            "has_hsa_account": has_hsa,
            "max_contribution_limit": max_hsa_contribution,
            "recommended_contribution": recommended_contribution,
            "reason": "HSAs offer triple tax advantage: pre-tax contributions, tax-free growth, and tax-free withdrawals for qualified medical expenses"
        }
    
    def estimate_savings_optimization(self) -> Dict[str, Any]:
        """
        Estimate how to save more for retirement.
        
        Returns:
            Dictionary with savings optimization recommendations
        """
        retirement_readiness = self.estimate_retirement_readiness()
        
        current_contribution = retirement_readiness["current_annual_contribution"]
        required_contribution = retirement_readiness["required_annual_contribution"]
        
        contribution_gap = required_contribution - current_contribution
        
        # Calculate potential increases
        increase_10_percent = current_contribution * 1.1
        increase_20_percent = current_contribution * 1.2
        
        return {
            "current_annual_contribution": current_contribution,
            "required_annual_contribution": required_contribution,
            "contribution_gap": contribution_gap,
            "recommended_increase": max(contribution_gap, current_contribution * 0.1),
            "increase_10_percent": increase_10_percent,
            "increase_20_percent": increase_20_percent,
            "strategies": [
                "Increase 401k contribution by 1-2% annually",
                "Maximize employer match if available",
                "Consider opening or increasing IRA contributions",
                "Automate savings increases with each raise"
            ]
        }
    
    def _calculate_required_contribution(
        self, 
        current_value: float,
        years: int,
        target_income: float,
        expected_return: float
    ) -> float:
        """Calculate required annual contribution to meet retirement goal."""
        # Target portfolio value needed (4% rule)
        target_portfolio_value = target_income / 0.04
        
        # Calculate required contribution using future value of annuity formula
        # FV = PV * (1+r)^n + PMT * [((1+r)^n - 1) / r]
        # Solving for PMT: PMT = (FV - PV*(1+r)^n) / [((1+r)^n - 1) / r]
        
        future_value_factor = (1 + expected_return) ** years
        annuity_factor = ((1 + expected_return) ** years - 1) / expected_return
        
        required_contribution = (target_portfolio_value - current_value * future_value_factor) / annuity_factor
        
        return max(0, required_contribution)
    
    def _estimate_success_probability(
        self,
        current_value: float,
        years: int,
        target_income: float,
        allocation: Dict[str, float]
    ) -> float:
        """Estimate success probability using simplified Monte Carlo logic."""
        # Simplified version - full version would use retirement agent's Monte Carlo
        expected_return = (
            allocation["equity"] * 0.07
            + allocation["bonds"] * 0.04
            + allocation["real_estate"] * 0.06
            + allocation["cash"] * 0.02
        )
        
        target_portfolio_value = target_income / 0.04
        expected_value = current_value * ((1 + expected_return) ** years)
        
        # Rough probability estimate based on expected value vs target
        if expected_value >= target_portfolio_value:
            return 85.0  # High probability if on track
        elif expected_value >= target_portfolio_value * 0.8:
            return 60.0  # Moderate probability
        elif expected_value >= target_portfolio_value * 0.6:
            return 40.0  # Lower probability
        else:
            return 20.0  # Low probability

