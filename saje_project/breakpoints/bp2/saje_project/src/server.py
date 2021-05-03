from sanic import Sanic, text
from saje import Runner
import log  # noqa

app = Sanic(__name__)


@app.get("/")
async def handler(request):
    return text(request.ip)


@app.post("/")
async def start_job(request):
    request.app.ctx.saje.send("something")
    return text(request.ip)


@app.post("/stop")
async def stop_job(request):
    request.app.ctx.saje.send("__STOP__")
    return text(request.ip)


@app.main_process_start
def start_saje(app, _):
    app.ctx.saje = Runner()
    app.ctx.saje.start()


@app.main_process_stop
def stop_saje(app, _):
    app.ctx.saje.stop()


app.run(port=8888, debug=True, workers=2)
