import motor.motor_asyncio
from app.settings import settings

client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True)

db = client.date_finder

user_collection = db.get_collection("users")
restaurant_collection = db.get_collection("restaurants")


