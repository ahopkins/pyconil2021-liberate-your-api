from sanic import Sanic, html
from sanic.log import logger
from pathlib import Path
import ujson
import asyncio
import presentation  # noqa
from watchgod import awatch

app = Sanic("Presentation")
PRESENTATION = Path(__file__).parent / "presentation"
HELLO = {
    "command": "hello",
    "protocols": [
        "http://livereload.com/protocols/official-7",
    ],
    "serverName": app.name,
}
RELOAD = {"command": "reload", "path": str(PRESENTATION / "slides.md")}


@app.get("/")
def index(_):
    with open(PRESENTATION / "index.html", "r") as f:
        doc = f.read()

    with open(PRESENTATION / "slides.md", "r") as f:
        slides = f.read()

    return html(doc.replace("__SLIDES__", slides))


app.static("/assets", PRESENTATION / "assets")


@app.signal("watchdog.file.reload")
async def file_reloaded():
    print("...")


livereload = Sanic("livereload")
livereload.static("/livereload.js", PRESENTATION / "livereload.js")


@livereload.websocket("/livereload")
async def livereload_handler(request, ws):
    global app
    logger.info("Connected")
    msg = await ws.recv()
    logger.info(msg)
    await ws.send(ujson.dumps(HELLO))

    while True:
        print("waiting")
        await app.event("watchdog.file.reload")
        await ws.send(ujson.dumps(RELOAD))
        print("triggered")


@app.before_server_start
async def start(app, _):
    global livereload
    app.ctx.livereload = await livereload.create_server(
        port=35729, return_asyncio_server=True
    )
    app.ctx.livereload.after_start()


@app.before_server_stop
async def stop(app, _):
    app.ctx.livereload.before_stop()
    await app.ctx.livereload.close()
    app.ctx.livereload.after_stop()


@app.before_server_start
async def start_watch(app, loop):
    app.add_task(watch(app))


async def watch(app):
    async for changes in awatch(PRESENTATION):
        for change, filename in changes:
            await app.dispatch("watchdog.file.reload")
