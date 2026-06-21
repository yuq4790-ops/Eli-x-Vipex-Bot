from os.path import join
import os
import discord
from discord.ext import commands, tasks
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent
import asyncio
from datetime import timedelta
from discord import app_commands


TOKEN = os.getenv("TOKEN")

LIVE_CHANNEL_ID = 1442092783690055803
POST_CHANNEL_ID = 1440717598831411382

TIKTOK_USERS = [
    "eli97xo",
    "vipexak"
]


PING_ROLE = "@everyone"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

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



# MODERATION 
ALLOWED_USERS = { 
    1280038439202590802
}

@bot.tree.command(name="ban", description="Banning a User")
@app_command.describe(
    user="User you want to ban",
    grund="Reason for ban"
)
async def ban(
    interaction: discord.Interaction,
    user: discord.Member,
    grund: str = "No Reason"


):
    if interaction.user.id nit on ALLOWED_USERS:
        await interaction.response.send_message(
            "Not Allowed",
            ephemeral=True
        )
        return
                                            
    





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


WELCOME_CHANNEL_ID = 1470008906934648954

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            discord.ui.Button(
                label="Zur Verifizierung!",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/FKjSYygj2f"
            )
        )

        self.add_item(
            discord.ui.Button(
                label="Vipex Tiktok",
                style=discord.ButtonStyle.link,
                url="https://www.tiktok.com/@vipexak"
            )
        )

        self.add_item(
            discord.ui.Button(
                label="Elixo Tiktok",
                style=discord.ButtonStyle.link,
                url="https://www.tiktok.com/@eli97xo"
            )
        )


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    embed = discord.Embed(
        title="**Willkommen!**",
        description=(
            f"**Hey {member.mention}. Schön das du hier bist!**\n\n"
            "- **Info:**\n"
            "> Mit der Verifizierung stimmst du unserem Regelwerk zu.\n"
            "> Du kannst dieses jederzeit unter <#1440371432877199397> einsehen.\n\n"
            "- **Verifizierung:**\n"
            "> Bevor du richtig loslegen kannst, musst du dich noch freischalten,\n"
            "> um Zugriff auf alle Kanäle zu erhalten."
        ),
        color=discord.Color.blurple()
    )

    embed.set_image(
        url="https://cdn.discordapp.com/banners/1440371431991935169/54ccd3adb048eb0efde3097de052b5f4.webp?size=1024"
    )

    await channel.send(
        content=f"Willkommen {member.mention}!",
        embed=embed,
        view=WelcomeView()
    )



#----------------verify panel-------

GUILD_ID = 1440371431991935169

VERIFY_ROLE_ID = 1441758416292024445     
REMOVE_ROLE_ID = 1512604669426536549      


class VerifyPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verifizieren",
        style=discord.ButtonStyle.success,
        custom_id="verify_button"
    )
    async def verify_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        verify_role = interaction.guild.get_role(VERIFY_ROLE_ID)
        remove_role = interaction.guild.get_role(REMOVE_ROLE_ID)

        if verify_role is None:
            await interaction.response.send_message(
                "Verifizierungsrolle nicht gefunden.",
                ephemeral=True
            )
            return

        if verify_role in interaction.user.roles:
            await interaction.response.send_message(
                "Du bist bereits verifiziert.",
                ephemeral=True
            )
            return

        
        await interaction.user.add_roles(verify_role)

        
        if remove_role and remove_role in interaction.user.roles:
            await interaction.user.remove_roles(remove_role)

        await interaction.response.send_message(
            "Du wurdest erfolgreich verifiziert!",
            ephemeral=True
        )


@bot.tree.command(
    name="verifypanel",
    description="Erstellt das Verifizierungspanel",
    guild=discord.Object(id=GUILD_ID)
)
async def verifypanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Verifizierung",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Informationen",
        value=(
            "> Mit der Verifizierung stimmst du unserem\n"
            "> <#1440371432877199397> zu.\n\n"
            "> Nach erfolgreicher Verifizierung erhältst du\n"
            "> Zugriff auf alle Kanäle."
        ),
        inline=False
    )

    embed.set_image(
        url="https://cdn.discordapp.com/banners/1440371431991935169/54ccd3adb048eb0efde3097de052b5f4.webp?size=1024"
    )

    await interaction.channel.send(
        embed=embed,
        view=VerifyPanelView()
    )

    await interaction.response.send_message(
        "Verify Panel erstellt.",
        ephemeral=True
    )

#-------------Activity--------------------

statuses = [
    "discord.gg/skybase",
    "Hosted by Yuqii",
    "Skybase System",
    "🎉Giveaway Incoming!🎉",
    "Verify for Chatting!",
]

status_index = 0

@tasks.loop(seconds=2)
async def rotate_status():
    global status_index

    activity = discord.Activity(
        type=discord.ActivityType.listening,
        name=statuses[status_index]
    )

    await bot.change_presence(activity=activity)

    status_index = (status_index + 1) % len(statuses)


#-------------CALL--------------------------------------------
VOICE_CHANNEL_ID = 1513217517588582445


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


TARGET_USERS = [
    1325204584829947914,
]

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in TARGET_USERS:

       
        await message.reply("||Halt die fresse du fetter Bastard||")

        try:
          
            await message.author.timeout(
                timedelta(hours=1),
                reason="Automatischer Timeout"
            )

            
            await message.channel.send(
                f" {message.author.mention} der drecks Albaner wurde für **1 Stunde** getimeoutet. Halt das nächste mal deine fresse bitte"
            )

        except discord.Forbidden:
            await message.channel.send(
                "Timeout failed"
            )

        except Exception as e:
            print(f"Timeout Fehler: {e}")

    await bot.process_commands(message)


#-------------bot ready-------------
@bot.event
async def on_ready():

    bot.add_view(VerifyPanelView())

    try:
        synced = await bot.tree.sync(
            guild=discord.Object(id=GUILD_ID)
        )
        print(f"{len(synced)} Commands synchronisiert.")

    except Exception as e:
        print(f"Sync Fehler: {e}")

    print(f"Logged in als {bot.user}")

    if not check_videos.is_running():
        check_videos.start()

    for user in TIKTOK_USERS:
        bot.loop.create_task(start_live_client(user))

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

            # Nicht erneut verbinden, falls bereits verbunden
            if guild.voice_client is None:
                await channel.connect()
                print(f"Verbunden mit {channel.name}")
            else:
                print("Bot ist bereits in einem Voice Channel.")

    except Exception as e:
        print(f"Voice Fehler: {e}")

        print(discord.__version__)
bot.run(TOKEN)
