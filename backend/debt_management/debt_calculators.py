"""
Debt Calculation Functions for Debt Management Agent.
Provides calculations for debt payoff strategies, interest savings, and timelines.
"""

from typing import Dict, Any, List, Optional
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class DebtCalculator:
    """Calculates debt payoff strategies and savings."""
    
    @staticmethod
    def calculate_debt_avalanche(
        debts: List[Dict[str, Any]],
        monthly_payment: float
    ) -> Dict[str, Any]:
        """
        Calculate debt avalanche payoff strategy.
        Prioritizes highest interest rate debts first.
        
        Args:
            debts: List of debt dicts with keys: name, balance, interest_rate, minimum_payment
            monthly_payment: Total monthly amount available for debt repayment
            
        Returns:
            Dictionary with payoff plan, total interest, and timeline
        """
        # Sort by interest rate (highest first)
        sorted_debts = sorted(debts, key=lambda x: x.get("interest_rate", 0), reverse=True)
        
        payoff_plan = []
        total_interest = 0.0
        months_to_payoff = 0
        remaining_balance = {d["name"]: d["balance"] for d in debts}
        current_month = 0
        
        while any(balance > 0 for balance in remaining_balance.values()):
            current_month += 1
            available_payment = monthly_payment
            
            # Pay minimums on all debts
            for debt in sorted_debts:
                name = debt["name"]
                if remaining_balance[name] > 0:
                    min_payment = debt.get("minimum_payment", 0)
                    payment = min(min_payment, remaining_balance[name])
                    remaining_balance[name] -= payment
                    available_payment -= payment
            
            # Apply extra to highest interest debt
            for debt in sorted_debts:
                name = debt["name"]
                interest_rate = debt.get("interest_rate", 0) / 100 / 12  # Monthly rate
                
                if remaining_balance[name] > 0 and available_payment > 0:
                    # Add interest
                    interest = remaining_balance[name] * interest_rate
                    total_interest += interest
                    remaining_balance[name] += interest
                    
                    # Apply extra payment
                    extra_payment = min(available_payment, remaining_balance[name])
                    remaining_balance[name] -= extra_payment
                    available_payment -= extra_payment
                    
                    if remaining_balance[name] <= 0:
                        payoff_plan.append({
                            "debt": name,
                            "month_paid_off": current_month,
                            "total_paid": debt["balance"] + sum(
                                d.get("interest_paid", 0) for d in payoff_plan if d.get("debt") == name
                            )
                        })
        
        months_to_payoff = current_month
        
        return {
            "strategy": "debt_avalanche",
            "payoff_order": [d["name"] for d in sorted_debts],
            "total_interest": total_interest,
            "months_to_payoff": months_to_payoff,
            "total_paid": sum(d["balance"] for d in debts) + total_interest,
            "payoff_plan": payoff_plan
        }
    
    @staticmethod
    def calculate_debt_snowball(
        debts: List[Dict[str, Any]],
        monthly_payment: float
    ) -> Dict[str, Any]:
        """
        Calculate debt snowball payoff strategy.
        Prioritizes smallest balance debts first for psychological wins.
        
        Args:
            debts: List of debt dicts
            monthly_payment: Total monthly amount available
            
        Returns:
            Dictionary with payoff plan, total interest, and timeline
        """
        # Sort by balance (smallest first)
        sorted_debts = sorted(debts, key=lambda x: x.get("balance", 0))
        
        payoff_plan = []
        total_interest = 0.0
        months_to_payoff = 0
        remaining_balance = {d["name"]: d["balance"] for d in debts}
        current_month = 0
        
        while any(balance > 0 for balance in remaining_balance.values()):
            current_month += 1
            available_payment = monthly_payment
            
            # Pay minimums on all debts
            for debt in sorted_debts:
                name = debt["name"]
                if remaining_balance[name] > 0:
                    min_payment = debt.get("minimum_payment", 0)
                    payment = min(min_payment, remaining_balance[name])
                    remaining_balance[name] -= payment
                    available_payment -= payment
            
            # Apply extra to smallest debt
            for debt in sorted_debts:
                name = debt["name"]
                interest_rate = debt.get("interest_rate", 0) / 100 / 12
                
                if remaining_balance[name] > 0 and available_payment > 0:
                    # Add interest
                    interest = remaining_balance[name] * interest_rate
                    total_interest += interest
                    remaining_balance[name] += interest
                    
                    # Apply extra payment
                    extra_payment = min(available_payment, remaining_balance[name])
                    remaining_balance[name] -= extra_payment
                    available_payment -= extra_payment
                    
                    if remaining_balance[name] <= 0:
                        payoff_plan.append({
                            "debt": name,
                            "month_paid_off": current_month,
                            "total_paid": debt["balance"] + sum(
                                d.get("interest_paid", 0) for d in payoff_plan if d.get("debt") == name
                            )
                        })
        
        months_to_payoff = current_month
        
        return {
            "strategy": "debt_snowball",
            "payoff_order": [d["name"] for d in sorted_debts],
            "total_interest": total_interest,
            "months_to_payoff": months_to_payoff,
            "total_paid": sum(d["balance"] for d in debts) + total_interest,
            "payoff_plan": payoff_plan
        }
    
    @staticmethod
    def compare_strategies(
        debts: List[Dict[str, Any]],
        monthly_payment: float
    ) -> Dict[str, Any]:
        """
        Compare avalanche vs snowball strategies.
        
        Returns:
            Comparison with savings difference and recommendation
        """
        avalanche = DebtCalculator.calculate_debt_avalanche(debts, monthly_payment)
        snowball = DebtCalculator.calculate_debt_snowball(debts, monthly_payment)
        
        interest_difference = snowball["total_interest"] - avalanche["total_interest"]
        time_difference = snowball["months_to_payoff"] - avalanche["months_to_payoff"]
        
        # Determine recommendation
        max_interest_rate = max(d.get("interest_rate", 0) for d in debts)
        min_interest_rate = min(d.get("interest_rate", 0) for d in debts)
        interest_spread = max_interest_rate - min_interest_rate
        
        if interest_spread > 3:  # Significant difference
            recommended = "avalanche"
            reason = f"Interest rates vary significantly ({interest_spread:.1f}%), so Avalanche saves ${interest_difference:,.2f} in interest."
        else:
            recommended = "snowball"
            reason = "Interest rates are similar, so Snowball provides psychological wins and faster momentum."
        
        return {
            "avalanche": avalanche,
            "snowball": snowball,
            "interest_savings": interest_difference,
            "time_difference": time_difference,
            "recommended_strategy": recommended,
            "recommendation_reason": reason
        }
    
    @staticmethod
    def calculate_student_loan_payment(
        principal: float,
        interest_rate: float,
        years: int
    ) -> float:
        """Calculate monthly student loan payment using standard amortization."""
        monthly_rate = interest_rate / 100 / 12
        num_payments = years * 12
        
        if monthly_rate == 0:
            return principal / num_payments
        
        payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                  ((1 + monthly_rate) ** num_payments - 1)
        
        return payment
    
    @staticmethod
    def calculate_idr_payment(
        discretionary_income: float,
        plan_type: str = "SAVE"
    ) -> float:
        """
        Calculate Income-Driven Repayment plan payment.
        
        Args:
            discretionary_income: AGI - 150% of poverty line (or 225% for SAVE)
            plan_type: SAVE, PAYE, IBR, REPAYE
            
        Returns:
            Monthly payment amount
        """
        # SAVE: 10% of discretionary income (5% for undergraduate loans)
        # PAYE/IBR: 10% of discretionary income
        # REPAYE: 10% of discretionary income
        
        if plan_type == "SAVE":
            percentage = 0.10  # 10% for graduate, 5% for undergraduate (simplified)
        else:
            percentage = 0.10
        
        return discretionary_income * percentage / 12
    
    @staticmethod
    def calculate_budget_50_30_20(
        monthly_income: float
    ) -> Dict[str, float]:
        """Calculate 50/30/20 budget allocation."""
        return {
            "needs": monthly_income * 0.50,
            "wants": monthly_income * 0.30,
            "savings_debt": monthly_income * 0.20
        }
    
    @staticmethod
    def calculate_zero_based_budget(
        monthly_income: float,
        expenses: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate zero-based budget.
        
        Args:
            monthly_income: Total monthly income
            expenses: Dictionary of expense categories and amounts
            
        Returns:
            Budget allocation with remaining amount
        """
        total_expenses = sum(expenses.values())
        remaining = monthly_income - total_expenses
        
        return {
            "total_income": monthly_income,
            "allocated_expenses": expenses,
            "total_allocated": total_expenses,
            "remaining": remaining,
            "is_balanced": abs(remaining) < 0.01
        }

