from flask import Flask
from subprocess import call, PIPE
from glob import glob
from os.path import join, split, splitext
from distutils import spawn
import psutil
import config
import shelve
import json
from cors import crossdomain

app = Flask(__name__)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True

processes = {}

@app.route('/')
@crossdomain(origin='*')
def index():
    return 'hello world'

@app.route('/upload/<path>')
def upload(path):

    raw_files = glob(join(config.PATH, path, '*.RAW'))

    if len(raw_files):
        rawconv_path = split(spawn.find_executable('rawconverter'))[0]
        rawconv_out = join(config.PATH, path)

        processes[path] = []

        for item in raw_files:

            readw_proc = psutil.Popen(['readw', '-c', item], stdout=PIPE)
            rawc_proc = psutil.Popen(
                ['rawconverter', item, '--ms2', '--select_mono_prec', '--out_folder', rawconv_out ],
                cwd=rawconv_path, stdout=PIPE
            )

            filename = splitext(item)[0]

            processes[path].extend(({
                'filename': filename + '.mzXML',
                'process': readw_proc,
                'status': None
            }, {
                'filename': filename + '.ms2',
                'process': rawc_proc,
                'status': None
            }))
    else:
        return 'nope'

    return 'wat'


@app.route('/status/<path>')
def status(path):
    status = []


    if path in processes:
        for process in processes[path]:
            # get status string while we can
            try:
                process['status'] = process['process'].status()
            # when process is dead we read stdout
            except psutil.NoSuchProcess:
                try:
                    process['status'] = process['process'].communicate()[0]
                except Exception:
                    pass

        return json.dumps([ { k: v for k, v in x.items() if k != 'process' } for x in processes[path] ], sort_keys=True, indent=4, separators=(',', ': '))
    else:
        return '%s not found' % path

    return 'wat'


if __name__ == "__main__":
    app.run(host='0.0.0.0')
