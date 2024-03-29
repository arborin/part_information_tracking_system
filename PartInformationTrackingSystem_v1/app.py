import logging
import socket
import sys
from threading import Event, Thread

import communicate
import flask
import serial
from flask import Flask, flash, json, render_template
from flask.config import Config
from flask_socketio import SocketIO, emit
from pymongo import MongoClient, errors

# On startup the app has to load database settings first


class App(Flask):
    def __init__(self, import_name, camera_params=None, scale_params=None, db_params=None):

        super().__init__(import_name)

        # 10 Parameter
        self.weights_file = 'settings/weights.json'

        # CAMERA PATAMETERS
        with open(camera_params, 'r') as fileo:
            self.camera_params = json.load(fileo)

        # SCALE PARAMETERS
        with open(scale_params, 'r') as fileo:
            self.scale_params = json.load(fileo)

        # DATABASE PARAMETERS
        with open(db_params, 'r') as fileo:
            self.db_params = json.load(fileo)

        #
        with open(self.weights_file, 'r') as fileo:
            self.weights = json.load(fileo)

        self.camera_file = camera_params
        self.scale_file = scale_params
        self.db_file = db_params

        self.active_weight = None
        try:
            self.camera_port = communicate.create_camera_port(
                self.camera_params)
        except:

            self.camera_port = None

        self.last_camera_string = None

    def write_settings(self, dest):
        if dest == 'camera':
            with open(self.camera_file, 'w') as fileo:
                json.dump(self.camera_params, fileo)

        if dest == 'db':
            with open(self.db_file, 'w') as fileo:
                json.dump(self.db_params, fileo)

        if dest == 'scale':
            with open(self.scale_file, 'w') as fileo:
                json.dump(self.scale_params, fileo)

        if dest == 'weights':
            with open(self.weights_file, 'w') as fileo:
                json.dump(self.weights, fileo)


app = App(__name__, camera_params='settings/camera.json',
          scale_params='settings/scale.json',
          db_params='settings/db.json')


logging.basicConfig(level=logging.DEBUG)

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)
thread = Thread()
thread_stop_event = Event()


def check_camera():
    logging.info(">>>>>>>>>>>>>>>def check camera")
    while not thread_stop_event.isSet():

        for scale in app.scale_params['scale']:
            scale_name = scale['name']
            
            # IF SCALE IS ACTIVE IN CASE OF 2 SCALE
            if scale['active']:
                logging.info("0 - PROCESS RUNS FOR SCALE: {} \n".format(scale['name']))
                logging.info("1 - GET DATA FROM CAMERA \n")

                if app.camera_port and app.active_weight[scale_name]:
                    camera_string = communicate.query_camera_string(app.camera_port)
                else:
                    socketio.sleep(1)
                    continue
                print("-----------------------------------------------------------")
                print(camera_string)
                print("-----------------------------------------------------------")

                # camera_string = "HHAR2502301##Ca##131945##T04222##S0002130##N01###"

                if camera_string and (camera_string.count('#') == 13):
                    # check if first char is valid
                    if camera_string[0].isalnum() is False:
                        app.last_camera_string = camera_string[1:]
                    else:
                        app.last_camera_string = camera_string

                    logging.info("2 - CAMERA STRING: {}\n".format(app.last_camera_string))
                    socketio.sleep(5)

                    # OLD
                    # result = communicate.scale_get_weight((app.scale_params["scale_ip"], app.scale_params['scale_port']),app)
                    # NEW
                    result = communicate.scale_get_weight((scale["scale_ip"], scale['scale_port']), app)
                    
                    logging.info("3 - SCALE IP: {} PORT: {}\n".format(scale["scale_ip"], scale["scale_port"]))

                    if (result <= app.active_weight[scale_name]['hl']) and (result >= app.active_weight[scale_name]['ll']):
                        resp = communicate.write_weight_to_db(app.db_params, result, app)
                        logging.info("4 - WRITE TO DATABASE\n")
                    else:
                        logging.info("4 - WRITE TO DATABASE FALSE\n")
                        resp = communicate.write_weight_to_db(app.db_params, result, app, False)

                    socketio.emit('newnumber', {'number': str(resp)}, namespace='/test')

            logging.info("END - PROCESS \n")
            logging.info("===============================================================")

        socketio.sleep(1)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    print('Client connected')

    if not thread.isAlive():
        print("Starting Thread", file=sys.stderr)
        thread = socketio.start_background_task(check_camera)


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


