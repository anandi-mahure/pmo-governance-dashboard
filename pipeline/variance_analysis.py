"""
PMO Governance Dashboard — Variance Analysis Module
Author: Anandi Mahure
Description: Budget and schedule variance analysis across project portfolio.
Outputs summary statistics and flags at-risk projects for governance reporting.
"""

import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

os.makedirs("outputs", exist_ok=True)


def load_data() -> pd.DataFrame:
    df = pd.read_csv("data/projects.csv")
    log.info(f"Loaded {len(df)} projects")
    return df


def budget_variance_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Classify projects by budget variance severity."""
    df = df.copy()
    df["budget_rag"] = df["budget_variance_pct"].apply(
        lambda x: "RED" if x > 10 else ("AMBER" if x > 5 else "GREEN")
    )
    df["variance_gbp"] = df["actual_spend"] - df["total_budget"]
    log.info(f"Budget analysis: {(df['budget_rag']=='RED').sum()} RED, "
             f"{(df['budget_rag']=='AMBER').sum()} AMBER, "
             f"{(df['budget_rag']=='GREEN').sum()} GREEN")
    return df


def schedule_variance_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Classify projects by schedule slippage severity."""
    df = df.copy()
    df["schedule_rag"] = df["schedule_variance_days"].apply(
        lambda x: "RED" if x > 14 else ("AMBER" if x > 7 else "GREEN")
    )
    log.info(f"Schedule analysis: avg slip = {df['schedule_variance_days'].mean():.1f} days")
    return df


def portfolio_summary(df: pd.DataFrame) -> dict:
    """Generate top-level portfolio KPIs."""
    return {
        "report_date":          datetime.now().strftime("%d %B %Y"),
        "total_projects":       len(df),
        "total_budget":         df["total_budget"].sum(),
        "total_actual_spend":   df["actual_spend"].sum(),
        "portfolio_variance_pct": round(
            (df["actual_spend"].sum() - df["total_budget"].sum())
            / df["total_budget"].sum() * 100, 1),
        "red_projects":         int((df["rag_status"] == "RED").sum()),
        "amber_projects":       int((df["rag_status"] == "AMBER").sum()),
        "green_projects":       int((df["rag_status"] == "GREEN").sum()),
        "avg_schedule_slip_days": round(df["schedule_variance_days"].mean(), 1),
        "projects_over_budget": int((df["budget_variance_pct"] > 0).sum()),
    }


def main():
    log.info("=" * 55)
    log.info("PMO GOVERNANCE — VARIANCE ANALYSIS STAGE")
    log.info("=" * 55)

    df = load_data()
    df = budget_variance_analysis(df)
    df = schedule_variance_analysis(df)

    summary = portfolio_summary(df)

    log.info(f"\n  Portfolio variance : {summary['portfolio_variance_pct']:+.1f}%")
    log.info(f"  RED projects       : {summary['red_projects']}")
    log.info(f"  Avg schedule slip  : {summary['avg_schedule_slip_days']} days")

    # Save enriched dataset
    df.to_csv("outputs/variance_analysis.csv", index=False)
    log.info("Variance analysis saved: outputs/variance_analysis.csv")
    return df, summary


if __name__ == "__main__":
    main()
