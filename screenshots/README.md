# Screenshots

Place your API test screenshots here to serve as proof of work.

## Required Screenshots — Task 1 (Lost & Found)

- `task1_post_item.png` — POST /items
- `task1_get_items.png` — GET /items
- `task1_get_item_by_id.png` — GET /items/{item_id}
- `task1_put_item.png` — PUT /items/{item_id}
- `task1_delete_item.png` — DELETE /items/{item_id}
- `task1_status_filter.png` — GET /items/status/Lost
- `task1_category_filter.png` — GET /items/category/Electronics

## Required Screenshots — Task 2 (Event Reservation)

- `task2_post_event.png` — POST /events
- `task2_get_events.png` — GET /events
- `task2_reserve_seat.png` — POST /events/{event_id}/reserve (success)
- `task2_get_reservations.png` — GET /events/{event_id}/reservations
- `task2_availability.png` — GET /events/{event_id}/availability
- `task2_cancel_reservation.png` — DELETE /reservations/{reservation_id}
- `task2_event_full.png` — POST /events/{event_id}/reserve when full (400 error)
- `task2_event_closed.png` — POST /events/{event_id}/reserve when closed (400 error)
