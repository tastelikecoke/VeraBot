import json
import sys
import asyncio
import discord
import os.path

class ServerDataManager:
    def __init__(self):
        pass
    async def ask(self, server_data, client, service, message):
        if message.content.startswith(server_data.prefix):
            sys.stdout.flush()
            await client.send_message(message.channel, "hey!")

class ServerData:
    def __init__(self):
        self.server_id = "" # not serialized
        self.prefix = "!vera"

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
            self.list[key].prefix = data[key]["prefix"]

    def serialize(self):
        "save the class"
        data = {}
        with open("assets/data.json", "r") as data_file:
            data = json.loads(data_file.read())

        for id in self.list:
            if not id in data:
                data[id] = {}
            data[id]["prefix"] = self.list[id].prefix

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