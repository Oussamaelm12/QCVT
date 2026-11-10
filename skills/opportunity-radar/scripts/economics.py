#!/usr/bin/env python3
"""Transparent unit-economics sensitivity calculations; no forecast claims."""
import argparse
import json

def model(price_eur, target_eur=10000, fee_fraction=0.15, monthly_fixed_eur=20, variable_cost_eur=0, conversion_fraction=0.02):
    if price_eur <= 0 or target_eur <= 0 or not 0 <= fee_fraction < 1 or not 0 < conversion_fraction <= 1 or monthly_fixed_eur < 0 or variable_cost_eur < 0:
        raise ValueError("invalid scenario parameters")
    from math import ceil
    customers = ceil(target_eur / price_eur)
    gross = customers * price_eur
    fees = gross * fee_fraction
    variable = customers * variable_cost_eur
    return {
        "status": "SCENARIO, NOT FORECAST",
        "target_gross_revenue_eur": target_eur,
        "price_eur_per_paying_customer_month": price_eur,
        "paying_customers_required": customers,
        "conversion_fraction_assumed": conversion_fraction,
        "qualified_visitors_required_at_assumed_conversion": ceil(customers / conversion_fraction),
        "gross_revenue_eur": round(gross, 2),
        "platform_fees_eur": round(fees, 2),
        "variable_cost_eur": round(variable, 2),
        "fixed_operating_cost_eur": monthly_fixed_eur,
        "contribution_after_listed_costs_eur": round(gross - fees - variable - monthly_fixed_eur, 2),
        "disclaimer": "Excludes taxes, refunds, churn, marketing, labor, and other unlisted costs. Assumed conversion is not evidence."
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--price", type=float, required=True)
    p.add_argument("--target", type=float, default=10000)
    p.add_argument("--fee", type=float, default=0.15)
    p.add_argument("--fixed", type=float, default=20)
    p.add_argument("--variable", type=float, default=0)
    p.add_argument("--conversion", type=float, default=0.02)
    args = p.parse_args()
    print(json.dumps(model(args.price, args.target, args.fee, args.fixed, args.variable, args.conversion), indent=2))
if __name__ == "__main__":
    main()
