from datetime import date, timedelta

from flask import Request

from exceptions import ValidationError


def filter_date(request: Request, filter_type: str) -> tuple:
    start_date, end_date = None, None
    today = date.today()
    end_date = today
    if filter_type == "week":
        start_date = today - timedelta(days=7)
    elif filter_type == "month":
        start_date = today - timedelta(days=30)
    elif filter_type == "3months":
        start_date = today - timedelta(days=90)
    elif filter_type == "custom":
        start_str = request.args.get("start_date")
        end_str = request.args.get("end_date")
        if not start_str or not end_str:
            raise ValidationError({"error": "Custom filter requires start_date and end_date"})
        try:
            start_date = date.fromisoformat(start_str)
            end_date = date.fromisoformat(end_str)
        except ValueError:
            raise ValidationError({"error": "Dates must be in YYYY-MM-DD format."})
    else:
        raise ValidationError({"error": f"Unsupported filter type: {filter_type}"})
    return start_date, end_date