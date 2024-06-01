from config import Config
import asyncio
import nats
from service import Service
from parser import Parser


async def main():
    cfg = Config()

    nc = await nats.connect(cfg.nats)
    js = nc.jetstream()

    try:
        await js.add_stream(name="main-stream", subjects=["cv.new"])
    except Exception as e:
        print(f"Stream might already exist: {e}")

    parser = Parser()
    srv = Service(parser, js)

    _ = await js.subscribe("cv.new", cb=srv.parser_handler)

    print("Listening for messages...")
    while True:
        # Ожидание для предотвращения завершения программы
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
