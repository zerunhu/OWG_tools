from prometheus_client import Gauge, Enum
import prometheus_client
import requests
from flask import Response, Flask

app = Flask(__name__)

g = Gauge('my_devops_healthy', 'the devops platform healthy check')

def healthy_check():
    try:
        res = requests.get("http://127.0.0.1:8002/api/healthy")
        if res.status_code == 200:
            g.set(1)
        else:
            g.set(0)
    except:
        g.set(0)

@app.route("/metrics")
def metrics():
    healthy_check()
    return Response(prometheus_client.generate_latest(g), mimetype="text/plain")

@app.route('/')
def index():
    return "Hello World"

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8066)