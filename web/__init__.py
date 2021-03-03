import os
import logging

from flask import Flask

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder=os.environ.get('TEMPLATE_FOLDER', 'templates'))
config_path = os.path.join('config', os.environ.get('WEB_CONFIG_FILE', 'config.py'))
app.config.from_pyfile(config_path)
logger.info(f'loaded configuration from {config_path}')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == "__main__":
    app.run(host="0.0.0.0")

from web.views import *
