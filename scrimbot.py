import discord
import asyncio
import random
import coc
from loguru import logger
from config import settings, emojis
from discord.ext import tasks, commands
from datetime import datetime

clan_1 = "9LUR2PL9"  # Innuendo
# clan_1 = "PCJUCJGY"  # Team Reddit
clan_2 = "89QYUYRY"  # Aardvark
war_clans = [clan_1]
emoji_1 = emojis['other']['rcs']
emoji_2 = emojis['other']['rcs']

coc_client = coc.login(settings['supercell']['user'], settings['supercell']['pass'], key_names="vps")


class ScrimBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag = 1

        # start task
        self.scrim_loop.start()

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")
        print(self.user.id)
        print("------------")
        logger.add(self.send_log, level="DEBUG")
        logger.info("ScrimBot is now online")
        activity = discord.Activity(type=discord.ActivityType.watching, name="Pick Your Poison")
        await self.change_presence(status=discord.Status.online, activity=activity)

    def send_log(self, message):
        asyncio.ensure_future(self.send_message(message))

    async def send_message(self, message):
        await self.get_channel(settings['logChannels']['scrim']).send(f"`{message}`")

    @tasks.loop(minutes=10)
    async def scrim_loop(self):
        await self.wait_until_ready()
        channel_1 = self.get_channel(647916521309339698)
        # channel_2 = self.get_channel(637681714923044883)

        def star_phrases(stars):
            if stars == 3:
                # return ["Well that was just the bee's knees! 3 stars for you!", 
                #         "You pulled a blinder there! Nice 3 star attack!", 
                #         "That was a bloody good, three star attack!", 
                #         "You must be chuffed! 3 more stars for your clan.", 
                #         "That was a doodle!  Too easy!", 
                #         "You got the full Monty! Well done!", 
                #         "On it like a car bonnet!"]
                return ["Holy smokes!  You ripped out three stars on that one!", 
                        "I have no words. You are the reason I can wake up and face each day!", 
                        "Tearing down the walls and taking names with three stars.", 
                        "All hail the conquering heroes! Here are three stars for your clan!", 
                        "Nothing less than perfection!", "I want to be you!"]
            if stars == 2:
                # return ["Let's take a butchers and see if someone else can get all three stars.", 
                #         "You made a dog's dinner of that one.  Keep practicing.", 
                #         "That was almost mint. Guess someone else will have to nick that last star."]
                return ["Almost there! You will get them next time.", 
                        "At least we know where all the traps are now!", 
                        "So close, yet so far.", 
                        ("With a little coaching, I believe you will wreck that base next time. "
                         "Oh wait, there is no next time.")]
            if stars == 1:
                # return ["Nothing to see here.  Just your bog-standard one star.", 
                #         "Well that was a botch job. Wonky attack!", 
                #         "Budge up and make some room for someone who will get three stars!", 
                #         "Give me a tinkle on the blower and we'll chat about what went wrong there.", 
                #         "That is minging.  You can do better than that!", 
                #         "Is it me or was that attack a bit skew-whiff?", 
                #         "Well that really throws a spanner in the works. We're going to have to do better than that."]
                return ["Perhaps another strategy next time.", 
                        "We are going to need some clean up on aisle 1.", 
                        "May I recommend a good tutorial or perhaps a YouTube channel?",
                        "I'm doing a little quick math here and I'm not sure that's going to add to the win column."
                        "You are going to need more stars than that if you want to win this war!"]
            if stars == 0:
                # return ["Kill the CC. Kill the heroes. Bob's your uncle. Wreck the base.  Better luck next time.", 
                #         "You dropped a clanger there. Ask for help next time!", 
                #         "Well, that went a bit pear-shaped.", 
                #         "That just takes the biscuit!"]
                return ["Do you even clash, bro?", 
                        "That was a scout, right?", 
                        "Uh oh, I think we had a disco!",
                        "Uhhhhh, I'm just going to look the other way."
                        "It is OK.  Take a deep breath.  We didn't really need those stars anyway."]

        for war_clan in war_clans:
            war = await coc_client.get_current_war(f"#{war_clan}")
            if war_clan == clan_1:
                fname = "scrim1.txt"
                channel = channel_1
                clan_1_name = "Innuendo"
                clan_2_name = "Aardvark"
                print(fname)
            else:
                fname = "scrim2.txt"
                channel = channel_2
                clan_1_name = "Team Eddy"
                clan_2_name = "Team HODL"
            with open(fname, "r") as f:
                last_attack = int(float(f.readline()))
            new_last_attack = last_attack
            # if war.state == "preparation" and self.flag == 0:
            #     hours = war.start_time.seconds_until // 3600
            #     minutes = (war.start_time.seconds_until % 3600) // 60
            #     content = f"{emoji_1} **RCS vs. Roar's** {emoji_2}"
            #     content += (f"\n{hours:.0f} hours and {minutes:.0f} minutes until the war begins.\n"
            #                 f"Come back and watch the RCS take away their roar!")
            #     await channel.send(content)
            #     self.flag = 1
            #     logger.info("Flag switched to 1. Prep message should not show again.")
            if war.state in ['inWar', 'warEnded']:
                hours = war.end_time.seconds_until // 3600
                minutes = (war.end_time.seconds_until % 3600) // 60
                print(f"{hours:02}:{minutes:02} left in war")
                try:
                    for attack in war.attacks:
                        print("Processing war attacks...")
                        print(f"{attack.order}. {attack.attacker.town_hall} vs {attack.defender.town_hall}")
                        if attack.order > last_attack:
                            print(f"Processing attack #{attack.order}")
                            attacker_name = f"{str(attack.attacker.map_position)}. {attack.attacker.name}"
                            defender_name = f"{str(attack.defender.map_position)}. {attack.defender.name}"
                            if attack.defender.is_opponent:
                                attacker_name = f"{emoji_1} {attacker_name}"
                                defender_name = f"{emoji_2} {defender_name}"
                            else:
                                attacker_name = f"{emoji_2} {attacker_name}"
                                defender_name = f"{emoji_1} {defender_name}"
                            townhalls = f"({str(attack.attacker.town_hall)}v{str(attack.defender.town_hall)})"
                            line_1 = f"{attacker_name} just attacked {defender_name}"
                            stars = f"{emojis['stars']['new']*attack.stars}{emojis['stars']['empty']*(3-attack.stars)}"
                            line_2 = f"{stars} ({str(attack.destruction)}%) {townhalls}"
                            if attack.defender.is_opponent:
                                line_3 = f"{random.choice(star_phrases(attack.stars))}"
                            else:
                                # Should be "" if opponent is not RCS
                                line_3 = f"{random.choice(star_phrases(attack.stars))}"
                            content = f"{line_1}\n{line_2}\n{line_3}\n------------"
                            await channel.send(content)
                            logger.info(f"Attack #{attack.order} processed and posted.")
                            new_last_attack = attack.order
                            print(new_last_attack)
                except:
                    logger.exception("attack loop")
                if new_last_attack > last_attack:
                    if len(clan_1_name) > len(clan_2_name):
                        name_width = len(clan_1_name) + 3
                    else:
                        name_width = len(clan_2_name) + 3
                    zws = " \u200b"
                    clan_1_name = f"`{zws*(name_width-len(clan_1_name)-1)}{clan_1_name}{zws}`"
                    clan_2_name = f"`\u200b {clan_2_name}{zws*(name_width-len(clan_2_name)-2)}`"
                    clan_1_stars = f"{war.clan.stars}/{war.clan.max_stars}"
                    clan_1_stars = f"`{zws*(name_width-len(clan_1_stars)-1)}{clan_1_stars}{zws}`"
                    clan_2_stars = f"{war.opponent.stars}/{war.opponent.max_stars}"
                    clan_2_stars = f"`\u200b {clan_2_stars}{zws*(name_width-len(clan_2_stars)-2)}`"
                    if war.clan.destruction < 100:
                        width = 5
                        precision = 4
                        clan_1_per = f"{war.clan.destruction:{width}.{precision}}"
                    else:
                        clan_1_per = war.clan.destruction
                    clan_1_per = f"`{zws*(name_width-len(clan_1_per)-2)}{clan_1_per}%{zws}`"
                    if war.opponent.destruction < 100:
                        width = 4
                        precision = 4
                        clan_2_per = f"{war.opponent.destruction:{width}.{precision}}"
                    else:
                        clan_2_per = war.opponent.destruction
                    clan_2_per = f"`\u200b {clan_2_per}%{zws*(name_width-len(clan_2_per)-3)}`"
                    clan_1_attacks = f"{war.clan.attacks_used}/{war.team_size*2}"
                    clan_1_attacks = f"`{zws*(name_width-len(clan_1_attacks)-1)}{clan_1_attacks}{zws}`"
                    clan_2_attacks = f"{war.opponent.attacks_used}/{war.team_size*2}"
                    clan_2_attacks = f"`\u200b {clan_2_attacks}{zws*(name_width-len(clan_2_attacks)-2)}`"
                    content = f"{clan_1_name}{emojis['other']['gap']}{emojis['other']['rcs']}{emojis['other']['gap']}{clan_2_name}"
                    content += f"\n{clan_1_stars}{emojis['other']['gap']}{emojis['stars']['new']}{emojis['other']['gap']}{clan_2_stars}"
                    content += f"\n{clan_1_per}{emojis['other']['gap']}{emojis['other']['per']}{emojis['other']['gap']}{clan_2_per}"
                    content += f"\n{clan_1_attacks}{emojis['other']['gap']}{emojis['other']['swords']}{emojis['other']['gap']}{clan_2_attacks}"
                    await channel.send(content)
                    if war.end_time.seconds_until > 3600:
                        await channel.send(f"{war.end_time.seconds_until // 3600:.0f} hours left in war.")
                    else:
                        await channel.send(f"{war.end_time.seconds_until // 60:.0f} minutes left in war.")
                    try:
                        with open(fname, 'w') as f:
                            f.write(str(new_last_attack))
                    except:
                        logger.exception("Failed to write file")
            if datetime.now().hour == 4 and 0 < datetime.now().minute < 12:
                logger.debug(f"End of Loop | Flag = {self.flag}")


client = ScrimBot()
client.run(settings['discord']['scrimToken'])

