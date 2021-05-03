import asyncio
import uuid
from sanic import Sanic, text
from sanic.log import logger


app = Sanic(__name__)
app.config.NUM_TASK_WORKERS = 2


@app.post("/start_task")
async def start_task(request):
    uid = uuid.uuid4()
    await request.app.ctx.queue.put(
        {
            "name": "execute_slow_stuff",
            "uid": uid,
        }
    )
    return text(f"Started task with {uid=}", status=202)


async def worker(name, queue):
    while True:
        job = await queue.get()
        if not job:
            break
        size = queue.qsize()
        logger.info(f"[{name}] Running {job}. {size} in queue.")
        await asyncio.sleep(0.1)


@app.after_server_start
async def setup_task_executor(app, _):
    app.ctx.queue = asyncio.Queue(maxsize=64)
    for x in range(app.config.NUM_TASK_WORKERS):
        app.add_task(worker(f"Worker-{x}", app.ctx.queue))


app.run(port=8888, debug=True)
