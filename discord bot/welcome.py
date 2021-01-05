import discord
import datetime
import random
intents = discord.Intents.all()
client = discord.Client(intents=intents)

welcomeMessage = "welcome people" # Enter your welcome message here.
welcomeChannelID = 795482626394816523 # Enter the welcome channel's ID here.
botToken = "Nzk1NDgzNjEyODMzMTIwMjU3.X_KB2A.ZbBz_jNm-A95KtEjigeiO34ph50" # Enter your bot's token here.


# Logging information for start-up.
@client.event
async def on_ready():
    print("I'm all set as {0.user}.".format(client))
    if len(client.guilds) == 0:
        print("I'm not in any servers.")
    else:
        print("I'm in the server/servers:", end="")
        for item in client.guilds:
            print(" " + item.name, end="")
        print(".")


# Logs new users and sends the welcome message.
@client.event
async def on_member_join(member):
    ##需要开启intents权限，这个权限需要在dev的机器人设置哪里把intents的权限打开，不然会报错
    embed = discord.Embed(title=f"Welcome To Mafia Server, Be carefully or you will die",
                          color=random.randint(0, 0xFFFFFF))
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_author(name=member.name, icon_url=member.avatar_url)
    embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
    channel = client.get_channel(id=welcomeChannelID)
    await channel.send(embed=embed)
async def on_member_remove(member):
    print("a people {} remove".format(member))
    await client.get_channel(welcomeChannelID).send(welcomeMessage)

# A help message.
@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return

    if message.content == ('!help'):
        await client.get_channel(welcomeChannelID).send("this is help")  # Enter what you would like your help message to be here.


client.run(botToken)