# Author:  DINDIN Meryll
# Date:    26 April 2019
# Project: AsTeR

try: from process.utils import *
except: from utils import *

class Voice_IBM:

    def __init__(self, credentials='configs/credentials.yaml'):

        with open(credentials, 'r') as raw: crd = yaml.safe_load(raw)
        self.stt = SpeechToTextV1(iam_apikey=crd['voice_ibm']['key'], url=crd['voice_ibm']['url'])
        self.stt.set_default_headers({'x-watson-learning-opt-out': 'true'})
        del crd

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

    def __init__(self, credentials='configs/credentials.yaml'):

        with open(credentials, 'r') as raw: crd = yaml.safe_load(raw)
        self.api = VisualRecognitionV3('2018-03-19', iam_apikey=crd['image_ibm']['key'])
        del crd

    def request(self, image_path):

        with open(image_path, 'rb') as img:
            req = self.api.classify(images_file=img, images_filename=image_path)
    
        return req.get_result()['images'][0]['classifiers'][0]['classes']

class Senti_IBM:

    def __init__(self, credentials='configs/credentials.yaml'):

        with open(credentials, 'r') as raw: crd = yaml.safe_load(raw)
        arg = {'iam_apikey': crd['texts_ibm']['key'], 'url': crd['texts_ibm']['url']}
        self.api = NaturalLanguageUnderstandingV1(version='2018-11-16', **arg)
        del crd

    def request(self, message):

        key = list(pd.read_csv('configs/vocabulary.csv', sep=',').Word.values.ravel())
        
        fea = Features(sentiment=SentimentOptions(targets=key), 
                       keywords=KeywordsOptions(sentiment=True, limit=10))

        return self.api.analyze(text=message, features=fea).get_result()

class Voice_Rev:

    def __init__(self, credentials='configs/credentials.yaml'):

        with open(credentials, 'r') as raw: crd = yaml.safe_load(raw)
        self.stt = apiclient.RevAiAPIClient(crd['voice_rev']['key'])
        del crd

    def request_to_vectors(self, json_request):

        txt, beg, end = [], [], []

        for word in json_request['monologues'][0]['elements']:
            if word['type'] == 'text':
                txt.append(word['value'])
                beg.append(word['ts'])
                end.append(word['end_ts'])
            if word['type'] == 'punct' and word['value'] != ' ':
                txt[-1] = txt[-1] + word['value']

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

class Meteo_Sky:

    def __init__(self, credentials='configs/credentials.yaml'):

        with open(credentials, 'r') as raw: crd = yaml.safe_load(raw)
        self.url = '{}{}'.format(crd['meteo_sky']['url'], crd['meteo_sky']['key'])
        del crd

    def request(self, longitude, latitude, date):

        t_s = int(datetime.timestamp(date))
        req = '{}/{},{},{}'.format(self.url, latitude, longitude, t_s)
        req = requests.get(req).json()

        req = req['hourly']['data']
        lst_keys = []
        for ele in req: lst_keys += list(ele.keys())
        lst_keys = np.unique(lst_keys)

        dic = dict()
        for key in lst_keys: dic[key] = []
        for ele in req:
            for key in lst_keys:
                if key not in ele.keys(): dic[key].append(np.nan)
                else: dic[key].append(ele[key])

        dtf = pd.DataFrame.from_dict(dic)
        dtf.time = [datetime.fromtimestamp(int(ele)) for ele in dtf.time]
        dtf.set_index('time', inplace=True)
        for key in ['summary', 'icon', 'uvIndex', 'visibility', 'precipType', 'pressure', 'precipProbability']:
            try: dtf.drop(key, axis=1, inplace=True)
            except: pass

        return dtf

if __name__ == '__main__':

    print(Meteo_Sky().request('-121.449855', '39.746697', datetime.datetime(year=2019, month=3, day=1)))
