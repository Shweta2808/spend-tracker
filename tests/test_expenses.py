def test_create_expense_happy_path(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"amount": 42.5, "category": "food", "note": "lunch", "date": "2026-09-10"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == 42.5
    assert body["category"] == "food"
    assert body["id"] is not None


def test_create_expense_rejects_negative_amount(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"amount": -5, "category": "food", "date": "2026-09-10"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_expense_rejects_zero_amount(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"amount": 0, "category": "food", "date": "2026-09-10"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_expense_rejects_empty_category(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"amount": 10, "category": "", "date": "2026-09-10"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_expense_rejects_malformed_date(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "not-a-date"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_expense_rejects_missing_api_key(client):
    response = client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-09-10"},
    )
    assert response.status_code == 401


def test_create_expense_rejects_wrong_api_key(client):
    response = client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-09-10"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_list_expenses_no_filter(client, auth_headers):
    client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-09-01"},
        headers=auth_headers,
    )
    client.post(
        "/expenses",
        json={"amount": 20, "category": "travel", "date": "2026-09-05"},
        headers=auth_headers,
    )
    response = client.get("/expenses", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_list_expenses_filter_by_category(client, auth_headers):
    client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-09-01"},
        headers=auth_headers,
    )
    client.post(
        "/expenses",
        json={"amount": 20, "category": "travel", "date": "2026-09-05"},
        headers=auth_headers,
    )
    response = client.get("/expenses?category=food", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["category"] == "food"


def test_list_expenses_filter_by_date_range(client, auth_headers):
    client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-08-01"},
        headers=auth_headers,
    )
    client.post(
        "/expenses",
        json={"amount": 20, "category": "food", "date": "2026-09-05"},
        headers=auth_headers,
    )
    response = client.get(
        "/expenses?start_date=2026-09-01&end_date=2026-09-30", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["date"] == "2026-09-05"


def test_list_expenses_no_matches_returns_empty_list(client, auth_headers):
    response = client.get("/expenses?category=nonexistent", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_list_expenses_invalid_date_range_rejected(client, auth_headers):
    response = client.get(
        "/expenses?start_date=2026-09-30&end_date=2026-09-01", headers=auth_headers
    )
    assert response.status_code == 400


def test_list_expenses_pagination(client, auth_headers):
    for day in range(1, 6):
        client.post(
            "/expenses",
            json={"amount": 10, "category": "food", "date": f"2026-09-{day:02d}"},
            headers=auth_headers,
        )
    first_page = client.get("/expenses?limit=2&offset=0", headers=auth_headers).json()
    second_page = client.get("/expenses?limit=2&offset=2", headers=auth_headers).json()

    assert first_page["total"] == 5
    assert len(first_page["items"]) == 2
    assert len(second_page["items"]) == 2
    first_ids = {item["id"] for item in first_page["items"]}
    second_ids = {item["id"] for item in second_page["items"]}
    assert first_ids.isdisjoint(second_ids)


def test_update_expense_happy_path(client, auth_headers):
    created = client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-09-01"},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/expenses/{created['id']}",
        json={"amount": 25, "category": "travel", "note": "corrected", "date": "2026-09-02"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["amount"] == 25
    assert body["category"] == "travel"
    assert body["note"] == "corrected"
    assert body["date"] == "2026-09-02"


def test_update_expense_not_found(client, auth_headers):
    response = client.put(
        "/expenses/999999",
        json={"amount": 25, "category": "travel", "date": "2026-09-02"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_update_expense_rejects_invalid_amount(client, auth_headers):
    created = client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-09-01"},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/expenses/{created['id']}",
        json={"amount": -1, "category": "food", "date": "2026-09-01"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_delete_expense_happy_path(client, auth_headers):
    created = client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-09-01"},
        headers=auth_headers,
    ).json()

    response = client.delete(f"/expenses/{created['id']}", headers=auth_headers)
    assert response.status_code == 204

    listing = client.get("/expenses", headers=auth_headers).json()
    assert listing["total"] == 0


def test_delete_expense_not_found(client, auth_headers):
    response = client.delete("/expenses/999999", headers=auth_headers)
    assert response.status_code == 404


def test_update_expense_rejects_missing_api_key(client, auth_headers):
    created = client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-09-01"},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/expenses/{created['id']}",
        json={"amount": 20, "category": "food", "date": "2026-09-01"},
    )
    assert response.status_code == 401


def test_delete_expense_rejects_missing_api_key(client, auth_headers):
    created = client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-09-01"},
        headers=auth_headers,
    ).json()

    response = client.delete(f"/expenses/{created['id']}")
    assert response.status_code == 401


def test_list_expenses_rejects_limit_over_200(client, auth_headers):
    response = client.get("/expenses?limit=201", headers=auth_headers)
    assert response.status_code == 422


def test_list_expenses_combined_category_and_date_filter(client, auth_headers):
    client.post(
        "/expenses",
        json={"amount": 10, "category": "food", "date": "2026-08-15"},
        headers=auth_headers,
    )
    client.post(
        "/expenses",
        json={"amount": 20, "category": "food", "date": "2026-09-15"},
        headers=auth_headers,
    )
    client.post(
        "/expenses",
        json={"amount": 30, "category": "travel", "date": "2026-09-15"},
        headers=auth_headers,
    )
    response = client.get(
        "/expenses?category=food&start_date=2026-09-01&end_date=2026-09-30",
        headers=auth_headers,
    )
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["amount"] == 20


def test_list_expenses_echoes_limit_and_offset(client, auth_headers):
    response = client.get("/expenses?limit=3&offset=1", headers=auth_headers)
    body = response.json()
    assert body["limit"] == 3
    assert body["offset"] == 1


def test_create_expense_normalizes_category_casing_and_whitespace(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"amount": 10, "category": "  Food  ", "date": "2026-09-01"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["category"] == "food"


def test_create_expense_rejects_whitespace_only_category(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"amount": 10, "category": "   ", "date": "2026-09-01"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_list_expenses_filter_is_case_insensitive(client, auth_headers):
    client.post(
        "/expenses",
        json={"amount": 10, "category": "Food", "date": "2026-09-01"},
        headers=auth_headers,
    )
    response = client.get("/expenses?category=FOOD", headers=auth_headers)
    body = response.json()
    assert body["total"] == 1


def test_get_categories_empty_when_no_expenses(client, auth_headers):
    response = client.get("/expenses/categories", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_categories_returns_sorted_normalized_unique_list(client, auth_headers):
    client.post(
        "/expenses",
        json={"amount": 10, "category": "Travel", "date": "2026-09-01"},
        headers=auth_headers,
    )
    client.post(
        "/expenses",
        json={"amount": 20, "category": "  food  ", "date": "2026-09-02"},
        headers=auth_headers,
    )
    client.post(
        "/expenses",
        json={"amount": 5, "category": "FOOD", "date": "2026-09-03"},
        headers=auth_headers,
    )
    response = client.get("/expenses/categories", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == ["food", "travel"]


def test_get_categories_rejects_missing_api_key(client):
    response = client.get("/expenses/categories")
    assert response.status_code == 401
