import asyncio
import platform

import uvicorn


def setup_event_loop():
    if platform.system() != "Windows":
        try:
            import uvloop

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            print("Using uvloop event loop policy.")
        except ImportError:
            print("uvloop not available, using default asyncio loop.")
    else:
        print("Running on Windows: using default event loop.")


if __name__ == "__main__":
    setup_event_loop()

    uvicorn.run(
        "src:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
