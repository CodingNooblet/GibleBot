import discord
from discord.ext import commands
from discord import Game
import asyncio
import os
import pickle
import sys
import tempfile
import time
import aiohttp
import logging
import random
import datetime
import pytesseract
import re
import json
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
import short_url

logging.basicConfig(filename='log0.log', level=logging.INFO)


def get_prefix(bot, message):
	server = message.server
	prefix = config["default_prefix"]
	return prefix


Giblebot = commands.Bot(command_prefix=get_prefix)
try:
	with open(os.path.join('data', 'memorydict'), "rb") as fd:
		Giblebot.memory_dict = pickle.load(fd)
	logging.info("memorydict Loaded Successfully")
except OSError:
	logging.info("memorydict Not Found - Looking for Backup")
	try:
		with open(os.path.join('data', 'memorydict_backup'), "rb") as fd:
			Giblebot.memory_dict = pickle.load(fd)
		logging.info("memorydict Backup Loaded Successfully")
	except OSError:
		logging.info("memorydict Backup Not Found - Creating New memorydict")
		Giblebot.memory_dict = {}
		with open(os.path.join('data', 'memorydict'), "wb") as fd:
			pickle.dump(Giblebot.memory_dict, fd, -1)
		logging.info("memorydict Created")

memory_dict = Giblebot.memory_dict

config = {}
pkmn_dict = {}
channel_dict = {}


# logger.exception(type(error).__name__, exc_info=error)
def load_config():
	global config
	global pkmn_dict
	with open("config.json", 'r') as fd:
		config = json.load(fd)
	with open("pkmn_name_number.json", 'r') as pd:
		pkmn_dict = json.load(pd)


load_config()


async def verify_poke_message(message):
	converted_message = (message.content).lower()
	pokemons = pkmn_dict.keys()
	occurence = true_count = 0
	messagecode = ''
	for word in converted_message.split():
		if word in pokemons:
			occurence = converted_message.count(word)
			true_count += occurence
			messagecode = pkmn_dict[word]
	while len(messagecode) < 3:
		messagecode = '0' + messagecode
	if (true_count is 1):
		await pokemon_image(messagecode, message)


async def verify_coords(message):
	converted_message = (message.content).lower()
	if (re.search('-?\d{1,2}.\d{4,8}(,|\s)\s?-?\d{2,3}.\d{4,8}', converted_message)):
		searchObject = re.search('-?\d{1,2}.\d{4,8}(,|\s)\s?-?\d{2,3}.\d{4,8}', converted_message)
		coords = searchObject.group()
		lat = re.split(', |,|\s', coords)[0]
		lng = re.split(', |,|\s', coords)[1]
		pass
	else:
		return
	channel = message.channel
	author = message.author
	server = channel.server
	width = '250'
	height = '150'
	maptype = 'roadmap'
	zoom = '15'

	center = '{},{}'.format(lat, lng)
	query_center = 'center={}'.format(center)
	query_markers = 'markers=color:0x006B0B%7C{}'.format(center)
	query_size = 'size={}x{}'.format(width, height)
	query_zoom = 'zoom={}'.format(zoom)
	query_maptype = 'maptype={}'.format(maptype)
	
	map_ = ('https://maps.googleapis.com/maps/api/staticmap?' +
	        query_center + '&' + query_markers + '&' +
	        query_maptype + '&' + query_size + '&' + query_zoom)
	api_key = 'AIzaSyDfqT9v-1PnYOZbOAubTEYkfqnwRuM28CY'
	if api_key is not None:
	    map_ += ('&key=%s' % api_key)
	    # log.debug("API_KEY added to static map url.")
	# return map_
	#print(lat + lng)
	#print(map_)
	maplink = 'https://www.google.com/maps/search/?api=1&query=' + lat + ',' + lng
	embed = discord.Embed(title="Go to green marker!", colour=discord.Colour.green(), url=maplink)
	embed.set_image(url=map_)
	#embedmaplink = str({"embeds":[{"thumbnail":{"url": map_}}]})
	messagesend = "Coordinates detected. Generating map link : "
	await Giblebot.send_message(message.channel, content=messagesend, embed=embed)
	return


