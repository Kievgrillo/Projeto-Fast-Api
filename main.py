from fastapi import FastAPI

app = FastAPI(title="Projeto FastAPI")


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/itens/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}