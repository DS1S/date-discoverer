import uvicorn
from app.settings import settings

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(settings.PORT), reload=True, debug=True)
