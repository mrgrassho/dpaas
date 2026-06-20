from dpaas_core.cost_model import parse_usage_schedule, scenario_for_unit_price, usage_for_month


def test_default_usage_schedule():
    assert usage_for_month(0) == 10
    assert usage_for_month(3) == 8
    assert usage_for_month(8) == 6
    assert usage_for_month(18) == 5
    assert usage_for_month(30) == 4


def test_cost_scenario_math_and_override():
    schedule = parse_usage_schedule("0-0:2,1-1:1")
    scenario = scenario_for_unit_price(10.0, months=1, schedule=schedule)

    assert scenario["monthly"][0]["estimated_diapers"] == 60
    assert scenario["monthly"][0]["estimated_cost_ars"] == 600.0
    assert scenario["monthly"][1]["estimated_cost_ars"] == 300.0
    assert scenario["total_cost_ars"] == 900.0
