"""Unit tests for the booking allowance business rule."""
import pytest

from server import calculate_max_bookable_places


@pytest.mark.parametrize(
    "points, available, already_booked, expected",
    [
        (8, 20, 6, 6),     # Remaining club quota is restrictive
        (3, 20, 0, 3),     # Club points are restrictive
        (20, 4, 0, 4),     # Competition capacity is restrictive
        (20, 20, 0, 12),   # Absolute club quota
        (0, 20, 0, 0),    # No points
        (20, 0, 0, 0),    # No available places
        (20, 20, 12, 0),  # Quota exhausted
        (20, 20, 15, 0),  # Defensive clamp of negative allowance
        ("10", "8", "2", 8),  # JSON-style numeric strings
    ],
)
def test_calculate_max_bookable_places(points, available, already_booked, expected):
    assert calculate_max_bookable_places(points, available, already_booked) == expected
