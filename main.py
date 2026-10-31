from os.path import join
import os
import discord
from discord.ext import commands, tasks
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent
import asyncio
from datetime import timedelta
from discord import app_commands
from TikTokLive.client.errors import UserOfflineError
import TikTokLive


TOKEN = os.getenv("TOKEN")

LIVE_CHANNEL_ID = 1564335456718688427


TIKTOK_USERS = [
    "calli_eh",
    "vipexak"
   
]


PING_ROLE = "@everyone"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

live_sent = {}
live_tasks_started = False

def is_allowed():
    async def predicate(ctx):
        return ctx.author.id in ALLOWED_USERS

    return commands.check(predicate)




async def start_live_client(username):
    client = TikTokLiveClient(unique_id=username)

    while True:
        try:
            is_live = await client.is_live()

            if is_live:
                if not live_sent.get(username, False):
                    live_sent[username] = True

                    channel = bot.get_channel(LIVE_CHANNEL_ID)

                    await channel.send(
                        f"{PING_ROLE}\n"
                        f"🔴 **{username}** ist jetzt LIVE!\n"
                        f"https://www.tiktok.com/@{username}/live"
                    )

                    print(f"{username} ist LIVE")

            else:
                if live_sent.get(username, False):
                    print(f"{username} ist offline")

                live_sent[username] = False

        except Exception as e:
            print(f"{username}: {e}")

        await asyncio.sleep(30)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None, *, note=None):
    if channel is None:
        channel = ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(
        ctx.guild.default_role,
        overwrite=overwrite
    )
    embed = discord.Embed(
        title="Channel locked",
        color=discord.Color.dark_purple()
    )
    embed.add_field(
        name="Channel",
        value=channel.mention,
        inline=False
    )
    embed.add_field(
        name="locked from",
        value=ctx.author.mention,
        inline=False
    )
    embed.add_field(
        name="Notice",
        value=note if note else "No Notice.",
        inline=False
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    if ctx.guild.banner:
        embed.set_image(url=ctx.guild.banner.url)

    embed.set_footer(
        text=f"{ctx.guild.name}"
    )
    await ctx.send(embed=embed)


       #-------------welcome panel-----------


WELCOME_CHANNEL_ID = 1564334940408258683

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    container = discord.ui.Container(
        
        discord.ui.TextDisplay(
            "# Willkommen!\n"
            f"**Hey {member.mention}. Schön das du hier bist!**\n"
        ),
        discord.ui.Separator(),
        discord.ui.Section(
            discord.ui.TextDisplay(

                "- **Info:**\n"
                "> Mit der Verifizierung stimmst du unserem Regelwerk zu.\n"
                "> Du kannst dieses jederzeit unter <#1564891463081402448> einsehen.\n\n"
                "- **Verifizierung:**\n"
                "> Bevor du richtig loslegen kannst, musst du dich noch freischalten,\n"
                "> um Zugriff auf alle Kanäle zu erhalten."
            ),
            accessory=discord.ui.Thumbnail(
                media="https://cdn.discordapp.com/banners/1535780243703472220/0fe8419d285cbc022a1c7428b3f42615.webp?size=1024"
            )
        ),

        discord.ui.Separator(),

        discord.ui.ActionRow(
            discord.ui.Button(
                label="Vipex TikTok",
                style=discord.ButtonStyle.link,
                url="https://www.tiktok.com/@vipexak"
            ),
            discord.ui.Button(
                label="Calluci TikTok",
                style=discord.ButtonStyle.link,
                url="https://www.tiktok.com/@calli_eh"
            ),
            discord.ui.Button(
                label="Zum Regelwerk",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/ScURUHSkgZ"
            )
        )
    )

    view = discord.ui.LayoutView()
    view.add_item(container)
    await channel.send(view=view)

#----------------verify panel-------



#-------------Activity--------------------

statuses = [
    "discord.gg/aslans",
    "Hosted by Yuqii",
    "Aslans Assistant",
    "Giveaway Incoming!",
    "Verify for Chatting!",
]

status_index = 0

@tasks.loop(seconds=2)
async def rotate_status():
    global status_index

    activity = discord.Activity(
        type=discord.ActivityType.streaming,
        name=statuses[status_index]
    )

    await bot.change_presence(activity=activity)

    status_index = (status_index + 1) % len(statuses)


#-------------CALL--------------------------------------------
@bot.event
async def on_ready():
    activity = discord.Game(name="Niggas")
    await bot.change_presence(
        status=discord.Status.streaming,
        activity=activity
    )





VOICE_CHANNEL_ID = 1566120649053708368


@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and after.channel is None:
        try:
            guild = await bot.fetch_guild(GUILD_ID)
            channel = bot.get_channel(VOICE_CHANNEL_ID)
            if channel is None:
                channel = await bot.fetch_channel(VOICE_CHANNEL_ID)

            if channel:
                await channel.connect()
                print("Automatisch neu verbunden.")
        except Exception as e:
            print(f"Reconnect Fehler: {e}")




# -------anti webhook
TRUSTED_ROLE_ID = 1564750335430369300

@bot.event
async def on_webhooks_update(channel: discord.abc.GuildChannel):
    guild = channel.guild

    webhooks = await guild.webhooks()

    for webhook in webhooks:
        if webhook.channel_id != channel.id:
            continue

        if webhook.user is None:
            continue

        member = guild.get_member(webhook.user.id)
        if member is None:
            continue

        if all(role.id != TRUSTED_ROLE_ID for role in member.roles):
            try:
                await webhook.delete(reason="Webhook forbidden")
                print(f"Webhook from {member} deleted.")
            except discord.Forbidden:
                print("No perms to delete Webhook.")


#-------------bot ready-------------
@bot.event
async def on_ready():
    global live_tasks_started

    bot.add_view(VerifyPanel())

    try:
        synced = await bot.tree.sync(
            guild=discord.Object(id=GUILD_ID)
        )
        print(f"{len(synced)} Commands synchronisiert.")
    except Exception as e:
        print(f"Sync Fehler: {e}")

    print(f"Logged in als {bot.user}")
    print(TikTokLive.__version__)

    # TikTok-Tasks nur EINMAL starten
    if not live_tasks_started:
        for user in TIKTOK_USERS:
            print(f"Starte TikTok-Task für {user}")
            asyncio.create_task(start_live_client(user))

        live_tasks_started = True

    if not rotate_status.is_running():
        rotate_status.start()

    # Voice Channel verbinden
    try:
        guild = bot.get_guild(GUILD_ID)

        if guild is None:
            print("Guild nicht gefunden.")
            return

        channel = guild.get_channel(VOICE_CHANNEL_ID)

        if channel is None:
            print("Voice Channel nicht gefunden.")
            return

        if isinstance(channel, discord.VoiceChannel):
            vc = guild.voice_client

            if vc is None:
                await channel.connect()
                print(f"Verbunden mit {channel.name}")
            elif vc.channel.id != VOICE_CHANNEL_ID:
                await vc.move_to(channel)
                print(f"In {channel.name} verschoben.")
            else:
                print("Bot ist bereits im richtigen Voice Channel.")

    except Exception as e:
        print(f"Voice Fehler: {e}")

if __name__ == "__main__":
    bot.run(TOKEN)
