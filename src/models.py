from datetime import datetime

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "full_name": user.get("full_name"),
        "join_date": user.get("join_date", datetime.utcnow()),
    }