# print(config)
async def pokemon_image(messagecode, message):
	"""Sends the animated gif of pokemon by number called.

	When the name of the pokemon appears in a message
	Works anywhere. Send gif of pokemon."""
	channel = message.channel
	author = message.author
	combo = messagecode
	server = channel.server
	time_now = datetime.datetime.now()
	# time_last_sent, time_cooldown = None
	if (combo in memory_dict.keys()):
		time_last_sent = memory_dict[combo]
		time_cooldown = time_last_sent - datetime.timedelta(minutes=-10)
		if (time_now > time_cooldown):
			memory_dict[combo] = time_now
			pass
		else:
			return
	elif (combo not in memory_dict.keys()):
		memory_dict[combo] = time_now
	# first randomize luck, then check for file
	luck = random.randint(1, 100)
	filelist = []
	filepathstring = ''
	if (luck < 5):
		filepathstring = '/apps/pythontestdrill/nonanimatedsprites/' + combo + 's.png'
	elif (luck > 90):
		filepathstring = '/apps/pythontestdrill/nonanimatedsprites/' + combo + '.png'
	elif (luck < 13):
		filepathstring = '/apps/pythontestdrill/animatedshinysprites2/'
		files = os.listdir(filepathstring)
		for filename in files:
			if combo in filename:
				filelist.append(filename)
		filepathstring = (filepathstring + (random.choice(filelist)))
		logging.info(filepathstring)
	else:
		filepathstring = '/apps/pythontestdrill/animatedsprites/'
		files = os.listdir(filepathstring)
		for filename in files:
			if combo in filename:
				filelist.append(filename)
		filepathstring = (filepathstring + (random.choice(filelist)))
		logging.info(filepathstring)
	# see if file exists, then send it
	if os.path.isfile(filepathstring):
		await Giblebot.send_file(channel, filepathstring)
	else:
		# await Giblebot.send_message(channel, ("Gible! Problem loading pokémon. Go yell at DallasPoGo!"))
		return


@Giblebot.event
async def on_ready():
	await Giblebot.change_presence(game=Game(name="with Sharpedo"))
	print("Logged in as " + Giblebot.user.name)


async def start_countdown(ctx, integer):
	while (integer > 0):
		message_content = "Lobby will begin in " + str(integer) + " seconds"
		if (integer < 11):
			message_content = "Lobby will begin in " + str(integer) + " seconds.  Too late to join."
		temporary_message = await Giblebot.send_message(ctx.message.channel, message_content)
		time_sent = datetime.datetime.now()
		time_complete = time_sent - datetime.timedelta(seconds=-integer)
		channel_dict[ctx.message.channel] = time_complete
		time.sleep(5)
		await Giblebot.delete_message(temporary_message)
		integer -= 5
		if (channel_dict[ctx.message.channel] == 000):
			await Giblebot.send_message(ctx.message.channel, "Countdown cancelled.")
			channel_dict[ctx.message.channel] = time_sent
			return
	await Giblebot.send_message(ctx.message.channel, "Fight started. Too late to join now.")


@Giblebot.command(pass_context=True, aliases=["l"])
async def lobbytimer(ctx):
	"""Start a timer that counts down seconds
	Usage: !l <seconds>

	Gible will start a second countdown timer.
	"""
	now = datetime.datetime.now()
	lobbytimer_split = ctx.message.clean_content.split()
	if (ctx.message.channel in channel_dict.keys()):
		if lobbytimer_split[1] == 'cancel':
			channel_dict[ctx.message.channel] = 000
			return
		time_complete = channel_dict[ctx.message.channel]
		if (now > time_complete):
			pass
		else:
			await Giblebot.send_message(ctx.message.channel, "A countdown is already active!")
			return
	if not lobbytimer_split[1].isdigit():
		await Giblebot.send_message(ctx.message.channel, "A number less than 120 is required")
		return
	else:
		integer = int(lobbytimer_split[1])
		if (integer > 120):
			await Giblebot.send_message(ctx.message.channel, "A number less than 120 is required")
			return
		else:
			await start_countdown(ctx, integer)
			return


