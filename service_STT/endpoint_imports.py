# Author:  DINDIN Meryll
# Date:    28 June 2019
# Project: AsTeR

import argparse

from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
from flask_ngrok import run_with_ngrok
from werkzeug.utils import secure_filename
