# -*- coding: utf-8 -*-
"""
OpenClaw GenPark Marketing - Hill Adstock Saturation Curve & KKT Multi-Channel Budget Allocator
Standard Library only: math, typing.
Calculates geometric adstock carryover with non-linear Hill saturation curves, solves KKT
first-order conditions for multi-channel budget allocation, and computes Cox churn hazards.
"""

import math
from typing import Dict, List, Any

class OpenClawGenParkMarketing:
    def __init__(self):
        pass

    def compute_hill_adstock_saturation(self, spend_series: List[float],
                                        half_saturation_k: float = 1000.0,
                                        hill_exponent_n: float = 1.5,
                                        retention_rate_alpha: float = 0.5,
                                        max_volume_v: float = 100.0) -> Dict[str, Any]:
        """
        Calculates geometric adstock decay and Hill saturation response:
        Adstock: y_t = spend_t + alpha * y_{t-1}
        Hill Response: R(y) = V * (y^n) / (K^n + y^n)
        """
        alpha = max(0.0, min(0.99, retention_rate_alpha))
        K = max(1.0, half_saturation_k)
        n = max(0.1, hill_exponent_n)
        V = max(1.0, max_volume_v)

        adstock_series = []
        response_series = []
        y_prev = 0.0

        for s in spend_series:
            y_curr = s + alpha * y_prev
            adstock_series.append(round(y_curr, 2))
            y_prev = y_curr

            # Hill curve
            numerator = V * (y_curr ** n)
            denominator = (K ** n) + (y_curr ** n)
            resp = numerator / denominator if denominator > 0 else 0.0
            response_series.append(round(resp, 2))

        return {
            "retention_rate_alpha": alpha,
            "half_saturation_k": K,
            "hill_exponent_n": n,
            "total_raw_spend": sum(spend_series),
            "final_adstock_level": adstock_series[-1] if adstock_series else 0.0,
            "final_response_units": response_series[-1] if response_series else 0.0,
            "adstock_series": adstock_series,
            "response_series": response_series
        }

    def optimize_kkt_budget_allocation(self, channel_params: List[Dict[str, float]],
                                      total_budget_usd: float) -> Dict[str, Any]:
        """
        Allocates marketing budget across channels to equalize marginal revenue (KKT condition):
        Response_i(B_i) = V_i * B_i / (K_i + B_i) -> dR/dB = (V_i * K_i) / (K_i + B_i)^2
        Uses bisection on Lagrange multiplier lambda to solve sum B_i = B_total.
        """
        B_tot = max(100.0, total_budget_usd)
        
        # Bisection on lambda in [low, high]
        lambda_low = 1e-9
        lambda_high = 100.0
        best_allocations = {}

        for _ in range(50):
            lambda_mid = (lambda_low + lambda_high) / 2.0
            current_sum = 0.0
            alloc = {}

            for ch in channel_params:
                name = ch.get("channel", "chan")
                V = float(ch.get("v_max", 50000.0))
                K = float(ch.get("k_half", 5000.0))

                # (V * K) / (K + B)^2 = lambda  =>  (K + B)^2 = (V * K) / lambda
                # B = sqrt( (V * K) / lambda ) - K
                val = (V * K) / max(1e-9, lambda_mid)
                if val > 0:
                    b_target = math.sqrt(val) - K
                else:
                    b_target = 0.0

                b_clamped = max(0.0, b_target)
                alloc[name] = b_clamped
                current_sum += b_clamped

            if current_sum > B_tot:
                lambda_low = lambda_mid
            else:
                lambda_high = lambda_mid
            best_allocations = alloc

        # Compute expected revenue per channel
        allocated_output = []
        total_projected_rev = 0.0

        for ch in channel_params:
            name = ch.get("channel", "chan")
            V = float(ch.get("v_max", 50000.0))
            K = float(ch.get("k_half", 5000.0))
            b_spend = best_allocations.get(name, 0.0)
            rev = V * b_spend / (K + b_spend) if (K + b_spend) > 0 else 0.0
            total_projected_rev += rev

            allocated_output.append({
                "channel": name,
                "recommended_spend_usd": round(b_spend, 2),
                "budget_share_pct": round((b_spend / B_tot) * 100.0, 2),
                "expected_revenue_usd": round(rev, 2),
                "roas": round(rev / max(1.0, b_spend), 2)
            })

        return {
            "total_budget_usd": B_tot,
            "total_projected_revenue_usd": round(total_projected_rev, 2),
            "aggregate_roas": round(total_projected_rev / B_tot, 2),
            "channel_allocations": allocated_output
        }

    def calculate_churn_hazard(self, tenure_months: float,
                              baseline_hazard: float = 0.05,
                              covariate_weights: Dict[str, float] = None,
                              covariates: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Calculates Cox Proportional Hazards: h(t | x) = h0 * exp( sum beta_i * x_i )
        Survival probability S(t) = exp( - h(t | x) * t )
        """
        h0 = max(0.001, baseline_hazard)
        weights = covariate_weights or {"price_increase_pct": 0.05, "unresolved_tickets": 0.40, "nps_score_inv": 0.20}
        covs = covariates or {"price_increase_pct": 10.0, "unresolved_tickets": 1.0, "nps_score_inv": 2.0}

        linear_predictor = sum(weights.get(k, 0.0) * covs.get(k, 0.0) for k in covs)
        hazard_ratio = math.exp(min(20.0, max(-20.0, linear_predictor)))
        effective_hazard = h0 * hazard_ratio

        # Survival probability
        survival_prob = math.exp(-effective_hazard * (tenure_months / 12.0))
        churn_risk_prob = 1.0 - survival_prob

        return {
            "tenure_months": tenure_months,
            "baseline_hazard": h0,
            "hazard_ratio": round(hazard_ratio, 4),
            "annual_churn_probability": round(churn_risk_prob, 4),
            "expected_survival_probability": round(survival_prob, 4),
            "retention_tier": "CRITICAL_RETENTION_INTERVENTION" if churn_risk_prob >= 0.40 else ("MODERATE_CHURN_WATCH" if churn_risk_prob >= 0.20 else "HEALTHY_LOW_CHURN")
        }
