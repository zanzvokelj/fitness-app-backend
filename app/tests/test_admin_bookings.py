def test_non_admin_cannot_create_session(client, setup_booking_data):
    data = setup_booking_data

    r = client.post(
        "/api/v1/admin/sessions",
        json={
            "center_id": data["center_id"],
            "class_type_id": data["class_type_id"],
            "start_time": "2030-01-01T10:00:00",
            "capacity": 10,
        },
    )

    assert r.status_code in (401, 403)