import os
import discord
from discord.ext import commands, tasks
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent
import asyncio
from datetime import timedelta

TOKEN = os.getenv("TOKEN")

LIVE_CHANNEL_ID = 1442092783690055803
POST_CHANNEL_ID = 1440717598831411382

TIKTOK_USERS = [
    "eli97xo",
    "vipexak"
]

ALLOWED_USERS = {
    662596869221908480
    1280038439202590802
}

PING_ROLE = "@everyone"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_videos = {}
live_sent = {}


def is_allowed():
    async def predicate(ctx):
        return ctx.author.id in ALLOWED_USERS

    return commands.check(predicate)


def get_latest_video(username):
    return None


@tasks.loop(minutes=1)
async def check_videos():

    channel = bot.get_channel(POST_CHANNEL_ID)

    for username in TIKTOK_USERS:

        latest_video = get_latest_video(username)

        if latest_video is None:
            continue

        if username not in last_videos:
            last_videos[username] = latest_video
            continue

        if latest_video != last_videos[username]:

            last_videos[username] = latest_video

            video_url = f"https://www.tiktok.com/@{username}/video/{latest_video}"

            await channel.send(
                f"{PING_ROLE}\n"
                f"📹 Neuer TikTok Post von **{username}**\n"
                f"{video_url}"
            )


async def start_live_client(username):

    client = TikTokLiveClient(unique_id=username)

    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):

        live_channel = bot.get_channel(LIVE_CHANNEL_ID)

        if live_sent.get(username):
            return

        live_sent[username] = True

        await live_channel.send(
            f"{PING_ROLE}\n"
            f"🔴 **{username}** ist jetzt LIVE!\n"
            f"https://www.tiktok.com/@{username}/live"
        )

    while True:
        try:
            live_sent[username] = False
            await client.start()

        except Exception as e:
            print(f"Live Error {username}: {e}")

        await asyncio.sleep(10)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    check_videos.start()

    for user in TIKTOK_USERS:
        bot.loop.create_task(start_live_client(user))



# MODERATION 


@bot.command()
@is_allowed()
async def ban(ctx, member: discord.Member, *, reason="Kein Grund angegeben"):

    await member.ban(reason=reason)

    await ctx.send(
        f"{member.mention} wurde gebannt.\nGrund: {reason}"
    )


@bot.command()
@is_allowed()
async def kick(ctx, member: discord.Member, *, reason="Kein Grund angegeben"):

    await member.kick(reason=reason)

    await ctx.send(
        f"{member.mention} wurde gekickt.\nGrund: {reason}"
    )


@bot.command()
@is_allowed()
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="Kein Grund angegeben"):

    duration = timedelta(minutes=minutes)

    await member.timeout(duration, reason=reason)

    await ctx.send(
        f"{member.mention} wurde für {minutes} Minuten getimeoutet.\nGrund: {reason}"
    )


@bot.command(name="rto")
@is_allowed()
async def remove_timeout(ctx, member: discord.Member):

    await member.timeout(None)

    await ctx.send(
        f"Timeout von {member.mention} wurde entfernt."
    )


@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CheckFailure):
        await ctx.send("Du darfst diesen Command nicht benutzen.")

    else:
        print(error)


bot.run(TOKEN)
