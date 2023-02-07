import asyncio

async def q(val, callback):
    # loop = asyncio.get_event_loop()
    # fut = loop.create_future()
    # fut.add_done_callback(cb)
    print(val)
    callback(val)
    # fut.set_result(val)

def cb(r):
    # r = fut.result()
    print(r, "world")
    # fut._loop.stop()

async def test():
    await q("hello", cb)

asyncio.run(test())

# loop = asyncio.get_event_loop()
# fut = loop.create_future()
# fut.add_done_callback(cb)
# loop.call_soon(q, "hello", fut)

# loop.run_forever()