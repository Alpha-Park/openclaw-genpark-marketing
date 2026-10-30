# -*- coding: utf-8 -*-
import sys, json
from client import OpenClawGenParkMarketing

client = OpenClawGenParkMarketing()

TOOLS = [
    {
        "name": "compute_hill_adstock_saturation",
        "description": "Calculates geometric adstock carryover with non-linear Hill saturation curves.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spend_series": {"type": "array", "items": {"type": "number"}},
                "half_saturation_k": {"type": "number"},
                "hill_exponent_n": {"type": "number"},
                "retention_rate_alpha": {"type": "number"},
                "max_volume_v": {"type": "number"}
            },
            "required": ["spend_series"]
        }
    },
    {
        "name": "optimize_kkt_budget_allocation",
        "description": "Solves KKT first-order conditions for multi-channel marketing budget allocation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "channel_params": {"type": "array", "items": {"type": "object"}},
                "total_budget_usd": {"type": "number"}
            },
            "required": ["channel_params", "total_budget_usd"]
        }
    },
    {
        "name": "calculate_churn_hazard",
        "description": "Calculates Cox Proportional Hazards churn risk and survival probability.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tenure_months": {"type": "number"},
                "baseline_hazard": {"type": "number"},
                "covariate_weights": {"type": "object"},
                "covariates": {"type": "object"}
            },
            "required": ["tenure_months"]
        }
    }
]

def handle_request(req):
    method = req.get("method")
    rid = req.get("id")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        params = req.get("params", {})
        tname = params.get("name")
        args = params.get("arguments", {})
        if tname == "compute_hill_adstock_saturation":
            res = client.compute_hill_adstock_saturation(args["spend_series"], args.get("half_saturation_k", 1000.0), args.get("hill_exponent_n", 1.5), args.get("retention_rate_alpha", 0.5), args.get("max_volume_v", 100.0))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "optimize_kkt_budget_allocation":
            res = client.optimize_kkt_budget_allocation(args["channel_params"], args["total_budget_usd"])
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "calculate_churn_hazard":
            res = client.calculate_churn_hazard(args["tenure_months"], args.get("baseline_hazard", 0.05), args.get("covariate_weights"), args.get("covariates"))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32600, "message": "Invalid Request"}}

def main():
    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
