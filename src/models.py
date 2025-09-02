from datetime import datetime

def user_helper(u) -> dict:
    return {
        "id": str(u["_id"]),
        "username": u["username"],
        "full_name": u.get("full_name"),
        "join_date": u.get("join_date"),
        "cash_balance": u.get("cash_balance", 0.0),
        "holdings": u.get("holdings", {}),
    }