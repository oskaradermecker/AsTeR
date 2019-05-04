# Author:  DINDIN Meryll
# Date:    04 May 2019
# Project: AsTeR

try: from process.apis import *
except: from apis import *

class FieldVision:

    def __init__(self, image_path, api=Image_IBM()):

        self.pth = image_path
        self.req = api.request(image_path)

        self.req = pd.DataFrame([(e['class'], e['score']) for e in self.req], columns=['CLASS', 'SCORE'])
        self.req = self.req.sort_values(by='SCORE', ascending=False)
        self.req['CLASS'] = [e.lower() for e in self.req['CLASS']]

    def dump_image(self):

        pre = '/'.join(self.pth.split('/')[:-1])
        fle = self.pth.split('/')[-1].split('.')[0]
        img = Image.open(self.pth)
        img.thumbnail((512, 256), Image.ANTIALIAS)

        fig = plt.figure(figsize=(13, 5))
        gds = gridspec.GridSpec(1, 5)

        ax0 = plt.subplot(gds[:,1:])
        ax0.imshow(img)
        ax0.set_xticks([])
        ax0.set_yticks([])

        ax1 = plt.subplot(gds[:,0])
        sns.barplot(x='SCORE', y='CLASS', data=self.req, label='Detected Classes', orient='h')
        sns.set_color_codes("pastel")
        ax1.set_xticks([])
        ax1.set_xlabel('')

        plt.tight_layout()
        plt.show()

        fig.savefig('{}/{}_analysis.png'.format(pre, fle))

if __name__ == '__main__':

    # Initialize the arguments
    prs = argparse.ArgumentParser()    
    prs.add_argument('-f', '--filename', help='Call Filename', type=str)
    prs = prs.parse_args()

    FieldVision('images/{}'.format(prs.filename)).dump_image()
