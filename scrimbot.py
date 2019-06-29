import discord
import asyncio
import aiohttp
import random
from datetime import timedelta, datetime
from config import settings, emojis, colorPick

class ScrimBot(discord.Client):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # create background task
    self.bg_task = self.loop.create_task(self.my_background_task())

  async def on_ready(self):
    print(f"Logged in as {self.user.name}")
    print(self.user.id)
    print("------------")

  async def my_background_task(self):
    await self.wait_until_ready()
    channel = self.get_channel(582020768511295488)
    def build_attacks(d):
      attack_data = []
      for member in d['clan']['members']:
        try:
          attack_data.append({"clan": 1, "order": member['attacks'][0]['order'], "attackerTag": member['attacks'][0]['attackerTag'],"defenderTag":member['attacks'][0]['defenderTag'],"stars": member['attacks'][0]['stars'],"percent":member['attacks'][0]['destructionPercentage']})
        except:
          pass
        try:
          attack_Data.append({"clan": 1,"order": member['attacks'][1]['order'],"attackerTag":member['attacks'][1]['attackerTag'],"defenderTag":member['attacks'][1]['defenderTag'],"stars": member['attacks'][1]['stars'],"percent":member['attacks'][1]['destructionPercentage']})
        except:
          pass
      for member in d['opponent']['members']:
        try:
          attack_data.append({"clan": 2,"order": member['attacks'][0]['order'],"attackerTag":member['attacks'][0]['attackerTag'],"defenderTag":member['attacks'][0]['defenderTag'],"stars": member['attacks'][0]['stars'],"percent":member['attacks'][0]['destructionPercentage']})
        except:
          pass
        try:
          attack_data.append({"clan": 2,"order": member['attacks'][1]['order'],"attackerTag":member['attacks'][1]['attackerTag'],"defenderTag":member['attacks'][1]['defenderTag'],"stars": member['attacks'][1]['stars'],"percent":member['attacks'][1]['destructionPercentage']})
        except:
          pass
      return sorted(attack_data, key=lambda k: k['order'])

    def find_player(tag):
      player = []
      for member in data['clan']['members']:
        if member['tag'] == tag:
          player.append({"name": member['name'], "th": member['townhallLevel'], "map": member['mapPosition']})
          return player
      for member in data['opponent']['members']:
        if member['tag'] == tag:
          player.append({"name": member['name'], "th": member['townhallLevel'], "map": member['mapPosition']})
          return player

    def star_phrases(stars):
      if stars == 3:
        # return ["Well that was just the bee's knees! 3 stars for you!", "You pulled a blinder there! Nice 3 star attack!", "That was a bloody good, three star attack!", "You must be chuffed! 3 more stars for your clan.", "That was a doodle!  Too easy!", "You got the full Monty! Well done!", "On it like a car bonnet!"]
        return ["Holy smokes!  You ripped out three stars on that one!", "I have no words. You are the reason I can wake up and face each day!", "Tearing down the walls and taking names with three stars.", "All hail the conquering heroes! Here are three stars for your clan!", "Nothing less than perfection!", "I want to be you!"]
      if stars == 2:
        # return ["Let's take a butchers and see if someone else can get all three stars.", "You made a dog's dinner of that one.  Keep practicing.", "That was almost mint. Guess someone else will have to nick that last star."]
        return ["Almost there! You will get them next time.", "At least we know where all the traps are now!", "So close, yet so far.", "With a little coaching, I believe you will wreck that base next time. Oh wait, there is no next time."]
      if stars == 1:
        # return ["Nothing to see here.  Just your bog-standard one star.", "Well that was a botch job. Wonky attack!", "Budge up and make some room for someone who will get three stars!", "Give me a tinkle on the blower and we'll chat about what went wrong there.", "That is minging.  You can do better than that!", "Is it me or was that attack a bit skew-whiff?", "Well that really throws a spanner in the works. We're going to have to do better than that."]
        return ["Perhaps another strategy next time.", "We are going to need some clean up on aisle 1.", "May I recommend a good tutorial or perhaps a YouTube channel?", "You are going to need more stars than that if you want to win this war!"]
      if stars == 0:
        # return ["Kill the CC. Kill the heroes. Bob's your uncle. Wreck the base.  Better luck next time.", "You dropped a clanger there. Ask for help next time!", "Well, that went a bit pear-shaped.", "That just takes the biscuit!"]
        return ["Do you even clash, bro?", "That was a scout, right?", "Uh oh, I think we had a disco!", "It is OK.  Take a deep breath.  We didn't really need those stars anyway."]

    clan_1 = "9LUR2PL9"   # Innuendo
    clan_2 = "89QYUYRY"   # Aardvark
    emoji_1 = :airplane:
    emoji_2 = emojis['other']['tank']

    headers = {'Accept':'application/json','Authorization':'Bearer ' + settings['supercell']['apiKey']}
    url = f"https://api.clashofclans.com/v1/clans/%23{clan_1}/currentwar"

    while not self.is_closed():
      with open('scrim.txt', 'r') as f:
        last_attack = int(float(f.readline()))
      new_last_attack = last_attack
      async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
          if r.status == 200:
            data = await r.json()
          else:
            print("API pull failed.")
            print(r.status)
            print(r.text)
      timeAdjust = timedelta(hours=1)
      if data['state'] == 'preparation':
        time_to_start = datetime.strptime(data['startTime'], '%Y%m%dT%H%M%S.%fZ') - datetime.now() + timeAdjust
        content = f"**{data['clan']['name']} vs {data['opponent']['name']}**"
        content = f"\n{time_to_start} until war begins.\nCome back and watch the progress!"
      if data['state'] in ['inWar', 'warEnded']:
        print("in war")
        attacks = build_attacks(data)
        time_to_end = datetime.strptime(data['endTime'], '%Y%m%dT%H%M%S.%fZ') - datetime.now() + timeAdjust
        for attack in attacks:
          if attack['order'] > last_attack:
            attacker = find_player(attack['attackerTag'])
            defender = find_player(attack['defenderTag'])
            attacker_name = f"{str(attacker[0]['map'])}. {attacker[0]['name']}"
            defender_name = f"{str(defender[0]['map'])}. {defender[0]['name']}"
            if attack['clan'] == 1:
              attacker_name = f"{emoji_1} {attacker_name}"
              defender_name = f"{emoji_2} {defender_name}"
            else:
              attacker_name = f"{emoji_2} {attacker_name}"
              defender_name = f"{emoji_1} {defender_name}"
            townhalls = f"({str(attacker[0]['th'])}v{str(defender[0]['th'])})"
            line_1 = f"{attacker_name} just attacked {defender_name}"
            stars = f"{emojis['stars']['new']*attack['stars']}{emojis['stars']['empty']*(3-attack['stars'])}"
            line_2 = f"{stars} ({str(attack['percent'])}%) {townhalls}"
            if attack['clan'] == 1:
              line_3 = f"{random.choice(star_phrases(attack['stars']))}"
            else:
              line_3 = f"{random.choice(star_phrases(attack['stars']))}"
            content = f"{line_1}\n{line_2}\n{line_3}\n------------"
            await channel.send(content)
            new_last_attack = attack['order']
            print(new_last_attack)
        # war update
        data['clan']['name'] = "Air"
        data['opponent']['name'] = "Ground"
        if new_last_attack > last_attack:
          if len(data['clan']['name']) > len(data['opponent']['name']):
            nameWidth = len(data['clan']['name']) + 3
          else:
            nameWidth = len(data['opponent']['name']) + 3
          if data['clan']['stars'] < data['opponent']['stars']:
            color = colorPick(181,0,0)
          else:
            if data['clan']['stars'] > data['opponent']['stars']:
              color = colorPick(51,153,255)
            else:
              if data['clan']['destructionPercentage'] < data['opponent']['destructionPercentage']:
                color = colorPick(181,0,0)
              else:
                color = colorPick(51,153,255)
          zws = " \u200b"
          clan_1_name = f"`{zws*(nameWidth-len(data['clan']['name'])-1)}{data['clan']['name']}{zws}`"
          clan_2_name = f"`\u200b {data['opponent']['name']}{zws*(nameWidth-len(data['opponent']['name'])-2)}`"
          clan_1_stars = f"{data['clan']['stars']}/{data['teamSize']*3}"
          clan_1_stars = f"`{zws*(nameWidth-len(clan_1_stars)-1)}{clan_1_stars}{zws}`"
          clan_2_stars = f"{data['opponent']['stars']}/{data['teamSize']*3}"
          clan_2_stars = f"`\u200b {clan_2_stars}{zws*(nameWidth-len(clan_2_stars)-2)}`"
          if data['clan']['destructionPercentage'] < 100:
            width = 5
            precision = 4
            clan_1_per = f"{data['clan']['destructionPercentage']:{width}.{precision}}"
          else:
            clan_1_per = data['clan']['destructionPercentage']
          clan_1_per = f"`{zws*(nameWidth-len(clan_1_per)-2)}{clan_1_per}%{zws}`"
          if data['opponent']['destructionPercentage'] < 100:
            width = 4
            precision = 4
            clan_2_per = f"{data['opponent']['destructionPercentage']:{width}.{precision}}"
          else:
            clan_2_per = data['opponent']['destructionPercentage']
          clan_2_per = f"`\u200b {clan_2_per}%{zws*(nameWidth-len(clan_2_per)-3)}`"
          clan_1_attacks = f"{data['clan']['attacks']}/{data['teamSize']*2}"
          clan_1_attacks = f"`{zws*(nameWidth-len(clan_1_attacks)-1)}{clan_1_attacks}{zws}`"
          clan_2_attacks = f"{data['opponent']['attacks']}/{data['teamSize']*2}"
          clan_2_attacks = f"`\u200b {clan_2_attacks}{zws*(nameWidth-len(clan_2_attacks)-2)}`"
          content = f"{clan_1_name}{emojis['other']['gap']}{emojis['other']['rcs']}{emojis['other']['gap']}{clan_2_name}"
          content += f"\n{clan_1_stars}{emojis['other']['gap']}{emojis['stars']['new']}{emojis['other']['gap']}{clan_2_stars}"
          content += f"\n{clan_1_per}{emojis['other']['gap']}{emojis['other']['per']}{emojis['other']['gap']}{clan_2_per}"
          content += f"\n{clan_1_attacks}{emojis['other']['gap']}{emojis['other']['swords']}{emojis['other']['gap']}{clan_2_attacks}"
          await channel.send(content)
          with open('scrim.txt', 'w') as f:
            f.seek(0)
            f.write(str(new_last_attack))
            f.truncate()
        await asyncio.sleep(600)

