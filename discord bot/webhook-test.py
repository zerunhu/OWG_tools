url = "https://discord.com/api/webhooks/795903703613308939/gjxeG-gGWbH2QQllAnd7hVKku8WC44-DBUpUbL2wD22nF7rMCNsz5DkYW7X7VrOUjujQ"
import requests, json
header = {
    "Content-Type": "application/json",
    "charset": "utf-8"
}
embed = {
    "title" : "title-test",
    "description": "test-des",
    "color": 0x00ff00,
    "fields": [{
        "name": "f1",
        "value": "v1",
    },{
        "name": "f2",
        "value": "v2",
    }]
}
msg = {
    "username": "gopher",
    "avatar_url": "",
    "content": "The message to send",
    "embeds": [embed]
}
sendData = json.dumps(msg)
c = requests.post(url, data=sendData, headers=header)
print(c)