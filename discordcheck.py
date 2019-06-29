import schedule
import discord
import time
import requests
from datetime import date
import pymssql
import re
from config import settings, colorPick


class DiscordCheck(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def check_members(self):
        # Open SQL connection
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor()
        # get list of clans to test against today
        cursor.execute("SELECT * FROM rcs_vwDiscordClans")
        fetch = cursor.fetchall()
        clans_dict = [{"shortName": row[1], "leaderTag": row[2], "clanName": row[3]} for row in fetch]
        # get full list of RCS clans
        cursor.execute("SELECT shortName FROM rcs_data")
        fetch = cursor.fetchall()
        clan_list = []
        for row in fetch:
            if "/" in row[0]:
                for clan in row[0].split("/"):
                    clan_list.append(clan)
            else:
                clan_list.append(row[0])
        conn.close()

        # Webhook just for Ninja Killers/Faceless Ninjas
        ninja_hook = "https://discordapp.com/api/webhooks/486699745272659997/IYifPjAKu3WvUMHyq-Hh1hK7Dn6gKEBDo2Tv3dQgE5UcusxrngpQq60MUr8vhp4ZJeMK"

        guild = self.get_guild(settings['discord']['rcsGuildId'])
        member_role = guild.get_role(296416358415990785)
        members = guild.members
        danger_bot = guild.get_channel(settings['rcsChannels']['botDev'])
        bot_dev = guild.get_channel(settings['rcsChannels']['botDev'])
        mod_chat = guild.get_channel(settings['rcsChannels']['botDev'])

        # Loop through clans. Build list of members that do not have the guest role.
        for clan in clans_dict:
            clan_members = []
            if '/' in clan['shortName']:
                short_list = clan['shortName'].split('/')
            else:
                short_list = [clan['shortName']]
            for clanName in short_list:
                if clanName != 'reddit':
                    regex = r"\W" + clanName + "\W|\W" + clanName + "\Z"
                else:
                    regex = r"\Wreddit[^\s]"
                for member in members:
                    if member_role in member.roles:
                        # if clan name is found in Discord name, we append to list and continue to next item in list
                        if re.search(regex, member.display_name, re.IGNORECASE) is not None:
                            # Consider replacing double bars here using replace()
                            clan_members.append('Discord Name: ' + member.display_name)

            if clan_members:
                # Discord Payload here
                text_string = (f"\n<@!{clan['leaderTag']}> Please check the following list of members "
                               f"to make sure everyone is still in your clan (or feeder). "
                               f"If someone is no longer in your clan, please notify a Chat "
                               f"Mod to have their Member role removed.")
                await danger_bot.send(text_string)
                text_string = ""
                for member in clan_members:
                    text_string += f"  {member}\n"
                embed = discord.Embed(color=colorPick(181, 0, 0))
                embed.add_field(name=f"**Results for {clan['clanName']}**\n",
                                value=text_string,
                                inline=False)
                await danger_bot.send(embed=embed)
                # send data to Ninjas via webhook
                if clan['clanName'] in ["Ninja Killers", "Faceless Ninjas"]:
                    payload = {
                        "embeds": [{
                            "color": colorPick(181, 0, 0),
                            "fields": [
                                {"name": f"**Results for {clan['clanName']}**\n", "value": text_string, "inline": False}
                            ]
                        }]
                    }
                    requests.post(ninja_hook, json=payload)
            else:
                await bot_dev.send(f"No members for {clan['clanName']}")

        # Once a week, we check for any users with the Members role that aren't otherwise connected to a clan
        # catching some false once since people identify their clans differently
        if date.today().weekday() == 6:
            errors = []
            for member in members:
                if member_role in member.roles:
                    test = 0
                    for clan_name in clan_list:
                        if clan_name in member.display_name:
                            test = 1
                            break
                    if test == 0:
                        errors.append(f"<@{member.id}> did not identify with any clan.")
            if errors:
                text_string = "We found some Members without a clan:\n"
                for err in errors:
                    text_string += f"  {err}\n"
                await self.send_text(mod_chat, text_string)

    async def send_text(self, channel, text):
        """ Sends text to channel, splitting if necessary
        Discord has a 2000 character limit
        """
        if len(text) < 2000:
            await channel.send(text)
        else:
            coll = ""
            for line in text.splitlines(keepends=True):
                if len(coll) + len(line) > 1994:
                    await channel.send(coll)
                    coll = ""
                coll += line
            await channel.send(coll)

def job():
    client = DiscordCheck()
    client.run(settings['discord']['banToken'])

schedule.every().day.at("16:43").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
