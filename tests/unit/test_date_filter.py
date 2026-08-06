from datetime import date
from unittest.mock import MagicMock

import pytest

from exceptions import ValidationError
from utils.date_filter import filter_date


def test_filter_date_week_uses_last_7_days(monkeypatch):
    monkeypatch.setattr("utils.date_filter.date", MagicMock(today=lambda: date(2026, 8, 6)))
    request = MagicMock()

    start_date, end_date = filter_date(request, "week")

    assert start_date == date(2026, 7, 30)
    assert end_date == date(2026, 8, 6)


def test_filter_date_custom_requires_both_dates():
    request = MagicMock()
    request.args.get.side_effect = ["2026-08-01", None]

    with pytest.raises(ValidationError):
        filter_date(request, "custom")


def test_filter_date_rejects_unknown_filter():
    request = MagicMock()

    with pytest.raises(ValidationError):
        filter_date(request, "year")
