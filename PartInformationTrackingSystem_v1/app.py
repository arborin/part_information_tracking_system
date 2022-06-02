import flask
import socket
import sys

from sqlalchemy import true
import communicate
import serial
from flask import json
from flask import Flask
from flask import render_template
from flask.config import Config
from pymongo import MongoClient
from flask_socketio import SocketIO, emit
from threading import Thread, Event
import logging
#On startup the app has to load database settings first


class App(Flask):
    def __init__(self, import_name, camera_params = None, scale_params = None, db_params = None):

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
            self.camera_port = communicate.create_camera_port(self.camera_params)
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

app = App(__name__, camera_params = 'settings/camera.json',
            scale_params = 'settings/scale.json',
            db_params = 'settings/db.json')
            
            
logging.basicConfig(level=logging.DEBUG)

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)
thread = Thread()
thread_stop_event = Event()

def check_camera():
    while not thread_stop_event.isSet():
        if app.camera_port and app.active_weight:
            camera_string = communicate.query_camera_string(app.camera_port)
        else:
            socketio.sleep(1)
            continue

        if camera_string and (camera_string.count('#')==13):
            # check if first char is valid
            if camera_string[0].isalnum() is False:
                app.last_camera_string = camera_string[1:]
            else:
                app.last_camera_string = camera_string
            print("DEBUG: camera string: {}".format(app.last_camera_string))
            socketio.sleep(5)
            result = communicate.scale_get_weight((app.scale_params["scale_ip"], app.scale_params['scale_port']),app)

            if (result <= app.active_weight['hl']) and (result >= app.active_weight['ll']):
                resp = communicate.write_weight_to_db(app.db_params, result, app)
            else:
                resp = resp = communicate.write_weight_to_db(app.db_params, result, app, False)

            socketio.emit('newnumber', {'number': str(resp)}, namespace='/test')

        socketio.sleep(1)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    print('Client connected')

    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(check_camera)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

@app.route('/')
def test():
    title = "Default Page"
    
    with open(app.weights_file, 'r') as fileo:
        app.weights = json.load(fileo)
        
    active = app.active_weight["part_name"] if app.active_weight is not None else "No Part active"
    
    return render_template('base.html', title = title, weights = app.weights, active_weight = active)

@app.route('/settings')
def settings():
    title = "Settings"
    return render_template('settings.html', title=title, db_params = app.db_params, scale_params = app.scale_params,
        camera_params = app.camera_params)

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
    app.camera_params = flask.request.form
    app.write_settings('camera')
    return app.make_response('OK')

@app.route('/settings/camera/checkconnection', methods=["GET", "POST"])
def check_camera_connection():
    if app.camera_port:
        if app.camera_port.is_open:
            app.camera_port.close()
    try:
        app.camera_port = communicate.create_camera_port(app.camera_params)
        return app.make_response('OK')
    except Exception:
        import traceback
        return app.make_response(traceback.format_exc())




@app.route('/settings/scale', methods=["GET", "POST"])
def set_scale_parames():
    args = flask.request.form

    app.logger.info(app.scale_params)
    args = dict(args)
    scale_id = int(args['scale_id'][0])
    
    
    app.scale_params['scale'][scale_id]['scale_ip'] = args['scale_ip'][0]
    app.scale_params['scale'][scale_id]['scale_port'] = args['scale_port'][0]
    
    app.logger.info(app.scale_params)
    app.write_settings('scale')
    
    return app.make_response('OK')

@app.route('/settings/weights', methods=["GET", "POST"])
def set_weights():
    args = flask.request.json
    app.weights = args
    app.write_settings('weights')
    return app.make_response("OK")

@app.route('/settings/scale/checkconnection', methods=['GET', 'POST'])
def check_scale_connection():
    params = flask.request.form
    try:
       sock =  socket.create_connection((params['scale_ip'], params['scale_port']), 0.5)
       sock.close()
       return app.make_response('OK')
    except Exception as e:
        return app.make_response('{}'.format(e))

@app.route('/settings/db/checkconnection', methods=['GET', 'POST'])
def check_db_connection():
    params = flask.request.form
    try:
        conn_params = {}
        if params['db_ip']!='':
            conn_params.update({'host':params['db_ip']})
        if params['db_port']!='':
            conn_params.update({'port':int(params['db_port'])})
        if params['db_user']!='':
            conn_params.update({'username':params['db_user']})
        if params['db_password']!='':
            conn_params.update({'password':params['db_password']})
        client = MongoClient(**conn_params, serverSelectionTimeoutMS=3000)
        client.admin.command('ismaster')
        return app.make_response('OK')
    except Exception as e:
        return app.make_response('{}'.format(e))

@app.route('/set_active_weight', methods=['GET', 'POST'])
def set_active_weight():
    
    params = flask.request.form
    
    try:
        result = communicate.scale_set_weight((app.scale_params['scale_ip'], 
                                                app.scale_params['scale_port']),
                                                params['weight'], 
                                                params['ll'], 
                                                params['hl'])
                                                
        app.active_weight = {"weight":float(params['weight'].replace(',','.')),
                            'll':float(params['ll'].replace(',', '.')),
                            'hl':float(params['hl'].replace(',', '.')),
                            "part_name": params["part_name"]
                            }
        return app.make_response(str(result) + "#" + params["part_name"])
    except:
        return app.make_response("NOK")
                        
    
    

@app.route('/get_weight', methods=['GET', 'POST'])
def get_weight():
    result = communicate.scale_get_weight((app.scale_params["scale_ip"], app.scale_params['scale_port']),app)
    if app.active_weight is None:
        return app.make_response("Error. Please set active weight first. Weight is {}".format(result))

    if (result <= app.active_weight['hl']) and (result >= app.active_weight['ll']):
        resp = communicate.write_weight_to_db(app.db_params, result, app)
        return app.make_response(str(resp))
    else:
        resp = communicate.write_weight_to_db(app.db_params, result, app, False)
        return app.make_response(str(resp))
        #return app.make_response('Weight is out of limits')


if __name__ == '__main__':
    socketio.run(app, debug=true)