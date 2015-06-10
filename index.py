from flask import Flask, jsonify, make_response, abort
from subprocess import PIPE
from glob import glob
from os.path import join, split, splitext, basename
from distutils import spawn
from cors import crossdomain
import psutil
import config
import os

app = Flask(__name__)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True

processes = {}

@app.route('/')
def index(): return ''

@app.route('/convert/<path>')
@crossdomain(origin='*')
def convert(path):
    # make sure we're not already running an operation for given path
    if path in processes: abort(409)

    raw_files = glob(join(config.PATH, path, '*.RAW'))
    # make sure the given path contains raw files
    if not len(raw_files): abort(400)

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
            'filename': basename(filename + '.mzXML'),
            'process': readw_proc,
            'status': None
        }, {
            'filename': basename(filename + '.ms2'),
            'process': rawc_proc,
            'status': None
        }))

    return success_response('Requested files are being converted')

@app.route('/status/<path>')
@crossdomain(origin='*')
def status(path):
    if not path in processes: abort(404)

    result = {
        'progress': 0.0,
        'status': 'running'
    }
    
    for process in processes[path]:
        # get status string while we can
        try:
            process['status'] = process['process'].status()

        # when process is dead we read from stdout
        except psutil.NoSuchProcess:
            result['progress'] = result['progress'] + 1

            try:
                return_code = process['process'].poll()
                # process['output'] = process['process'].communicate()[0]
                if return_code == 0:
                    process['status'] = 'success'
                else:
                    process['status'] = 'fail'
            # exception triggered when we try and poll a process we've already polled
            except Exception:
                pass

        if process['status'] == 'fail':
            if 'fail' in result['status']:
                result['status']['fail'].append(process['filename'])
            else:
                result['status'] = {
                    'fail': [ process['filename'] ]
                }

    # crude estimator of progress
    result['progress'] = round(result['progress']/len(processes[path]), 2) * 100

    if result['progress'] == 100:
        if not 'fail' in result['status']:
            result['status'] = 'success'
        del processes[path]

    return jsonify(result)

@app.route('/abort/<path>')
@crossdomain(origin='*')
def abort_conversion(path):
    if not path in processes: abort(404)

    for process in processes[path]:
        try:
            process['process'].kill()
        except Exception:
            pass

    del processes[path]
    return success_response('Conversion successfully aborted')

def error_response(error, code):
    return make_response(jsonify({ 'error': error }), code)

def success_response(message):
    return jsonify({ 'success' : message })

@app.errorhandler(400)
def erroneous_path(error):
    return error_response('No .raw files found at specified path', 400)

@app.errorhandler(404)
def status_failed(error):
    return error_response('There is no conversion operation for the given path', 404)

@app.errorhandler(409)
def conversion_running(error):
    return error_response('There is already a conversion operation running for the given path', 409)

if __name__ == "__main__":
    app.run(host='0.0.0.0')