@Giblebot.command(pass_context=True)
async def fingersnap(ctx):
	"""Restart after saving.
	Usage: ?fingersnap."""
	owner = discord.utils.get(Giblebot.get_all_members(), id=config["master"])
	if (ctx.message.author == owner):
		await Giblebot.send_message(ctx.message.channel, "Starting to rename all members...")
		members = ctx.message.channel.server.members
		for member in members:
			if (owner is member):
				pass
			else:
				await Giblebot.change_nickname(member, None)
		await Giblebot.send_message(ctx.message.channel, "All user nicknames have been reset!")
	else:
		await Giblebot.send_message(ctx.message.channel, "Unable to issue finger snap...")
		return


def checkDevRole(roles):
	for role in roles:
		if role.name == 'Team Deverock':
			logging.info(role.name)
			return True
	return False


def checkFamRole(roles):
	for role in roles:
		if role.name == 'fam':
			return True
	return False


@Giblebot.command(pass_context=True)
async def aprilfool(ctx):
	"""Restart after saving.
	Usage: ?aprilfool."""
	owner = discord.utils.get(Giblebot.get_all_members(), id=config["master"])
	randomnames = ['ConstipatedTrainer', 'TrainerTakingShit', 'FilthyCasual', 'TrainerOfShit', 'DumpsterFire']
	deverocknames = ['Team Rocket Grunt', 'Team Rocket Rookie']
	if (ctx.message.author == owner):
		await Giblebot.send_message(ctx.message.channel, "Starting to rename all members...")
		members = ctx.message.channel.server.members
		try:
			for member in members:
				if (owner is member):
					pass
				elif checkDevRole(member.roles):
					await Giblebot.change_nickname(member, random.choice(deverocknames))
				elif checkFamRole(member.roles):
					await Giblebot.change_nickname(member, 'T-R Balloon Rider')
				else:
					await Giblebot.change_nickname(member, random.choice(randomnames))
			await Giblebot.send_message(ctx.message.channel, "All user nicknames have been reset!")
		except Exception as e:
			await Giblebot.send_message(ctx.message.channel, "Name change interrupted...have to restart")
	else:
		await Giblebot.send_message(ctx.message.channel, "Unable to issue name change...")
		return


@Giblebot.command(pass_context=True)
async def restart(ctx):
	"""Restart after saving.
	Usage: !restart."""
	owner = discord.utils.get(Giblebot.get_all_members(), id=config["master"])
	await _save()
	if (ctx.message.author == owner):
		await Giblebot.send_message(ctx.message.channel, "Restarting...")
		Giblebot._shutdown_mode = 0
		await Giblebot.logout()
	else:
		await Giblebot.send_message(ctx.message.channel, "Ignoring request...")


@Giblebot.event
async def on_message(message):
	if not message.author.bot:
		await verify_poke_message(message)
		await verify_coords(message)
	if message.content.startswith(get_prefix(Giblebot, message)):
		# messagelist = message.content.split(" ")
		message.content = re.sub('/?', '', message.content)
		await Giblebot.process_commands(message)


async def _save():
	with tempfile.NamedTemporaryFile('wb', dir=os.path.dirname(os.path.join('data', 'memorydict')), delete=False) as tf:
		pickle.dump(memory_dict, tf, -1)
		tempname = tf.name
	try:
		os.remove(os.path.join('data', 'memorydict_backup'))
	except OSError as e:
		pass
	try:
		os.rename(os.path.join('data', 'memorydict'), os.path.join('data', 'memorydict_backup'))
	except OSError as e:
		if e.errno != errno.ENOENT:
			raise
	os.rename(tempname, os.path.join('data', 'memorydict'))


event_loop = asyncio.get_event_loop()
try:
	event_loop.run_until_complete(Giblebot.start(config['bot_token']))
except KeyboardInterrupt:
	_save()
	event_loop.run_until_complete(Giblebot.logout())
except Exception as e:
	_save()
	event_loop.run_until_complete(Giblebot.logout())
finally:
	pass
Giblebot.logout()
sys.exit(Giblebot)