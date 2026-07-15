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


TOKEN = os.getenv("TOKEN")

LIVE_CHANNEL_ID = 1442092783690055803


TIKTOK_USERS = [
    "eli97xo",
    "vipexak"
   
]


PING_ROLE = "@everyone"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

live_sent = {}


def is_allowed():
    async def predicate(ctx):
        return ctx.author.id in ALLOWED_USERS

    return commands.check(predicate)




async def start_live_client(username):
    while True:
        client = TikTokLiveClient(unique_id=username)

        @client.on(ConnectEvent)
        async def on_connect(event):
            live_channel = bot.get_channel(LIVE_CHANNEL_ID)

            if live_sent.get(username, False):
                return

            live_sent[username] = True

            await live_channel.send(
                f"{PING_ROLE}\n"
                f"🔴 **{username}** ist jetzt LIVE!\n"
                f"https://www.tiktok.com/@{username}/live"
            )

        try:
            await client.start()

        except Exception as e:
    print(f"Live Error {username}: {type(e).__name__}: {e}")

    if "offline" in str(e).lower():
        live_sent[username] = False
        except Exception as e:
            print(f"Live Error {username}: {e}")

        finally:
            try:
                await client.disconnect()
            except:
                pass

        await asyncio.sleep(10)



# MODERATION 
ALLOWED_USERS = { 
    1280038439202590802
}

@bot.tree.command(name="ban", description="Banning a User")
@app_commands.describe(
    user="User you want to ban",
    grund="Reason for ban"
)
async def ban(
    interaction: discord.Interaction,
    user: discord.Member,
    grund: str = "No Reason"


):
    if interaction.user.id not in ALLOWED_USERS:
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
                "> Du kannst dieses jederzeit unter <#1440371432877199397> einsehen.\n\n"
                "- **Verifizierung:**\n"
                "> Bevor du richtig loslegen kannst, musst du dich noch freischalten,\n"
                "> um Zugriff auf alle Kanäle zu erhalten."
            ),
            accessory=discord.ui.Thumbnail(
                media="https://images-ext-1.discordapp.net/external/8JT06RtO_W4n7L4NoSclCNQtpFvMoYzWmsUdkoZRKNk/%3Fsize%3D1024/https/cdn.discordapp.com/banners/1440371431991935169/54ccd3adb048eb0efde3097de052b5f4.webp?format=webp"
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
                label="Elixo TikTok",
                style=discord.ButtonStyle.link,
                url="https://www.tiktok.com/@eli97xo"
            ),
            discord.ui.Button(
                label="Zur Verifizierung",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/FKjSYygj2f"
            )
        )
    )

    view = discord.ui.LayoutView()
    view.add_item(container)
    await channel.send(view=view)

#----------------verify panel-------

GUILD_ID = 1440371431991935169
VERIFY_ROLE_ID = 1441758416292024445
REMOVE_ROLE_ID = 1512604669426536549


class VerifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Verifizieren",
            style=discord.ButtonStyle.success,
            custom_id="verify_button"
        )

    async def callback(self, interaction: discord.Interaction):
        verify_role = interaction.guild.get_role(VERIFY_ROLE_ID)
        remove_role = interaction.guild.get_role(REMOVE_ROLE_ID)

        if verify_role is None:
            return await interaction.response.send_message(
                "Verifizierungsrolle nicht gefunden.",
                ephemeral=True
            )

        if verify_role in interaction.user.roles:
            return await interaction.response.send_message(
                "Du bist bereits verifiziert.",
                ephemeral=True
            )

        await interaction.user.add_roles(verify_role)

        if remove_role and remove_role in interaction.user.roles:
            await interaction.user.remove_roles(remove_role)

        await interaction.response.send_message(
            "Du wurdest erfolgreich verifiziert!",
            ephemeral=True
        )
class InfoButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Weitere Infos",
            style=discord.ButtonStyle.secondary,

        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "**Weitere Informationen**\n\n"
            "• Wir verlangen niemals auf fremde Links zu klicken.\n"
            "• Der Verify Button verlinkt dich zu keinem Link.\n"
            "• Die Verifzierung ist dafür da Fakeaccounts abzuwehren.",
            ephemeral=True
        )


class VerifyPanel(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        button = VerifyButton()
        info_button = InfoButton()
        container = discord.ui.Container()



        container.add_item(
            discord.ui.TextDisplay(
                "# Verifizierung\n"
                f"**Informationen**\n"
            )
        )
        container.add_item(discord.ui.Separator())

        container.add_item(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    "> Mit der Verifizierung stimmst du unserem\n"
                    "> <#1440371432877199397> zu.\n\n"
                    "> Nach erfolgreicher Verifizierung erhältst du\n"
                    "> Zugriff auf alle Kanäle."
                ),
                accessory=discord.ui.Thumbnail(
                    media="https://cdn.discordapp.com/banners/1440371431991935169/54ccd3adb048eb0efde3097de052b5f4.webp?size=1024"
                )
            )
        )

        container.add_item(discord.ui.Separator())

        verify_button = VerifyButton()
        info_button = InfoButton()

        row = discord.ui.ActionRow()
        row.add_item(verify_button)
        row.add_item(info_button)

        container.add_item(row)

        self.add_item(container)


@bot.tree.command(
    name="verifypanel",
    description="Erstellt das Verify Panel",
    guild=discord.Object(id=GUILD_ID)
)
async def verifypanel(interaction: discord.Interaction):
    await interaction.channel.send(view=VerifyPanel())

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

# -------anti webhook
TRUSTED_ROLE_ID = 1440421346810134801 

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

    bot.add_view(VerifyPanel())

    try:
        synced = await bot.tree.sync(
            guild=discord.Object(id=GUILD_ID)
        )
        print(f"{len(synced)} Commands synchronisiert.")

    except Exception as e:
        print(f"Sync Fehler: {e}")

    print(f"Logged in als {bot.user}")


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
       
        print(f"Live-Checker gestartet: {username}")
bot.run(TOKEN)
