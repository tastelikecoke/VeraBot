import json
import sys
import re
import asyncio
import discord
import os.path

class ServerDataManager:
    def __init__(self):
        self.police_refractory = 0
        self.flammable_messages = []

    async def ask(self, server_data, client, service, message):
        if message.content == server_data.prefix:
            await client.send_message(message.channel, "hello de gozaru!")

        
        if message.content == "{0} help".format(server_data.prefix):
            await client.send_message(message.channel,\
                "Vera Bot only has three commands.\n !vera, !vera police, and !vera martial."\
            )

        if message.content == "{0} die".format(server_data.prefix):
            if message.author.name == "tastelikenyan":
                await client.send_message(message.channel, "bye de gozaru🚓")
                waiting = await client.logout()
                sys.exit()
            else:
                await client.send_message(message.channel, "no de gozaru")

        if message.content == "{0} police".format(server_data.prefix):
            if True not in map(lambda x: x.name == "Vera Bot", message.author.roles):
                await client.send_message(message.channel, "You don't own me de gozaru🚓 get the Vera Bot role first")
                return
            if message.channel.id in server_data.police_channels:
                server_data.police_channels.remove(message.channel.id)
                self.police_refractory = 0
                service.server_data_list.serialize()
                await client.send_message(message.channel, "police gone de gozaru🚓")
            else:
                self.police_refractory = 0
                server_data.police_channels.append(message.channel.id)
                service.server_data_list.serialize()
                await client.send_message(message.channel, "police active de gozaru🚓")
        
        if message.content == "{0} martial".format(server_data.prefix):
            if True not in map(lambda x: x.name == "Vera Bot", message.author.roles):
                await client.send_message(message.channel, "You don't own me de gozaru🚓 get the Vera Bot role first")
                return
            server_data.militancy = not server_data.militancy
            service.server_data_list.serialize()
            if server_data.militancy:
                await client.send_message(message.channel, "ok, will be deleting messages de gozaru🚓")
            else:
                await client.send_message(message.channel, "ok, won't be deleting messages de gozaru🚓")

        if message.channel.id in server_data.police_channels:

            matcher = re.search(r"(?:http(?:s)?://)..+", message.content)

            # if militancy is active
            if (len(message.attachments) > 0 or matcher) and server_data.militancy:
                await client.send_message(message.author, "do not post images & links. You have been warned.🚓")
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
                    new_message = await client.send_message(message.channel, "do not post images & links in {0} 🚓 post in #multimedia-links instead".format(message.channel.name))
                    self.flammable_messages.append(new_message)
                    self.police_refractory += 13
            else:
                self.police_refractory -= 1

class ServerData:
    def __init__(self):
        self.server_id = "" # not serialized
        self.prefix = "!vera"
        self.police_channels = []
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

        with open("assets/data.json", "w") as data_file:
            data_file.write(json.dumps(data))

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
                pass
            else:
                server_data = self.server_data_list.get_server(message.server.id)
                await self.manager.ask(server_data, self.client, self, message)

        self.client.run(self.secret.token)

if __name__ == "__main__":
    Service()