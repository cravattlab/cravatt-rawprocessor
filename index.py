from flask import Flask
from subprocess import call
from glob import glob
from os.path import join
import config

app = Flask(__name__)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/')
def index():
    return 'hello world'

@app.route('/upload/<path>')
def upload(path):

    raw_files = glob(join(config.PATH, path, '*.RAW'))

    if len(raw_files):
        for item in raw_files:
            print item
            call(['readw', '-c', item])
            call(['rawconverter', item, '--ms2', '--out_folder', join(config.PATH, path) ])
    else:
        return 'nope'

# @app.route('/status/<path>')
# def status(path):

if __name__ == "__main__":
    app.run(host='0.0.0.0')