@app.route('/')
def test():
    title = "Default Page"

    with open(app.weights_file, 'r') as fileo:
        app.weights = json.load(fileo)

    with open(app.scale_file, 'r') as fileo:
        app.scale_params = json.load(fileo)

    active = {'scale_a': "No Part active", 'scale_b': "No Part active"}

    if app.active_weight:
        active = {'scale_a': "No Part active", 'scale_b': "No Part active"}

        if app.active_weight.get('ScaleA'):
            active['scale_a'] = app.active_weight['ScaleA']["part_name"]
        else:
            active['scale_a'] = "No Part active"

        if app.active_weight.get('ScaleB'):
            active['scale_b'] = app.active_weight['ScaleB']["part_name"]
        else:
            active['scale_b'] = "No Part active"

    return render_template('base.html', title=title, weights=app.weights, scale_params=app.scale_params,  active_weight=active)


@app.route('/settings')
def settings():
    title = "Settings"
    return render_template('settings.html', title=title, db_params=app.db_params, scale_params=app.scale_params,
                           camera_params=app.camera_params)


@app.route('/console')
def console():
    return render_template('console.html')


@app.route('/console-output')
def console_output():
    return render_template('console.html')


@app.route('/settings/db', methods=["GET", "POST"])
def set_db_params():
    app.db_params = flask.request.form
    app.write_settings('db')
    return app.make_response('OK')


@app.route('/settings/camera', methods=["GET", "POST"])
def set_camera_params():

    # get_camera_params = flask.request.form.to_dict()

    # camera_id = int(get_camera_params['camera_id'])

    # print(app.camera_params, file=sys.stderr)
    # print("====================================", file=sys.stderr)

    # print(get_camera_params, file=sys.stderr)
    # print("====================================", file=sys.stderr)

    # app.camera_params['camera'][camera_id] = get_camera_params

    # print(app.camera_params, file=sys.stderr)
    # print("====================================", file=sys.stderr)

    app.camera_params = flask.request.form
    app.write_settings('camera')
    return app.make_response('OK')


@app.route('/settings/camera/checkconnection', methods=["GET", "POST"])
def check_camera_connection():
    print(" >> Checking cammera connection", file=sys.stderr)
    app.logger.info(app.camera_params)
    # try:
    if app.camera_port:
        if app.camera_port.is_open:
            app.camera_port.close()

    app.camera_port = communicate.create_camera_port(app.camera_params)
    app.logger.info(app.camera_port)
    return app.make_response('OK')
    # except Exception:
    #     import traceback
    #     return app.make_response(traceback.format_exc())


@app.route('/settings/scale', methods=["GET", "POST"])
def set_scale_parames():
    args = flask.request.form.to_dict()

    app.logger.info(app.scale_params)
    scale_id = int(args['scale_id'])

    app.scale_params['scale'][scale_id]['scale_ip'] = args['scale_ip']
    app.scale_params['scale'][scale_id]['scale_port'] = args['scale_port']

    app.logger.info(app.scale_params)
    app.write_settings('scale')

    return app.make_response('OK')


@app.route('/settings/scale/enable', methods=["GET", "POST"])
def set_scale_b():
    args = flask.request.form

    app.logger.info(app.scale_params)

    args = dict(args)
    active = int(args['active'][0])

    app.scale_params['scale'][1]['active'] = active

    app.logger.info(app.scale_params)
    app.write_settings('scale')

    return app.make_response('OK')


@app.route('/settings/weights', methods=["GET", "POST"])
def set_weights():
    weights = flask.request.json['weight']
    scale_id = flask.request.json['scale_id']

    # DELETE ALL OLD VALUES FROM JSON
    second_scale = []

    for index in range(len(app.weights)):
        if app.weights[index]['scale'] != scale_id:
            second_scale.append(app.weights[index])

    app.weights = second_scale

    print("===========================")
    print(app.weights)
    print("===========================")
    app.weights = app.weights + weights
    print(app.weights)
    print("===========================")

    # app.weights = args
    app.write_settings('weights')
    return app.make_response("OK")


