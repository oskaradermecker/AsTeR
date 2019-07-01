# Author:  DINDIN Meryll
# Date:    28 June 2019
# Project: AsTeR

import io
import os
import time
import yaml
import json
import wave

# Rev.ai package
from rev_ai import apiclient
# Google Cloud package
from google.oauth2 import service_account
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
# IBM Watson package
from watson_developer_cloud import SpeechToTextV1