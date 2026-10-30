# -*- coding: utf-8 -*-
from client import OpenClawGenParkMarketing

mkt = OpenClawGenParkMarketing()

# 1. Hill Adstock Saturation
spends = [500, 800, 1200, 1500, 2000, 1000]
hill = mkt.compute_hill_adstock_saturation(spends, half_saturation_k=1000.0, hill_exponent_n=1.5, retention_rate_alpha=0.4, max_volume_v=250.0)
print(f"Adstock Response: Final Adstock=${hill['final_adstock_level']}, Response Units={hill['final_response_units']}")

# 2. KKT Multi-Channel Budget Allocation
channels = [
    {"channel": "Google_Search", "v_max": 80000.0, "k_half": 8000.0},
    {"channel": "Meta_Video", "v_max": 60000.0, "k_half": 12000.0},
    {"channel": "TikTok_Shop", "v_max": 45000.0, "k_half": 6000.0}
]
alloc = mkt.optimize_kkt_budget_allocation(channels, total_budget_usd=25000.0)
print(f"\nOptimal KKT Budget Allocation (Total: ${alloc['total_budget_usd']}):")
for ch in alloc['channel_allocations']:
    print(f"  {ch['channel']}: ${ch['recommended_spend_usd']} ({ch['budget_share_pct']}%) -> ROAS {ch['roas']}x")

# 3. Churn Hazard
churn = mkt.calculate_churn_hazard(tenure_months=18.0, baseline_hazard=0.04)
print(f"\nChurn Hazard: Annual Churn Prob = {churn['annual_churn_probability']*100:.1f}% ({churn['retention_tier']})")
