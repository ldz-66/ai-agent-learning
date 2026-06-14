from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!", "status": "运行正常"}


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"你好，{name}！欢迎使用FastAPI"}


@app.get("/add")
def add_numbers(a: int, b: int):
    return {"a": a, "b": b, "result": a + b}