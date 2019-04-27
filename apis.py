# Author:  DINDIN Meryll
# Date:    26 April 2019
# Project: IBM Call for Code

import sys
import time
import json
import yaml
import joblib
import numpy as np

from io import StringIO
from rev_ai import apiclient
from pqdict import PQDict
from ibm_watson import VisualRecognitionV3
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud.websocket import RecognizeCallback, AudioSource
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features
from watson_developer_cloud.natural_language_understanding_v1 import KeywordsOptions
from watson_developer_cloud.natural_language_understanding_v1 import SentimentOptions
from watson_developer_cloud.natural_language_understanding_v1 import EmotionOptions

class ShortestPath:

    def __init__(self, graph):

        self.G = graph

    def dijkstra(self, origin, goal):

        inf = float('inf')
        D = {origin: 0}
        Q = PQDict(D)
        P = {}
        U = set(self.G.keys())

        while U:

            (v, d) = Q.popitem()
            D[v] = d
            U.remove(v)
            if v == goal: break

            for w in self.G[v]:
                if w in U:
                    d = D[v] + self.G[v][w]
                    if d < Q.get(w, np.inf):
                        Q[w] = d
                        P[w] = v

        v = goal
        path = [v]

        while v != origin:
            v = P[v]
            path.append(v) 

        path.reverse()

        return path

class Capturing(list):
    
    def __enter__(self):

        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    
    def __exit__(self, *args):

        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio 
        sys.stdout = self._stdout

class MyRecognizeCallback(RecognizeCallback):

    def __init__(self):

        RecognizeCallback.__init__(self)

    def on_data(self, data):

        print(json.dumps(data))
        
    def on_error(self, error):

        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):  

        print('Inactivity timeout: {}'.format(error))

class Voice_IBM:

    def __init__(self):

        self.stt = SpeechToTextV1(iam_apikey=crd['key'], url=crd['url'])
        self.stt.set_default_headers({'x-watson-learning-opt-out': 'true'})

    def request_to_vectors(self, json_request):

        txt, beg, end = [], [], []

        for sentence in json_request['results']:
            words = sentence['alternatives'][0]['timestamps']
            for word in words:
                txt.append(word[0])
                beg.append(word[1])
                end.append(word[2])

        out = dict()
        out['words'], out['starts'], out['ends'] = txt, beg, end

        return out

    def request(self, voice_path):

        with open(voice_path, 'rb') as audio_file:
            req = self.stt.recognize(audio=audio_file,
                                     content_type='audio/wav',
                                     word_alternatives_threshold=0.75)
            req = req.get_result()

        print(req)
        return self.request_to_vectors(req)

class Image_IBM:

    def __init__(self):

        self.api = VisualRecognitionV3('2018-03-19', iam_apikey=api_key)

    def request(self, image_path):

        with open(image_path, 'rb') as img:
            req = self.api.classify(images_file=img, images_filename=image_path)
    
        return req.get_result()['images'][0]['classifiers'][0]['classes']

class Senti_IBM:

    def __init__(self):

        self.api = NaturalLanguageUnderstandingV1(version='2018-11-16', iam_apikey=api_key, url=url_key)

    def request(self, message):

        with open('vocabulary.json') as raw: key = raw.readlines()[0].split(', ')

        fea = Features(sentiment=SentimentOptions(targets=key), 
                       keywords=KeywordsOptions(sentiment=True, emotion=True, limit=5))

        return self.api.analyze(text=message, features=fea).get_result()

class Voice_Rev:

    def __init__(self):

        self.stt = apiclient.RevAiAPIClient(key)

    def request_to_vectors(self, json_request):

        txt, beg, end = [], [], []

        for word in json_request['monologues'][0]['elements']:
            if word['type'] == 'text':
                txt.append(word['value'])
                beg.append(word['ts'])
                end.append(word['end_ts'])

        out = dict()
        out['words'], out['starts'], out['ends'] = txt, beg, end

        return out

    def request(self, voice_path):

        job = self.stt.submit_job_local_file(voice_path)

        while True:

            dls = self.stt.get_job_details(job.id)
            if str(dls.status).split('.')[-1] != 'TRANSCRIBED': time.sleep(1)
            else: break

        out = self.stt.get_transcript_json(job.id)
        return self.request_to_vectors(out)

if __name__ == '__main__':

    #with open('audios/call_911_0.json', 'r') as raw: log = json.load(raw)
    #message = ' '.join(np.asarray(log['words']))

    print(Image_IBM().request('images/earthquake_road.jpg'))
    #print(Senti_IBM().request(message))
    #print(Voice_Rev().request('audios/call_911_2.wav'))

    #graph = joblib.load('map_sf.jb')
    #print(ShortestPath(graph).dijkstra('40', '70'))