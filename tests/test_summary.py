def _add_expense(client, auth_headers, amount, category, expense_date):
    response = client.post(
        "/expenses",
        json={"amount": amount, "category": category, "date": expense_date},
        headers=auth_headers,
    )
    assert response.status_code == 201


def test_summary_total_and_by_category(client, auth_headers):
    _add_expense(client, auth_headers, 30, "food", "2026-09-05")
    _add_expense(client, auth_headers, 20, "food", "2026-09-10")
    _add_expense(client, auth_headers, 50, "travel", "2026-09-15")

    response = client.get("/summary?month=2026-09", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_spend"] == 100
    assert body["spend_by_category"] == {"food": 50, "travel": 50}


def test_summary_month_over_month_change(client, auth_headers):
    _add_expense(client, auth_headers, 100, "food", "2026-08-05")
    _add_expense(client, auth_headers, 150, "food", "2026-09-05")

    response = client.get("/summary?month=2026-09", headers=auth_headers)
    body = response.json()
    change = body["month_over_month_change"]
    assert change["current_total"] == 150
    assert change["previous_total"] == 100
    assert change["absolute_change"] == 50
    assert change["percent_change"] == 50.0


def test_summary_month_over_month_with_no_previous_spend(client, auth_headers):
    _add_expense(client, auth_headers, 100, "food", "2026-09-05")

    response = client.get("/summary?month=2026-09", headers=auth_headers)
    body = response.json()
    change = body["month_over_month_change"]
    assert change["previous_total"] == 0
    assert change["percent_change"] is None


def test_summary_flags_category_spike_over_20_percent(client, auth_headers):
    _add_expense(client, auth_headers, 100, "food", "2026-08-05")
    _add_expense(client, auth_headers, 150, "food", "2026-09-05")

    response = client.get("/summary?month=2026-09", headers=auth_headers)
    body = response.json()
    spikes = body["category_spikes"]
    assert len(spikes) == 1
    assert spikes[0]["category"] == "food"
    assert spikes[0]["percent_change"] == 50.0


def test_summary_does_not_flag_spike_under_20_percent(client, auth_headers):
    _add_expense(client, auth_headers, 100, "food", "2026-08-05")
    _add_expense(client, auth_headers, 110, "food", "2026-09-05")

    response = client.get("/summary?month=2026-09", headers=auth_headers)
    body = response.json()
    assert body["category_spikes"] == []


def test_summary_excludes_new_category_with_no_prior_data_from_spikes(client, auth_headers):
    _add_expense(client, auth_headers, 100, "food", "2026-08-05")
    _add_expense(client, auth_headers, 100, "food", "2026-09-05")
    _add_expense(client, auth_headers, 500, "entertainment", "2026-09-10")

    response = client.get("/summary?month=2026-09", headers=auth_headers)
    body = response.json()
    categories_flagged = [spike["category"] for spike in body["category_spikes"]]
    assert "entertainment" not in categories_flagged


def test_summary_defaults_to_current_month_when_not_specified(client, auth_headers):
    response = client.get("/summary", headers=auth_headers)
    assert response.status_code == 200
    assert "month" in response.json()


def test_summary_rejects_missing_api_key(client):
    response = client.get("/summary?month=2026-09")
    assert response.status_code == 401


def test_summary_rejects_malformed_month(client, auth_headers):
    response = client.get("/summary?month=2026-9", headers=auth_headers)
    assert response.status_code == 422


def test_summary_does_not_flag_spike_at_exactly_20_percent(client, auth_headers):
    _add_expense(client, auth_headers, 100, "food", "2026-08-05")
    _add_expense(client, auth_headers, 120, "food", "2026-09-05")

    response = client.get("/summary?month=2026-09", headers=auth_headers)
    body = response.json()
    assert body["category_spikes"] == []


def test_summary_merges_categories_with_different_casing(client, auth_headers):
    _add_expense(client, auth_headers, 50, "Food", "2026-09-05")
    _add_expense(client, auth_headers, 30, "food", "2026-09-10")
    _add_expense(client, auth_headers, 20, "  FOOD  ", "2026-09-15")

    response = client.get("/summary?month=2026-09", headers=auth_headers)
    body = response.json()
    assert body["spend_by_category"] == {"food": 100}
