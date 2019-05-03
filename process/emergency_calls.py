# Author:  DINDIN Meryll
# Date:    02 May 2019
# Project: AsTeR

try: from process.apis import *
except: from apis import *

class EmergencyCall:

    def __init__(self, voice_path, api=Voice_Rev(), load_file=False):

        self.api = api
        self.pth = voice_path

        pre = '/'.join(voice_path.split('/')[:-1])
        fle = voice_path.split('/')[-1].split('.')[0]

        if not load_file: 
            self.transcript(dump='{}/{}.json'.format(pre, fle))
        else: 
            with open('{}/{}.json'.format(pre, fle)) as out: 
                self.wrd = json.load(out)

        self.priority_analysis()

    def transcript(self, dump=None):

        self.wrd = self.api.request(self.pth)

        if not dump is None: 
            with open(dump, 'w') as out: 
                json.dump(self.wrd, out)

    def priority_analysis(self, api=Senti_IBM()):

        log = api.request(' '.join(self.wrd['words']))
        self.key = dict()
        for key in log['keywords']: self.key[key['text']] = int(100*key['relevance'])

        dic = dict()
        for e in log['sentiment']['targets']: dic[e['text']] = e['score']
        sco = np.zeros(len(self.wrd['words']))

        for i, wrd in enumerate(self.wrd['words']):
            mtc = [w for w in dic.keys() if w in wrd]
            for key in mtc: sco[i] += np.clip(dic[key], -1, 0)
        sco = np.cumsum(sco)
        self.sco = sco.copy().astype(str)

        self.sco[sco > -2.5] = 'HIGH'
        self.sco[sco > -1.5] = 'MEDIUM'
        self.sco[sco > -0.5] = 'LOW'

    def generate_video(self):

        warnings.simplefilter('ignore')

        rte, wav = wavfile.read(self.pth)
        v_beg = np.asarray(self.wrd['starts'])
        v_end = np.asarray(self.wrd['ends'])
        words = np.asarray(self.wrd['words'])

        # Initialize
        low, top, length = 0, 1, len(wav)/rte
        tns, wds = 'LOW', ' '.join(words[v_end < top][-7:])

        key = []
        for wrd in self.key.keys(): 
            if wrd in wds and not (wrd in ' '.join(key)): 
                key.append('{} ({})'.format(wrd, self.key[wrd]))

        sig = wav[max(0, int(low*rte)):min(wav.shape[0], int(top*rte))][:,0]
        sig = interpolate(np.arange(len(sig)), np.arange(rte), sig)

        f,z = periodogram(sig, fs=rte)
        msk = f < (rte / 50)
        f,z = f[msk], z[msk]

        fig = plt.figure(figsize=(13, 4))
        gds = gridspec.GridSpec(5, 3)

        ax1 = plt.subplot(gds[:3,:2], frameon=False)
        s_1, = ax1.plot(sig, c='dodgerblue', lw=0.75)
        ax1.set_title('Audio Signal', x=0, fontsize=11)
        ax1.set_xticks([])
        ax1.set_yticks([])
        ax1.set_ylim([-max(np.abs(wav[:,0])), max(np.abs(wav[:,0]))])

        ax2 = plt.subplot(gds[:3,2], frameon=False)
        s_2, = ax2.plot(f, z, c='black', lw=1.0)
        ax2.hlines(0.0, 0.0, max(f), lw=0.5)
        ax2.set_yticks([])
        ax2.set_xticks([])
        ax2.set_title('Periodogram', x=-0.04, fontsize=11)
        ax2.set_ylim([-300000.0, 300000.0])

        ax3 = plt.subplot(gds[3,:2], frameon=False)
        t_0 = ax3.text(10, 5, wds, fontsize=14)
        ax3.set_yticks([])
        ax3.set_xticks([])
        ax3.set_title('Transcription', x=0.005, fontsize=11)
        ax3.set_xlim([0, 100])
        ax3.set_ylim([0, 10])

        ax4 = plt.subplot(gds[3,2], frameon=False)
        ax4.text(-148, 0, 'LOW', fontsize=14)
        ax4.text(-80, 0, 'MEDIUM', fontsize=14)
        ax4.text(20, 0, 'HIGH', fontsize=14)
        ax4.set_yticks([])
        ax4.set_xticks([])
        ax4.set_xlim([-154, 60])
        ax4.set_ylim([-20, 20])
        ax4.set_title('Priority', x=-0.105, fontsize=11)
        if tns == 'LOW': ax4.add_artist(Rectangle((-152, -3), len(list(tns))*13, 16, fill=False))
        if tns == 'MEDIUM': ax4.add_artist(Rectangle((-87, -3), len(list(tns))*12, 16, fill=False))
        if tns == 'HIGH': ax4.add_artist(Rectangle((15, -3), len(list(tns))*11, 16, fill=False))
            
        ax5 = plt.subplot(gds[4,:], frameon=False)
        t_1 = ax5.text(6.5, 5, ' | '.join(key), fontsize=14)
        ax5.set_yticks([])
        ax5.set_xticks([])
        ax5.set_title('Keywords', x=-0.01, fontsize=11)
        ax5.set_xlim([0, 100])
        ax5.set_ylim([0, 10])

        plt.show()

        def update(frame_number):

            low, top = frame_number/30, (frame_number/30)+1
            wds = ' '.join(words[v_end < top][-7:])
            try: tns = self.sco[v_end < top][-1]
            except: tns = self.sco[-1]
            for wrd in self.key.keys(): 
                if wrd in wds and not (wrd in ' '.join(key)): 
                    key.append('{} ({})'.format(wrd, self.key[wrd]))

            sig = wav[max(0, int(low*rte)):min(wav.shape[0], int(top*rte))][:,0]
            sig = interpolate(np.arange(len(sig)), np.arange(rte), sig)

            f,z = periodogram(sig, fs=rte)
            msk = f < (rte / 50)
            f,z = f[msk], z[msk]
            
            s_1.set_ydata(sig)
            s_2.set_ydata(z)
            t_0.set_text(wds)
            t_1.set_text(' | '.join(key))
            
            ax4.artists[-1].remove()
            if tns == 'LOW': ax4.add_artist(Rectangle((-152, -3), len(list(tns))*13, 16, fill=False))
            if tns == 'MEDIUM': ax4.add_artist(Rectangle((-87, -3), len(list(tns))*12, 16, fill=False))
            if tns == 'HIGH': ax4.add_artist(Rectangle((15, -3), len(list(tns))*11, 16, fill=False))

        pre = '/'.join(self.pth.split('/')[:-1])
        fle = self.pth.split('/')[-1].split('.')[0]
        out = '{}/{}.mp4'.format(pre, fle)

        animation = FuncAnimation(fig, update, interval=30, frames=int(30*length))
        Writer = writers['ffmpeg']
        writer = Writer(fps=30, metadata=dict(artist='Meryll Dindin'), bitrate=1800)
        animation.save(out, writer=writer)

if __name__ == '__main__':

    # Initialize the arguments
    prs = argparse.ArgumentParser()    
    prs.add_argument('-f', '--filename', help='Call Filename', type=str)
    prs.add_argument('-v', '--withFilm', help='Generate Film', type=str, default='False')
    prs = prs.parse_args()
    if prs.withFilm == 'True': prs.withFilm = True
    else: prs.withFilm = False

    cll = EmergencyCall('calls/{}'.format(prs.filename), load_file=False)
    if prs.withFilm: cll.generate_video()
