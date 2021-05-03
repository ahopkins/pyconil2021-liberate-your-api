from uuid import uuid4

from sanic import Sanic, text
from sanic.response import json

from saje.backend import FileBackend
from saje.runner import Runner

app = Sanic(__name__)
WORKERS = 2


@app.get("/<uid:uuid>")
async def handler(request, uid):
    data = await request.app.ctx.jobs.fetch(uid)
    return json(data)


@app.post("/")
async def start_job(request):
    uid = str(uuid4())
    request.app.ctx.saje.send(
        {
            "task": "hello",
            "uid": uid,
            "kwargs": {"name": "Adam"},
        }
    )
    return text(uid)


@app.main_process_start
def start_saje(app, _):
    app.ctx.saje = Runner(workers=WORKERS)
    app.ctx.saje.start()


@app.main_process_stop
def stop_saje(app, _):
    app.ctx.saje.stop()


@app.after_server_start
async def setup_job_fetch(app, _):
    app.ctx.jobs = FileBackend("./db")


app.run(port=8888, workers=WORKERS)
