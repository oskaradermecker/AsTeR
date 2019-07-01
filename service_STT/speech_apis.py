# Author:  DINDIN Meryll
# Date:    28 June 2019
# Project: AsTeR

try: from service_STT.imports import *
except: from imports import *

class Voice_IBM:

    def __init__(self, credentials='configs/credentials.yaml'):

        with open(credentials, 'r') as raw: crd = yaml.safe_load(raw)
        self.stt = SpeechToTextV1(iam_apikey=crd['voice_ibm']['key'], url=crd['voice_ibm']['url'])
        self.stt.set_default_headers({'x-watson-learning-opt-out': 'true'})
        del crd

    def request_to_vectors(self, json_request):

        txt, beg, end = [], [], []

        for element in json_request['results']:
            for sentence in element['alternatives']:
                for word in sentence['timestamps']:
                    if word[0] != '%HESITATION':
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
                                     max_alternatives=1,
                                     continuous=True,
                                     timestamps=True)
            req = req.get_result()

        return self.request_to_vectors(req)

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

class Voice_GGC:

    def __init__(self, credentials='configs/google-cloud.json'):

        crd = service_account.Credentials.from_service_account_file(credentials)
        self.stt = speech.SpeechClient(credentials=crd)
        del crd

    def request_to_vectors(self, json_request):

        txt, beg, end = [], [], []

        for result in json_request.results:
            for word in result.alternatives[0].words:
                txt.append(word.word)
                beg.append(word.start_time.seconds + word.start_time.nanos/1e9)
                end.append(word.end_time.seconds + word.end_time.nanos/1e9)

        out = dict()
        out['words'], out['starts'], out['ends'] = txt, beg, end

        return out

    def request(self, voice_path):

        with wave.open(voice_path, 'rb') as fle: rte = fle.getframerate()
        arg = {'language_code': 'en-US', 'enable_word_time_offsets': True}
        cfg = types.RecognitionConfig(sample_rate_hertz=rte, **arg)

        out = voice_path.split('/')[-1].split('.')[0] + '_left.' + voice_path.split('/')[-1].split('.')[1]
        out = '/'.join(voice_path.split('/')[:-1] + [out])
        try: os.system('ffmpeg -y -i {} -map_channel 0.0.0 {}'.format(voice_path, out))
        except: pass

        with io.open(out, 'rb') as fle: fle = types.RecognitionAudio(content=fle.read())
        req = self.stt.recognize(cfg, fle)

        return self.request_to_vectors(req)

if __name__ == '__main__':

    api = Voice_Rev()
    print(api.request('calls/call_0.wav'))