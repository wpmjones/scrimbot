import schedule
import discord
import time
from config import settings


class DiscordCheck(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.check_members())

    async def check_members(self):
        await self.wait_until_ready()
        print("inside check members")


def job():
    client = DiscordCheck()
    client.run(settings['discord']['banToken'])


schedule.every(20).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
