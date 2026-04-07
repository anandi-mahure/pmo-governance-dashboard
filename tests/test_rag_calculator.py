import pytest

def calculate_rag(budget_variance_pct, schedule_variance_days, risk_score):
    if budget_variance_pct > 10 or schedule_variance_days > 14 or risk_score > 7:
        return "RED"
    elif budget_variance_pct > 5 or schedule_variance_days > 7 or risk_score > 5:
        return "AMBER"
    else:
        return "GREEN"

def test_red_budget(): assert calculate_rag(11.0, 0, 0) == "RED"
def test_red_schedule(): assert calculate_rag(0, 15, 0) == "RED"
def test_red_risk(): assert calculate_rag(0, 0, 7.1) == "RED"
def test_amber_budget(): assert calculate_rag(7.5, 0, 0) == "AMBER"
def test_amber_schedule(): assert calculate_rag(0, 10, 0) == "AMBER"
def test_amber_risk(): assert calculate_rag(0, 0, 6.0) == "AMBER"
def test_green(): assert calculate_rag(2.0, 3, 1.5) == "GREEN"
def test_green_zero(): assert calculate_rag(0, 0, 0) == "GREEN"
def test_negative_variance(): assert calculate_rag(-5.0, 0, 0) == "GREEN"
def test_boundary_10_pct(): assert calculate_rag(10.0, 0, 0) == "AMBER"
def test_boundary_5_pct(): assert calculate_rag(5.0, 0, 0) == "GREEN"
def test_red_priority(): assert calculate_rag(12.0, 8, 3) == "RED"
