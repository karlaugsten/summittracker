"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)

import SummitServer.views
import SummitServer.api
