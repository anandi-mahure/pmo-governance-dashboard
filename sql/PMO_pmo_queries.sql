-- ============================================================
-- PMO GOVERNANCE DASHBOARD — SQL QUERIES
-- Author: Anandi M | MSc Data Science, University of Bath
-- Description: Portfolio governance, RAG status, budget variance,
--              resource utilisation and milestone tracking queries
-- ============================================================


-- ── QUERY 1 ──────────────────────────────────────────────────
-- Portfolio RAG summary
-- Business question: How many projects are Red / Amber / Green?
-- ──────────────────────────────────────────────────────────────
SELECT
    rag_status,
    COUNT(project_id)                                   AS project_count,
    ROUND(COUNT(project_id) * 100.0 /
          SUM(COUNT(project_id)) OVER (), 1)            AS pct_of_portfolio,
    SUM(total_budget)                                   AS budget_at_risk,
    GROUP_CONCAT(project_name, ', ')                    AS projects
FROM projects
GROUP BY rag_status
ORDER BY CASE rag_status WHEN 'RED' THEN 1 WHEN 'AMBER' THEN 2 ELSE 3 END;


-- ── QUERY 2 ──────────────────────────────────────────────────
-- Budget variance by project
-- Business question: Which projects are over or under budget?
-- ──────────────────────────────────────────────────────────────
SELECT
    p.project_id,
    p.project_name,
    p.project_owner,
    p.total_budget                                      AS planned_budget,
    COALESCE(SUM(s.actual_spend), 0)                    AS actual_spend,
    COALESCE(SUM(s.actual_spend), 0) - p.total_budget   AS variance_gbp,
    ROUND((COALESCE(SUM(s.actual_spend), 0) - p.total_budget)
          / p.total_budget * 100, 1)                    AS variance_pct,
    CASE
        WHEN (COALESCE(SUM(s.actual_spend), 0) - p.total_budget)
             / p.total_budget * 100 > 10  THEN 'RED — Escalate'
        WHEN (COALESCE(SUM(s.actual_spend), 0) - p.total_budget)
             / p.total_budget * 100 > 5   THEN 'AMBER — Monitor'
        ELSE 'GREEN — On Track'
    END                                                 AS budget_rag
FROM projects p
LEFT JOIN spend s ON p.project_id = s.project_id
GROUP BY p.project_id, p.project_name, p.project_owner, p.total_budget
ORDER BY variance_pct DESC;


-- ── QUERY 3 ──────────────────────────────────────────────────
-- Schedule slippage tracker
-- Business question: Which milestones are late and by how many days?
-- ──────────────────────────────────────────────────────────────
SELECT
    m.milestone_id,
    m.milestone_name,
    p.project_name,
    m.planned_date,
    m.actual_date,
    CASE
        WHEN m.actual_date IS NULL THEN
            CAST(julianday('now') - julianday(m.planned_date) AS INTEGER)
        ELSE
            CAST(julianday(m.actual_date) - julianday(m.planned_date) AS INTEGER)
    END                                                 AS days_variance,
    CASE
        WHEN m.status = 'Complete' AND
             julianday(m.actual_date) <= julianday(m.planned_date)
             THEN 'Delivered On Time'
        WHEN m.status = 'Complete'   THEN 'Delivered Late'
        WHEN julianday('now') > julianday(m.planned_date)
             THEN 'Overdue — No Completion'
        ELSE 'Upcoming'
    END                                                 AS delivery_status
FROM milestones m
JOIN projects p ON m.project_id = p.project_id
ORDER BY days_variance DESC;


-- ── QUERY 4 ──────────────────────────────────────────────────
-- Resource utilisation by team
-- Business question: Who is over or under-allocated this month?
-- ──────────────────────────────────────────────────────────────
SELECT
    r.team_name,
    r.resource_name,
    SUM(r.allocated_hours)                              AS total_allocated_hrs,
    r.monthly_capacity_hrs,
    ROUND(SUM(r.allocated_hours) * 100.0
          / r.monthly_capacity_hrs, 1)                  AS utilisation_pct,
    CASE
        WHEN SUM(r.allocated_hours) > r.monthly_capacity_hrs * 1.1
             THEN 'OVER-ALLOCATED — Risk of burnout'
        WHEN SUM(r.allocated_hours) < r.monthly_capacity_hrs * 0.7
             THEN 'UNDER-UTILISED — Capacity available'
        ELSE 'OPTIMAL'
    END                                                 AS utilisation_status
