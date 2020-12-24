# -*- coding:utf-8 -*-
from flask import Flask, request
import requests
import json
app1 = Flask(__name__)
'''
脚本功能：从alertmanager获取到json文件，然后格式化过后再调用其他api进行处理。
'''
@app1.route('/', methods=['POST'])
def send():
    url = "https://oapi.dingtalk.com/robot/send?access_token=c59842fdd612c145b61782779cbe99615399a4190f1a488d0fe14d0bbbf042ce"
    header = {
        "Content-Type": "application/json",
        "charset": "utf-8"
    }
    data = json.loads(request.data)
    group_label = data.get("groupLabels")
    resolve_alerts = [alert for alert in data.get("alerts") if alert.get("status")=="resolved"]
    firing_alerts = [alert for alert in data.get("alerts") if alert.get("status")=="firing"]
    text = "### Group: {}\n".format(group_label.get("group"))
    if firing_alerts:
        text += "### [Firing:{}]\n".format(len(firing_alerts))
        for alert in firing_alerts:
            firing_alert_labels = ""
            for label in alert.get("labels").items():
                if label[0] == "alertname" or label[0] == "severity":
                    continue
                firing_alert_labels += "- {}: {}\n>".format(label[0],label[1])
            name = "#### {}\n".format(alert.get("labels").get("alertname"))
            summary = "#### [{}] {}\n".format(alert.get("labels").get("severity"),alert.get("annotations").get("summary"))
            start = "#### Firing time at: {}\n".format(alert.get("startsAt").split(".")[0])
            firing_labels = "#### Labels\n> {}".format(firing_alert_labels[:-1])
            text = text + name + summary + start + firing_labels
    if resolve_alerts:
        text += "### [Resolved:{}]\n".format(len(resolve_alerts))
        for alert in resolve_alerts:
            resolve_alert_labels = ""
            for label in alert.get("labels").items():
                if label[0] == "alertname" or label[0] == "severity":
                    continue
                resolve_alert_labels += "- {}: {}\n>".format(label[0], label[1])
            name = "#### {}\n".format(alert.get("labels").get("alertname"))
            summary = "#### [{}] {}\n".format(alert.get("labels").get("severity"),
                                              alert.get("annotations").get("summary"))
            resolve_labels = "#### Labels\n> {}".format(resolve_alert_labels[:-1])
            text = text + name + summary + resolve_labels
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "title": "Prometheus告警信息",
            "text": text
        },
        "at": {
            "isAtAll": False  # 在顶顶群里@人
        }
    }
    sendData = json.dumps(msg)
    c = requests.post(url, data=sendData, headers=header)
    return 'ok'

app1.run(debug=False,host='0.0.0.0',port=8060)