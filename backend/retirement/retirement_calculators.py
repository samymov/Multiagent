"""
Retirement Calculation Functions for Retirement Planning Agent.
Provides calculations for retirement readiness, income projections, and planning scenarios.
"""

from typing import Dict, Any, Optional
import logging
import random

logger = logging.getLogger(__name__)


class RetirementCalculator:
    """Calculates retirement planning metrics and projections."""
    
    @staticmethod
    def calculate_portfolio_value(portfolio_data: Dict[str, Any]) -> float:
        """Calculate current portfolio value."""
        total_value = 0.0
        
        for account in portfolio_data.get("accounts", []):
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
    
    @staticmethod
    def calculate_asset_allocation(portfolio_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate asset allocation percentages."""
        total_equity = 0.0
        total_bonds = 0.0
        total_real_estate = 0.0
        total_commodities = 0.0
        total_cash = 0.0
        total_value = 0.0
        
        for account in portfolio_data.get("accounts", []):
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
    
    @staticmethod
    def run_monte_carlo_simulation(
        current_value: float,
        years_until_retirement: int,
        target_annual_income: float,
        asset_allocation: Dict[str, float],
        annual_contribution: float = 10000,
        num_simulations: int = 500,
    ) -> Dict[str, Any]:
        """Run Monte Carlo simulation for retirement planning."""
        
        # Historical return parameters (annualized)
        equity_return_mean = 0.07
        equity_return_std = 0.18
        bond_return_mean = 0.04
        bond_return_std = 0.05
        real_estate_return_mean = 0.06
        real_estate_return_std = 0.12
        
        successful_scenarios = 0
        final_values = []
        years_lasted = []
        
        for _ in range(num_simulations):
            portfolio_value = current_value
            
            # Accumulation phase
            for _ in range(years_until_retirement):
                equity_return = random.gauss(equity_return_mean, equity_return_std)
                bond_return = random.gauss(bond_return_mean, bond_return_std)
                real_estate_return = random.gauss(real_estate_return_mean, real_estate_return_std)
                
                portfolio_return = (
                    asset_allocation["equity"] * equity_return
                    + asset_allocation["bonds"] * bond_return
                    + asset_allocation["real_estate"] * real_estate_return
                    + asset_allocation["cash"] * 0.02
                )
                
                portfolio_value = portfolio_value * (1 + portfolio_return)
                portfolio_value += annual_contribution
            
            # Retirement phase
            retirement_years = 30
            annual_withdrawal = target_annual_income
            years_income_lasted = 0
            
            for year in range(retirement_years):
                if portfolio_value <= 0:
                    break
                
                # Inflation adjustment (3% per year)
                annual_withdrawal *= 1.03
                
                equity_return = random.gauss(equity_return_mean, equity_return_std)
                bond_return = random.gauss(bond_return_mean, bond_return_std)
                real_estate_return = random.gauss(real_estate_return_mean, real_estate_return_std)
                
                portfolio_return = (
                    asset_allocation["equity"] * equity_return
                    + asset_allocation["bonds"] * bond_return
                    + asset_allocation["real_estate"] * real_estate_return
                    + asset_allocation["cash"] * 0.02
                )
                
                portfolio_value = portfolio_value * (1 + portfolio_return) - annual_withdrawal
                
                if portfolio_value > 0:
                    years_income_lasted += 1
            
            final_values.append(max(0, portfolio_value))
            years_lasted.append(years_income_lasted)
            
            if years_income_lasted >= retirement_years:
                successful_scenarios += 1
        
        # Calculate statistics
        final_values.sort()
        success_rate = (successful_scenarios / num_simulations) * 100
        
        # Calculate expected value at retirement
        expected_return = (
            asset_allocation["equity"] * equity_return_mean
            + asset_allocation["bonds"] * bond_return_mean
            + asset_allocation["real_estate"] * real_estate_return_mean
            + asset_allocation["cash"] * 0.02
        )
        expected_value_at_retirement = current_value
        for _ in range(years_until_retirement):
            expected_value_at_retirement *= 1 + expected_return
            expected_value_at_retirement += annual_contribution
        
        return {
            "success_rate": round(success_rate, 1),
            "median_final_value": round(final_values[num_simulations // 2], 2),
            "percentile_10": round(final_values[num_simulations // 10], 2),
            "percentile_90": round(final_values[9 * num_simulations // 10], 2),
            "average_years_lasted": round(sum(years_lasted) / len(years_lasted), 1),
            "expected_value_at_retirement": round(expected_value_at_retirement, 2),
        }
    
    @staticmethod
    def calculate_retirement_readiness(
        current_value: float,
        years_until_retirement: int,
        target_annual_income: float,
        asset_allocation: Dict[str, float],
        annual_contribution: float = 10000,
        social_security_benefit: float = 0,
        pension_income: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive retirement readiness assessment.
        
        Args:
            current_value: Current portfolio value
            years_until_retirement: Years until retirement
            target_annual_income: Target annual income in retirement
            asset_allocation: Asset allocation percentages
            annual_contribution: Annual contribution amount
            social_security_benefit: Expected Social Security benefit
            pension_income: Expected pension income
            
        Returns:
            Dictionary with retirement readiness metrics
        """
        # Calculate expected portfolio value at retirement
        expected_return = (
            asset_allocation["equity"] * 0.07
            + asset_allocation["bonds"] * 0.04
            + asset_allocation["real_estate"] * 0.06
            + asset_allocation["cash"] * 0.02
        )
        
        expected_value_at_retirement = current_value
        for _ in range(years_until_retirement):
            expected_value_at_retirement *= 1 + expected_return
            expected_value_at_retirement += annual_contribution
        
        # Calculate income from portfolio (4% rule)
        portfolio_income = expected_value_at_retirement * 0.04
        
        # Total retirement income
        total_retirement_income = portfolio_income + social_security_benefit + pension_income
        
        # Income gap
        income_gap = target_annual_income - total_retirement_income
        
        # Calculate required portfolio value to meet goal
        required_portfolio_income = target_annual_income - social_security_benefit - pension_income
        required_portfolio_value = required_portfolio_income / 0.04 if required_portfolio_income > 0 else 0
        
        # Calculate required annual contribution to meet goal
        required_contribution = RetirementCalculator._calculate_required_contribution(
            current_value,
            years_until_retirement,
            required_portfolio_value,
            expected_return
        )
        
        # Run Monte Carlo for success probability
        monte_carlo = RetirementCalculator.run_monte_carlo_simulation(
            current_value,
            years_until_retirement,
            target_annual_income,
            asset_allocation,
            annual_contribution
        )
        
        return {
            "current_portfolio_value": current_value,
            "expected_value_at_retirement": expected_value_at_retirement,
            "portfolio_income": portfolio_income,
            "social_security_benefit": social_security_benefit,
            "pension_income": pension_income,
            "total_retirement_income": total_retirement_income,
            "target_annual_income": target_annual_income,
            "income_gap": income_gap,
            "required_portfolio_value": required_portfolio_value,
            "current_annual_contribution": annual_contribution,
            "required_annual_contribution": required_contribution,
            "on_track": income_gap <= 0,
            "success_probability": monte_carlo["success_rate"],
            "years_until_retirement": years_until_retirement
        }
    
    @staticmethod
    def calculate_social_security_benefit(
        current_age: int,
        full_retirement_age: int = 67,
        estimated_benefit_at_fra: float = 0,
        claiming_age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate Social Security benefit based on claiming age.
        
        Args:
            current_age: Current age
            full_retirement_age: Full retirement age (typically 67)
            estimated_benefit_at_fra: Estimated benefit at full retirement age
            claiming_age: Age at which to claim (if None, uses FRA)
            
        Returns:
            Dictionary with benefit calculations
        """
        if claiming_age is None:
            claiming_age = full_retirement_age
        
        # Calculate reduction/increase based on claiming age
        if claiming_age < full_retirement_age:
            # Early claiming reduction: ~6.67% per year before FRA (up to 36 months), then ~5% per year
            months_before_fra = (full_retirement_age - claiming_age) * 12
            if months_before_fra <= 36:
                reduction = months_before_fra * (6.67 / 12) / 100
            else:
                reduction = (36 * 6.67 / 12 + (months_before_fra - 36) * 5 / 12) / 100
            benefit = estimated_benefit_at_fra * (1 - reduction)
        elif claiming_age > full_retirement_age:
            # Delayed claiming increase: ~8% per year after FRA (up to age 70)
            years_after_fra = min(claiming_age - full_retirement_age, 70 - full_retirement_age)
            increase = years_after_fra * 0.08
            benefit = estimated_benefit_at_fra * (1 + increase)
        else:
            benefit = estimated_benefit_at_fra
        
        return {
            "claiming_age": claiming_age,
            "full_retirement_age": full_retirement_age,
            "benefit_at_fra": estimated_benefit_at_fra,
            "benefit_at_claiming_age": benefit,
            "monthly_benefit": benefit / 12,
            "annual_benefit": benefit
        }
    
    @staticmethod
    def calculate_rmd(
        account_balance: float,
        age: int
    ) -> float:
        """
        Calculate Required Minimum Distribution (RMD) for traditional IRAs and 401(k)s.
        
        Args:
            account_balance: Account balance at end of previous year
            age: Age at end of current year
            
        Returns:
            RMD amount
        """
        # IRS Uniform Lifetime Table divisors (simplified)
        # For ages 72-115, using approximate divisors
        rmd_divisors = {
            72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6,
            76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1,
            80: 20.2, 81: 19.3, 82: 18.4, 83: 17.5,
            84: 16.6, 85: 15.8, 90: 12.7, 95: 9.6,
            100: 6.3, 105: 4.1, 110: 2.5, 115: 1.9
        }
        
        if age < 72:
            return 0.0  # No RMD required before age 72
        
        # Find closest divisor
        divisor = rmd_divisors.get(age)
        if divisor is None:
            # Interpolate for ages not in table
            if age < 85:
                divisor = 27.4 - (age - 72) * 0.8
            elif age < 100:
                divisor = 15.8 - (age - 85) * 0.3
            else:
                divisor = 6.3 - (age - 100) * 0.15
        
        return account_balance / divisor
    
    @staticmethod
    def calculate_safe_withdrawal_rate(
        portfolio_value: float,
        withdrawal_rate: float = 0.04
    ) -> Dict[str, Any]:
        """
        Calculate safe withdrawal rate analysis.
        
        Args:
            portfolio_value: Current portfolio value
            withdrawal_rate: Withdrawal rate (default 4%)
            
        Returns:
            Dictionary with withdrawal analysis
        """
        initial_withdrawal = portfolio_value * withdrawal_rate
        
        return {
            "portfolio_value": portfolio_value,
            "withdrawal_rate": withdrawal_rate,
            "initial_annual_withdrawal": initial_withdrawal,
            "initial_monthly_withdrawal": initial_withdrawal / 12,
            "note": "4% rule assumes 30-year retirement, adjust for longer retirements"
        }
    
    @staticmethod
    def _calculate_required_contribution(
        current_value: float,
        years: int,
        target_value: float,
        expected_return: float
    ) -> float:
        """Calculate required annual contribution to reach target value."""
        future_value_factor = (1 + expected_return) ** years
        annuity_factor = ((1 + expected_return) ** years - 1) / expected_return if expected_return > 0 else years
        
        required_contribution = (target_value - current_value * future_value_factor) / annuity_factor
        
        return max(0, required_contribution)