FROM resources r
WHERE r.month = strftime('%Y-%m', 'now')
GROUP BY r.team_name, r.resource_name, r.monthly_capacity_hrs
ORDER BY utilisation_pct DESC;


-- ── QUERY 5 ──────────────────────────────────────────────────
-- Top open risks by priority score
-- Business question: What are our highest-priority unmitigated risks?
-- ──────────────────────────────────────────────────────────────
SELECT
    rk.risk_id,
    rk.risk_description,
    p.project_name,
    rk.probability_score,
    rk.impact_score,
    rk.probability_score * rk.impact_score              AS risk_exposure_score,
    rk.mitigation_status,
    rk.risk_owner,
    RANK() OVER (ORDER BY rk.probability_score * rk.impact_score DESC) AS risk_rank
FROM risks rk
JOIN projects p ON rk.project_id = p.project_id
WHERE rk.status = 'Open'
ORDER BY risk_exposure_score DESC
LIMIT 10;


-- ── QUERY 6 ──────────────────────────────────────────────────
-- Monthly programme spend trend with running total
-- Business question: Is cumulative spend tracking to forecast?
-- ──────────────────────────────────────────────────────────────
SELECT
    spend_month,
    SUM(actual_spend)                                   AS monthly_spend,
    SUM(planned_spend)                                  AS monthly_forecast,
    SUM(actual_spend) - SUM(planned_spend)              AS monthly_variance,
    SUM(SUM(actual_spend)) OVER (
        ORDER BY spend_month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                                   AS cumulative_actual,
    SUM(SUM(planned_spend)) OVER (
        ORDER BY spend_month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                                   AS cumulative_forecast
FROM spend
GROUP BY spend_month
ORDER BY spend_month;


-- ── QUERY 7 ──────────────────────────────────────────────────
-- Milestone completion rate — on-time delivery %
-- Business question: What % of milestones are delivered on time?
-- ──────────────────────────────────────────────────────────────
WITH milestone_status AS (
    SELECT
        project_id,
        COUNT(*)                                        AS total_milestones,
        SUM(CASE WHEN status = 'Complete'
                 AND actual_date <= planned_date
                 THEN 1 ELSE 0 END)                     AS on_time,
        SUM(CASE WHEN status = 'Complete'
                 AND actual_date > planned_date
                 THEN 1 ELSE 0 END)                     AS late,
        SUM(CASE WHEN status != 'Complete'
                 AND planned_date < DATE('now')
                 THEN 1 ELSE 0 END)                     AS overdue
    FROM milestones
    GROUP BY project_id
)
SELECT
    p.project_name,
    ms.total_milestones,
    ms.on_time,
    ms.late,
    ms.overdue,
    ROUND(ms.on_time * 100.0 / ms.total_milestones, 1) AS on_time_delivery_pct
FROM milestone_status ms
JOIN projects p ON ms.project_id = p.project_id
ORDER BY on_time_delivery_pct DESC;


-- ── QUERY 8 ──────────────────────────────────────────────────
-- Project dependency risk — which projects block others?
-- Business question: If a Red project is delayed, what else slips?
-- ──────────────────────────────────────────────────────────────
SELECT
    p_blocker.project_name                              AS blocking_project,
    p_blocker.rag_status                                AS blocker_rag,
    p_dependent.project_name                            AS dependent_project,
    p_dependent.rag_status                              AS dependent_rag,
    d.dependency_type,
    CASE
        WHEN p_blocker.rag_status = 'RED'
             THEN 'HIGH RISK — Blocker is Red, dependent project at risk'
        WHEN p_blocker.rag_status = 'AMBER'
             THEN 'MONITOR — Blocker is Amber'
        ELSE 'LOW RISK'
    END                                                 AS cascade_risk
FROM dependencies d
JOIN projects p_blocker   ON d.blocking_project_id   = p_blocker.project_id
JOIN projects p_dependent ON d.dependent_project_id  = p_dependent.project_id
ORDER BY CASE p_blocker.rag_status WHEN 'RED' THEN 1 WHEN 'AMBER' THEN 2 ELSE 3 END;