def build_attacks(d):
  attack_data = []
  for member in d['clan']['members']:
    try:
      attack_data.append({"clan": 1, "order": member['attacks'][0]['order'], "attackerTag": member['attacks'][0]['attackerTag'],"defenderTag":member['attacks'][0]['defenderTag'],"stars": member['attacks'][0]['stars'],"percent":member['attacks'][0]['destructionPercentage']})
    except:
      pass
    try:
      attack_Data.append({"clan": 1, "order": member['attacks'][1]['order'], "attackerTag": member['attacks'][1]['attackerTag'], "defenderTag": member['attacks'][1]['defenderTag'], "stars": member['attacks'][1]['stars'], "percent": member['attacks'][1]['destructionPercentage']})
    except:
      pass
  for member in d['opponent']['members']:
    try:
      attack_data.append({"clan": 2, "order": member['attacks'][0]['order'], "attackerTag": member['attacks'][0]['attackerTag'], "defenderTag": member['attacks'][0]['defenderTag'], "stars": member['attacks'][0]['stars'], "percent": member['attacks'][0]['destructionPercentage']})
    except:
      pass
    try:
      attack_data.append({"clan": 2, "order": member['attacks'][1]['order'], "attackerTag": member['attacks'][1]['attackerTag'], "defenderTag": member['attacks'][1]['defenderTag'], "stars": member['attacks'][1]['stars'], "percent": member['attacks'][1]['destructionPercentage']})
    except:
      pass
  return sorted(attack_data, key=lambda k: k['order'])

client = ScrimBot()
client.run(settings['discord']['scrimToken'])

