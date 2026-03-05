# PMO Governance Dashboard
**Author:** Anandi M | MSc Data Science, University of Bath  
**Tools:** Python · SQL · Power BI · DAX · Excel  
**Domain:** Project Management Office · Operational Governance · KPI Reporting · RAG Status Tracking

---

## What This Project Does

An end-to-end PMO (Project Management Office) governance analytics system that consolidates project status, budget variance, resource utilisation and risk indicators into a single governance dashboard — designed for weekly leadership reporting and programme-level decision making.

Built to replicate the kind of MI pack a PMO Analyst or Business Analyst produces for senior stakeholders in large enterprise environments.

---

## Business Problems It Solves

| Problem | Solution |
|---|---|
| Project status scattered across spreadsheets | Centralised SQL data model with single source of truth |
| RAG status manually updated each week | Automated RAG calculation based on budget/schedule rules |
| No early warning for at-risk projects | Threshold-based escalation flags with 3-tier alert logic |
| Budget variance hidden in raw numbers | Variance analysis with trend, not just point-in-time |
| Resource over/under-allocation invisible | Utilisation tracking per team and per project |

---

## RAG Status Logic

```python
def calculate_rag(budget_variance_pct, schedule_variance_days, risk_score):
    """
    Automated RAG status calculation
    Red:   Budget > 10% over OR Schedule > 14 days late OR Risk score > 7
    Amber: Budget 5-10% over OR Schedule 7-14 days late OR Risk score 5-7
    Green: All within tolerance
    """
    if budget_variance_pct > 10 or schedule_variance_days > 14 or risk_score > 7:
        return 'RED'
    elif budget_variance_pct > 5 or schedule_variance_days > 7 or risk_score > 5:
        return 'AMBER'
    else:
        return 'GREEN'
```

---

## SQL Queries Included

| # | Query | Business Question | Technique |
|---|---|---|---|
| 1 | Portfolio RAG summary | How many projects are Red/Amber/Green? | GROUP BY + CASE |
| 2 | Budget variance by project | Which projects are over/under budget? | Actual vs planned JOIN |
| 3 | Schedule slippage tracker | Which milestones are late? | DATEDIFF + threshold |
| 4 | Resource utilisation | Who is over/under-allocated this month? | SUM hours + capacity |
| 5 | Risk register summary | What are the top 5 open risks? | ORDER BY + priority score |
| 6 | Monthly spend trend | Is programme spend tracking to forecast? | DATE + running total |
| 7 | Milestone completion rate | What % of milestones delivered on time? | COUNT + CASE + ratio |
| 8 | Dependency risk map | Which projects block others if delayed? | Self-JOIN dependency logic |

---

## Project Structure

```
pmo-governance-dashboard/
├── data/
│   ├── projects.csv               # 20 sample projects with status/budget/dates
│   ├── milestones.csv             # 80 milestone records
│   ├── resources.csv              # Resource allocation by project/month
│   └── risks.csv                  # Risk register with scores and owners
├── sql/
│   └── pmo_queries.sql            # 8 governance queries
├── pipeline/
│   ├── rag_calculator.py          # Automated RAG status engine
│   ├── variance_analysis.py       # Budget and schedule variance
│   └── dashboard_data_prep.py     # Power BI-ready output generator
├── outputs/
│   └── weekly_governance_pack.xlsx  # Sample governance report
└── README.md
```

---

## How To Run

```bash
# Install dependencies
pip install pandas numpy openpyxl xlsxwriter

# Generate full governance pack
python pipeline/rag_calculator.py
python pipeline/variance_analysis.py
python pipeline/dashboard_data_prep.py
```

---

## Sample Output — Weekly Governance Summary

| Project | RAG | Budget Variance | Schedule (Days) | Risk Score | Owner |
|---|---|---|---|---|---|
| Data Platform Migration | 🔴 RED | +14.2% | +18 days | 8/10 | Team A |
| CRM Integration | 🟡 AMBER | +6.8% | +9 days | 6/10 | Team B |
| Reporting Automation | 🟢 GREEN | -2.1% | +2 days | 3/10 | Team C |
| Cloud Infrastructure | 🟡 AMBER | +7.5% | +11 days | 5/10 | Team D |
| Analytics Dashboard | 🟢 GREEN | +1.2% | 0 days | 2/10 | Team E |

---

## Key Metrics Tracked

- **Portfolio RAG distribution** — % Red/Amber/Green across all projects
- **Budget variance** — actual vs planned spend, by project and programme total  
- **Schedule performance index** — milestones delivered on time vs total
- **Resource utilisation** — % allocated vs capacity, by team
- **Risk exposure score** — weighted average across open risks
- **Milestone burn rate** — planned vs actual completion velocity

---

## What I Would Do Differently

1. **Connect to a live project tool** — integrate with Jira or MS Project API rather than CSV so status updates automatically
2. **Add forecasting** — linear regression on spend trend to predict end-of-programme cost
3. **Email alerting** — auto-send Red project alerts to programme directors on Monday morning
4. **Power Automate integration** — trigger governance report generation on a schedule without manual run

---

## Skills Demonstrated
`SQL` `Python` `Pandas` `DAX` `Power BI` `Project Analytics` `RAG Status` `Variance Analysis` `Governance Reporting` `KPI Dashboards` `Stakeholder MI`
