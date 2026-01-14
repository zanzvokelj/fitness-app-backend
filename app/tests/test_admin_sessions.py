def test_admin_cannot_reduce_capacity_below_bookings(client, setup_booking_data):
    data = setup_booking_data

    # make booking
    r = client.post(
        f"/api/v1/bookings/?session_id={data['session_id']}",
        headers=data["headers"],
    )
    assert r.status_code == 201

    # capacity manjša od bookingov → VALIDATION ERROR
    r = client.patch(
        f"/api/v1/admin/sessions/{data['session_id']}/capacity",
        json={"capacity": 0},
        headers=data["headers"],
    )

    assert r.status_code == 422