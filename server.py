import json
import sys
import re
import asyncio
import discord
import os.path

class ServerDataManager:
    def __init__(self):
        self.police_refractory = 0
        self.loli_refractory = 0
        self.flammable_messages = []

    async def ask(self, server_data, client, service, message):
        if message.content == server_data.prefix:
            await client.send_message(message.channel, "hello de gozaru!")

        if message.content == "{0} help".format(server_data.prefix):
            await client.send_message(message.channel,\
                "Vera Bot only has three commands.\n !vera, !vera police, and !vera martial."\
            )

        if message.content == "{0} die".format(server_data.prefix):
            if message.author.name in ["tastelikenyan", "Rat", "Azel", "Shepy"]:
                await client.send_message(message.channel, "bye de gozaru🚓")
                waiting = await client.logout()
                sys.exit()
            else:
                await client.send_message(message.channel, "no de gozaru")

        if message.content.startswith("!vquote "):
            matcher = re.search(r"!vquote ([\S]+) ([\s\S]*)", message.content)

            if not matcher:
                await client.send_message(message.channel,\
                    embed=discord.Embed(title="Incorrect", description="wrong command."))
                return

            author = matcher.group(1).lower()
            quote = matcher.group(2)
            if author not in server_data.quotes:
                server_data.quotes[author] = {}
            discriminant = str(max([0,] + list(map(lambda x: int(x), list(server_data.quotes[author].keys())))) + 1)
            server_data.quotes[author][discriminant] = quote
            service.server_data_list.serialize()

            await client.send_message(message.channel,\
                embed=discord.Embed(title="Quoted \"{0} {1}\"".format(author, discriminant), description=quote))

        if message.content.startswith("!vunquote "):
            matcher = re.search(r"!vunquote ([\S]+) ([\S]+)", message.content)
            
            if not matcher:
                await client.send_message(message.channel,\
                    embed=discord.Embed(title="Incorrect", description="wrong command."))
                return

            author = matcher.group(1).lower()
            discriminant = matcher.group(2)
            quote = ""
            if author in server_data.quotes:
                if discriminant in server_data.quotes[author]:
                    quote = server_data.quotes[author][discriminant]
                    server_data.quotes[author].pop(discriminant)

            if quote == "":
                await client.send_message(message.channel,\
                    embed=discord.Embed(title="Not found", description="quote is nonexisting."))
            else:
                await client.send_message(message.channel,\
                    embed=discord.Embed(
                        title="{0} {1} deleted".format(author, discriminant),
                        description=quote))

            service.server_data_list.serialize()

        if message.content.startswith("!vquoteof"):
            matcher = re.search(r"!vquoteof ([\S]+) ([\S]+)", message.content)
            matcher_auth = re.search(r"!vquoteof ([\S]+)", message.content)

            if matcher:
                author = matcher.group(1).lower()
                discriminant = matcher.group(2)

                quote = ""
                if author in server_data.quotes:
                    if discriminant in server_data.quotes[author]:
                        quote = server_data.quotes[author][discriminant]

                if quote == "":
                    await client.send_message(message.channel,\
                        embed=discord.Embed(title="Not found", description="quote is nonexisting."))
                else:
                    await client.send_message(message.channel,\
                        embed=discord.Embed(
                            title="{0} {1}".format(author, discriminant),
                            description=quote))

            elif matcher_auth:
                author = matcher_auth.group(1).lower()
                author_quotes = ""

                if author in server_data.quotes:
                    author_quotes = server_data.quotes[author]
                
                    await client.send_message(message.channel,\
                        embed=discord.Embed(
                            title=author,
                            description="person has quotes ranging from {0} to {1}.".format(
                                min(list(map(lambda x: int(x), author_quotes.keys()))),
                                max(list(map(lambda x: int(x), author_quotes.keys()))),
                            )
                        )
                    )
            else:
                await client.send_message(message.channel,\
                    embed=discord.Embed(
                        title="Quotes",
                        description="\n".join(server_data.quotes.keys())
                    )
                )

        if message.content.startswith("{0} embody".format(server_data.prefix)):
            if True not in map(lambda x: x.name == "Vera Bot", message.author.roles):
                await client.send_message(message.channel,\
                    "You don't own me de gozaru🚓 get the Vera Bot role first")
                return
            else:
                embodiment = message.content[len("{0} embody".format(server_data.prefix)):]
                if len(embodiment) > 0:
                    await client.send_message(message.channel,\
                        embodiment)
                await client.delete_message(message)


        if message.content == "{0} police".format(server_data.prefix):
            if True not in map(lambda x: x.name == "Vera Bot", message.author.roles):
                await client.send_message(message.channel,\
                    "You don't own me de gozaru🚓 get the Vera Bot role first")
                return
            if message.channel.id in server_data.police_channels:
                server_data.police_channels.remove(message.channel.id)
                self.police_refractory = 0
                service.server_data_list.serialize()
                await client.send_message(message.channel,\
                    "police gone de gozaru🚓")
            else:
                self.police_refractory = 0
                server_data.police_channels.append(message.channel.id)
                service.server_data_list.serialize()
                await client.send_message(message.channel,\
                    "police active de gozaru🚓")

        if message.content == "{0} martial".format(server_data.prefix):
            if True not in map(lambda x: x.name == "Vera Bot", message.author.roles):
                await client.send_message(message.channel,\
                    "You don't own me de gozaru🚓 get the Vera Bot role first")
                return
            server_data.militancy = not server_data.militancy
            service.server_data_list.serialize()
            if server_data.militancy:
                await client.send_message(message.channel,\
                    "ok, will be deleting messages de gozaru🚓")
            else:
                await client.send_message(message.channel,\
                    "ok, won't be deleting messages de gozaru🚓")

        if message.channel.id in server_data.police_channels:

            matcher = re.search(r"(?:http(?:s)?://)..+", message.content)
            loli_matcher = re.search(r".*I .*loli.*", message.content)
            oppai_matcher = re.search(r".*oppai.*loli.*", message.content)

            if self.loli_refractory <= 0:
                if loli_matcher:
                    await client.add_reaction(message, "🚓")
                    await client.send_message(message.channel,\
                        "🚓 stop, this is the loli police de gozaru 🚓")
                    self.loli_refractory += 25
                if oppai_matcher:
                    await client.add_reaction(message, "🚓")
                    await client.send_message(message.channel,\
                        "🚓 stop, this is the shit taste police de gozaru 🚓")
                    self.loli_refractory += 25

            else:
                self.loli_refractory -= 1

            # if militancy is active
            if (len(message.attachments) > 0 or matcher) and server_data.militancy:
                await client.send_message(message.author,\
                    "do not post images & links. You have been warned.🚓")
                await client.delete_message(message)
            # control image posting
            elif self.police_refractory <= 0:
                for flammable_message in self.flammable_messages:
                    try:
                        await client.delete_message(flammable_message)
                    except discord.errors.NotFound:
                        pass
                self.flammable_messages = []

                if len(message.attachments) > 0 or matcher:
                    await client.add_reaction(message, "🚓")
                    new_message = await client.send_message(message.channel,\
                        "<@{0}> do not post images & links in {1} 🚓 post in #multimedia-links instead".format(
                            message.author.id, message.channel.name))
                    self.flammable_messages.append(new_message)
                    self.police_refractory += 13
            else:
                self.police_refractory -= 1

