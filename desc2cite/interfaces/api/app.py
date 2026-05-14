from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from desc2cite.interfaces.api.routes import router

app = FastAPI(title="Desc2Cite Web", version="0.1.0")
app.include_router(router)
app.mount("/static", StaticFiles(directory="desc2cite/interfaces/web/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    with open("desc2cite/interfaces/web/templates/index.html", "r", encoding="utf-8") as file:
        return file.read()