@app.route('/settings/scale/checkconnection', methods=['GET', 'POST'])
def check_scale_connection():
    params = flask.request.form
    try:
        sock = socket.create_connection(
            (params['scale_ip'], params['scale_port']), 0.5)
        sock.close()
        return app.make_response('OK')
    except Exception as e:
        return app.make_response('{}'.format(e))


@app.route('/settings/camera_ip/checkconnection', methods=['GET', 'POST'])
def check_ip_camera_connection():
    params = flask.request.form
    camera_ip = params['camera_ip']
    camera_port = params['camera_port']
    print("==================================")
    print("checking camera ip connection")
    print(f"camera ip: {camera_ip}, camera_port: {camera_port} ")
    print("==================================")
    try:
        sock = socket.create_connection((camera_ip, camera_port), 0.5)
        command = 'T\r\n'
        command = bytes(command, 'ascii')
        sock.sendall(command)
        response = sock.recv(4096)
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        print("==================================")
        print("camera response")
        print(response.decode('ascii'))
        print("==================================")

        return app.make_response('OK')

    except Exception as e:
        return app.make_response('{}'.format(e))


@app.route('/settings/db/checkconnection', methods=['GET', 'POST'])
def check_db_connection():
    params = flask.request.form
    res = 'OK'
    try:
        conn_params = {}
        if params['db_ip'] != '':
            conn_params.update({'host': params['db_ip']})
        if params['db_port'] != '':
            conn_params.update({'port': int(params['db_port'])})
        if params['db_user'] != '':
            conn_params.update({'username': params['db_user']})
        if params['db_password'] != '':
            conn_params.update({'password': params['db_password']})
        client = MongoClient(**conn_params, serverSelectionTimeoutMS=3000)
        client.admin.command('ismaster')
        # client.server_info()
        # return app.make_response('OK')

    except Exception as e:
        res = 'Error: {}...'.format(str(e)[:20])

    return app.make_response('{}'.format(res))


@app.route('/set_active_weight', methods=['GET', 'POST'])
def set_active_weight():

    params = flask.request.form

    get_data = params.to_dict()

    scale_index = 0
    scale_name = get_data['scale']
    if get_data['scale'] == 'ScaleB':
        scale_index = 1

    app.logger.info("+++++++++++++++++++++++++++++++++++++++")
    print(app.scale_params['scale'][scale_index]['scale_ip'])
    print(app.scale_params['scale'][scale_index]['scale_port'])
    print(params['scale'])
    app.logger.info("+++++++++++++++++++++++++++++++++++++++")

    # THIS IS FOR INIT DICT
    if app.active_weight == None:
        app.active_weight = {}

    app.active_weight[scale_name] = {"weight": float(params['weight'].replace(',', '.')),
                                     'll': float(params['ll'].replace(',', '.')),
                                     'hl': float(params['hl'].replace(',', '.')),
                                     "part_name": params["part_name"]
                                     }

    print("==========================================")
    print(app.active_weight)
    print("==========================================")

    try:
        result = communicate.scale_set_weight((app.scale_params['scale'][scale_index]['scale_ip'],
                                               app.scale_params['scale'][scale_index]['scale_port']),
                                              params['weight'],
                                              params['ll'],
                                              params['hl'])

        return app.make_response(str(result) + "#" + params["part_name"] + "#" + params['scale'])
    except:
        return app.make_response("NOK")


@app.route('/get_weight', methods=['GET', 'POST'])
def get_weight():
    app.logger.info("def get_weight()")

    scale_name = app.scale_params["name"]

    result = communicate.scale_get_weight(
        (app.scale_params["scale_ip"], app.scale_params['scale_port']), app)
    if app.active_weight is None:
        return app.make_response("Error. Please set active weight first. Weight is {}".format(result))

    if (result <= app.active_weight[scale_name]['hl']) and (result >= app.active_weight[scale_name]['ll']):
        resp = communicate.write_weight_to_db(app.db_params, result, app)
        return app.make_response(str(resp))
    else:
        resp = communicate.write_weight_to_db(
            app.db_params, result, app, False)
        return app.make_response(str(resp))
        # return app.make_response('Weight is out of limits')


if __name__ == '__main__':
    socketio.run(app, debug=True)
