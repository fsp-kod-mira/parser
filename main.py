from parser import Parser
import asyncio


async def main():
    parser = Parser()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
