"""
PMO Governance Dashboard — RAG Status Calculator & Data Generator
Author: Anandi M | MSc Data Science, University of Bath
Description: Automated RAG status calculation engine + sample data generator
             for PMO governance reporting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# ── RAG CALCULATOR ────────────────────────────────────────────
def calculate_rag(budget_variance_pct: float,
                  schedule_variance_days: int,
                  risk_score: float) -> str:
    """
    Automated RAG status — three-input rule engine.
    Any single RED trigger = RED overall.
    Any single AMBER (no RED) = AMBER overall.
    """
    if (budget_variance_pct > 10 or
        schedule_variance_days > 14 or
        risk_score > 7):
        return 'RED'
    elif (budget_variance_pct > 5 or
          schedule_variance_days > 7 or
          risk_score > 5):
        return 'AMBER'
    return 'GREEN'


def calculate_risk_score(probability: float, impact: float) -> float:
    """Risk exposure score = probability × impact (1-10 scale each)."""
    return round(probability * impact / 10, 1)


# ── SAMPLE DATA GENERATOR ────────────────────────────────────
def generate_portfolio_data(n_projects: int = 20) -> pd.DataFrame:
    """Generate realistic PMO portfolio dataset."""
    
    project_types = ['Data Migration', 'Platform Upgrade', 'CRM Integration',
                     'Reporting Automation', 'Cloud Migration', 'API Development',
                     'Analytics Dashboard', 'Security Remediation', 'ERP Enhancement',
                     'Digital Transformation']
    teams = ['Team Alpha', 'Team Beta', 'Team Gamma', 'Team Delta', 'Team Epsilon']
    owners = ['Sarah K', 'James T', 'Priya M', 'David L', 'Emma R',
              'Anandi M', 'Tom B', 'Lisa C', 'Raj P', 'Kate S']

    base_date = datetime(2024, 1, 1)
    projects = []

    for i in range(1, n_projects + 1):
        planned_start  = base_date + timedelta(days=random.randint(0, 60))
        planned_end    = planned_start + timedelta(days=random.randint(60, 180))
        budget         = random.randint(50000, 500000)
        spend_pct      = random.uniform(0.85, 1.18)
        actual_spend   = round(budget * spend_pct, 0)
        bv_pct         = round((actual_spend - budget) / budget * 100, 1)
        schedule_slip  = random.randint(-5, 25)
        probability    = round(random.uniform(1, 9), 1)
        impact         = round(random.uniform(1, 9), 1)
        risk           = calculate_risk_score(probability, impact)
        rag            = calculate_rag(bv_pct, schedule_slip, risk)

        projects.append({
            'project_id':             f'PRJ{i:03d}',
            'project_name':           f'{random.choice(project_types)} {i}',
            'project_owner':          random.choice(owners),
            'team':                   random.choice(teams),
            'planned_start':          planned_start.date(),
            'planned_end':            planned_end.date(),
            'total_budget':           budget,
            'actual_spend':           actual_spend,
            'budget_variance_pct':    bv_pct,
            'schedule_variance_days': schedule_slip,
            'risk_score':             risk,
            'rag_status':             rag,
            'status':                 random.choice(['In Progress', 'In Progress',
                                                     'In Progress', 'On Hold', 'Complete'])
        })

    return pd.DataFrame(projects)


def generate_milestones(projects_df: pd.DataFrame,
                        milestones_per_project: int = 4) -> pd.DataFrame:
    milestone_names = ['Kick-off Complete', 'Design Sign-off', 'Development Complete',
                       'UAT Complete', 'Go-Live', 'Post-Implementation Review']
    milestones = []
    mid = 1

    for _, proj in projects_df.iterrows():
        start = pd.to_datetime(proj['planned_start'])
        end   = pd.to_datetime(proj['planned_end'])
        interval = (end - start).days // milestones_per_project

        for j in range(milestones_per_project):
            planned = start + timedelta(days=interval * (j + 1))
            slip    = random.randint(-3, proj['schedule_variance_days'] + 5)
            actual  = planned + timedelta(days=slip)
            status  = 'Complete' if actual <= datetime.now() else 'Upcoming'

            milestones.append({
                'milestone_id':   f'MS{mid:04d}',
                'project_id':     proj['project_id'],
                'milestone_name': milestone_names[j % len(milestone_names)],
                'planned_date':   planned.date(),
                'actual_date':    actual.date() if status == 'Complete' else None,
                'status':         status,
                'days_variance':  slip
            })
            mid += 1

    return pd.DataFrame(milestones)


# ── GOVERNANCE SUMMARY REPORT ─────────────────────────────────
def generate_governance_report(projects_df: pd.DataFrame) -> dict:
    """Generate weekly governance pack summary statistics."""
    total  = len(projects_df)
    rag_summary = projects_df['rag_status'].value_counts()

    report = {
        'report_date':         datetime.now().strftime('%d %B %Y'),
        'total_projects':      total,
        'red_count':           rag_summary.get('RED', 0),
        'amber_count':         rag_summary.get('AMBER', 0),
        'green_count':         rag_summary.get('GREEN', 0),
        'red_pct':             round(rag_summary.get('RED', 0) / total * 100, 1),
        'total_budget':        projects_df['total_budget'].sum(),
        'total_actual_spend':  projects_df['actual_spend'].sum(),
        'portfolio_variance':  round(
            (projects_df['actual_spend'].sum() - projects_df['total_budget'].sum())
            / projects_df['total_budget'].sum() * 100, 1),
        'avg_schedule_slip':   round(projects_df['schedule_variance_days'].mean(), 1),
        'red_projects':        projects_df[
            projects_df['rag_status'] == 'RED']['project_name'].tolist()
    }
    return report


# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)

    # Generate data
    projects   = generate_portfolio_data(20)
    milestones = generate_milestones(projects)

    # Save
    projects.to_csv('data/projects.csv', index=False)
    milestones.to_csv('data/milestones.csv', index=False)

    # Print governance summary
    report = generate_governance_report(projects)
    print("\n" + "="*55)
    print(f"  PMO GOVERNANCE SUMMARY — {report['report_date']}")
    print("="*55)
    print(f"  Total Projects:    {report['total_projects']}")
    print(f"  🔴 RED:            {report['red_count']} ({report['red_pct']}%)")
    print(f"  🟡 AMBER:          {report['amber_count']}")
    print(f"  🟢 GREEN:          {report['green_count']}")
    print(f"  Portfolio Variance:{report['portfolio_variance']:+.1f}%")
    print(f"  Avg Schedule Slip: {report['avg_schedule_slip']} days")
    print(f"\n  🔴 Red Projects:")
    for p in report['red_projects']:
        print(f"     - {p}")
    print("="*55)
    print(f"\nData saved to data/ folder")
    print("Run sql/pmo_queries.sql against projects.csv for full analysis")
