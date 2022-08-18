import aiohttp
import asyncio
from cs_bot.api_cs.api import RequestsCS

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
a = RequestsCS()


class AsynseRequests:

    def __init__(self, data):
        self.data = data


    async def get_page(self, session, parsing_adress, item):
        async with session.get(parsing_adress) as s:  #
            if s.status == 200:
                data = await s.json()
                print(data)
                item.id_sell = data['item_id']

    async def get_all(self, session):
        tasks = []
        for item in self.data:
            parsing_adress = a.sell(item)
            task = asyncio.create_task(self.get_page(session, parsing_adress, item))
            tasks.append(task)
        return await asyncio.gather(*tasks)

    async def main(self):
        async with aiohttp.ClientSession() as session:
            return await self.get_all(session)

    async def run(self):
        asyncio.run(self.main())