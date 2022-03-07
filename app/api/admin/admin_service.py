
from app.api.admin.admin_models import BanUsersRequestModel
from app.lib.auth.auth_models import User
from app.db.mongo_driver import user_collection
from pymongo import UpdateOne


async def disable_user_accounts_by_email_and_id(
    admin: User,
    request: BanUsersRequestModel
):
    ids_to_ban_model = {}
    for user in request.users_to_ban_by_id:
        if user.id not in ids_to_ban_model:
            ids_to_ban_model[user.id] = user

    emails_to_ban_model = {}
    for user in request.users_to_ban_by_email:
        if user.email not in emails_to_ban_model:
            emails_to_ban_model[user.email] = user

    users = await user_collection.find({
        "$or": [
            {"_id": {"$in": list(ids_to_ban_model.keys())}},
            {"email": {"$in": list(emails_to_ban_model.keys())}}
        ]
    }).to_list(length=None)


    writes = []
    count = 0
    banned_user_ids = []

    for user in users:
        banned_user_ids.append(user["_id"])
        doc = {"UpdateOne": {}}

        if user["email"] in emails_to_ban_model:
            user["banMsg"] = emails_to_ban_model[user["email"]].msg
            user["banReason"] = emails_to_ban_model[user["email"]].reason.value
            doc["UpdateOne"]["filter"] = {"email": user["email"]}

        else:
            user["banMsg"] = ids_to_ban_model[user["_id"]].msg
            user["banReason"] = ids_to_ban_model[user["_id"]].reason.value
            doc["UpdateOne"]["filter"] = {"_id": user["_id"]}

        doc["UpdateOne"]["update"] = {
            "$set": {
                "banMsg": user["banMsg"],
                "banReason": user["banReason"],
                "disabled": True,
                "bannerId": admin.id
            }
        }

        writes.append(UpdateOne(
            doc["UpdateOne"]["filter"],
            doc["UpdateOne"]["update"]),
        )

    if banned_user_ids:
        count = (await user_collection.bulk_write(writes)).modified_count

    return {
        "count": count,
        "users_banned": banned_user_ids
    }


async def show_all_users():
    return await user_collection.find().to_list(length=None)






