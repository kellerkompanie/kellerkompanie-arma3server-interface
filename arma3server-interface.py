import json
import os.path

from flask import Flask

app = Flask(__name__)
settings = None


@app.route("/")
def hello():
    return "Hello World!"


def load_config():
    global settings

    if os.path.exists('config.json'):
        with open('data.txt') as json_file:
            settings = json.load(json_file)
    else:
        settings = {'host': '0.0.0.0', 'port': 5000,
                    'ssl_context_fullchain': '/etc/letsencrypt/live/server.kellerkompanie.com/fullchain.pem',
                    'ssl_context_privkey': '/etc/letsencrypt/live/server.kellerkompanie.com/privkey.pem'}

        with open('config.json', 'w') as outfile:
            json.dump(settings, outfile, sort_keys=True, indent=4)


if __name__ == "__main__":
    load_config()
    app.run(host=settings['host'], port=settings['port'],
            ssl_context=(settings['ssl_context_fullchain'], settings['ssl_context_privkey']))