class ServerData:
    def __init__(self):
        self.server_id = "" # not serialized
        self.prefix = "!vera"
        self.police_channels = []
        self.quotes = {}
        self.demerits = {}
        self.militancy = True

class ServerDataList:

    def __init__(self):
        self.list = {}
        self.deserialize()

    def get_server(self, id):
        if not id in self.list:
            self.list[id] = ServerData()
            self.serialize()
        return self.list[id]

    def deserialize(self):
        "load the class"

        if not os.path.isfile("assets/data.json"):
            with open("assets/data.json", "w") as data_file:
                data_file.write(json.dumps({}))

        data = {}
        with open("assets/data.json", "r") as data_file:
            data = json.loads(data_file.read())

        for key in data:
            self.list[key] = ServerData()
            self.list[key].server_id = key
            try:
                self.list[key].prefix = data[key]["prefix"]
                self.list[key].militancy = data[key]["militancy"]
                self.list[key].demerits = data[key]["demerits"]
                self.list[key].police_channels = data[key]["police_channels"]
                self.list[key].quotes = data[key]["quotes"]
            except KeyError:
                pass

    def serialize(self):
        "save the class"
        data = {}
        with open("assets/data.json", "r") as data_file:
            data = json.loads(data_file.read())

        for id in self.list:
            if not id in data:
                data[id] = {}
            data[id]["prefix"] = self.list[id].prefix
            data[id]["police_channels"] = self.list[id].police_channels
            data[id]["militancy"] = self.list[id].militancy
            data[id]["demerits"] = self.list[id].demerits
            data[id]["quotes"] = self.list[id].quotes

        with open("assets/data.json", "w") as data_file:
            data_file.write(json.dumps(data))

class PrivateManager:
    def __init__(self):
        pass
    async def ask(self, client, service, message):
        matcher = re.search(r"!announce (.+)", message.content)
        if matcher:
            announcement = matcher.group(1)
            for data in service.server_data_list.list.values():
                for channel in data.police_channels:
                    if len(announcement) > 0:
                        await client.send_message(client.get_channel(channel), announcement)
class Secret:
    def __init__(self):
        self.token = ""
        self.deserialize()

    def deserialize(self):
        "load the class"
        data = {}
        with open("assets/secrets.json", "r") as secrets_file:
            data = json.loads(secrets_file.read())
        self.token = data["token"]
    def serialize(self):
        "save the class"
        data = {}
        data["token"] = self.token
        with open("assets/secrets.json", "w") as secrets_file:
            secrets_file.write(json.dumps(data))

class Service:
    def __init__(self):
        self.client = discord.Client()
        self.secret = Secret()
        self.private_manager = PrivateManager()
        self.server_data_list = ServerDataList()
        self.manager = ServerDataManager()

        @self.client.event
        async def on_ready():
            """ what happens at start """
            print('Logged in as {0}'.format(self.client.user.name))
            sys.stdout.flush()

        @self.client.event
        async def on_message(message):
            if not message.server:
                await self.private_manager.ask(self.client, self, message)
            else:
                server_data = self.server_data_list.get_server(message.server.id)
                await self.manager.ask(server_data, self.client, self, message)

        self.client.run(self.secret.token)

if __name__ == "__main__":
    Service()