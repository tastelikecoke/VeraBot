import json

with open("assets/secrets.json", "w") as secrets_file:
    secrets_file.write(json.dumps({"token": ""}))

with open("assets/data.json", "w") as data_file:
    data_file.write(json.dumps({}))
