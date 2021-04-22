import os
import logging

from flask import Flask

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, template_folder=os.environ.get('TEMPLATE_FOLDER', 'templates')) 
config_path = os.path.join('config', os.environ.get('WEB_CONFIG_FILE', 'config.py'))
app.config.from_pyfile(config_path)
logging.info(f'loaded configuration from {config_path}')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

from web.views import *
