# Author:  DINDIN Meryll
# Date:    28 June 2019
# Project: AsTeR

from service_STT.speech_apis import *
from service_STT.endpoint_imports import *

# Defines the service APIs

api_IBM = Voice_IBM()
api_Rev = Voice_Rev()
api_GGC = Voice_GGC()

# Run Flask local server

if __name__ == '__main__':

    app = Flask('STT')
    run_with_ngrok(app)

    @app.route('/speech-to-text', methods=['POST'])
    def run_service():

        fle = request.files['audio_file']
        if not os.path.exists('.tmp'): os.mkdir('.tmp')
        nme = '/'.join(['./.tmp', secure_filename(fle.filename)])
        fle.save(nme)

        arg = dict(request.args)
        if arg['api_type'] == 'IBM': req = api_IBM.request(nme)
        if arg['api_type'] == 'Rev': req = api_Rev.request(nme)
        if arg['api_type'] == 'GGC': req = api_GGC.request(nme)

        arg = {'status': 200, 'mimetype': 'application/json'}
        return Response(response=json.dumps(req), **arg)

    #app.run(host='127.0.0.1', port='8080', threaded=True)
    app.run()
