import discord


class MyClient(discord.Client):
# "Nzk1NDgzNjEyODMzMTIwMjU3.X_KB2A.ZbBz_jNm-A95KtEjigeiO34ph50"

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            embed=discord.Embed(title="Tile", description="Desc", color=0x00ff00)
            embed.add_field(name="Fiel1", value="hi", inline=False)
            embed.add_field(name="Field2", value="hi2", inline=False)
            await message.channel.send(embed=embed)


client = MyClient()
client.run("Nzk1NDgzNjEyODMzMTIwMjU3.X_KB2A.ZbBz_jNm-A95KtEjigeiO34ph50")