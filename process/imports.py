# Author:  DINDIN Meryll
# Date:    02 May 2019
# Project: AsTeR

import sys
import tqdm
import time
import json
import yaml
import joblib
import branca
import requests
import warnings
import operator
import argparse
import geopandas
import scipy as sp
import scipy.ndimage
import numpy as np
import pandas as pd
import geojsoncontour

from io import StringIO
from PIL import Image
from pqdict import PQDict
from datetime import datetime
from scipy.io import wavfile
from scipy.signal import periodogram
from scipy.interpolate import interp1d
from scipy.interpolate import griddata

# API related packages

from rev_ai import apiclient
from ibm_watson import VisualRecognitionV3
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features
from watson_developer_cloud.natural_language_understanding_v1 import KeywordsOptions
from watson_developer_cloud.natural_language_understanding_v1 import SentimentOptions
from watson_developer_cloud.natural_language_understanding_v1 import EmotionOptions

# Visual packages

try:
    import folium
    import seaborn as sns
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    from folium import plugins
    from IPython.core.display import HTML
    from matplotlib.patches import Rectangle
    from matplotlib.animation import writers
    from matplotlib.animation import FuncAnimation
except:
    pass