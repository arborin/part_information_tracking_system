import socket
import datetime
import time
import serial
import sys
import logging
from asyncio import Lock
from pymongo import MongoClient
from serial.serialutil import PARITY_EVEN, PARITY_SPACE

logger = logging.getLogger('communicate')
handler = logging.FileHandler('communicate.log')
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def scale_set_weight(addr, weight, low, high):
    responses = b''
    weight = str(weight).replace('.', ',')
    low = str(low).replace('.', ',')
    high = str(high).replace('.', ',')
    sock = socket.create_connection(addr)
    # setting weight
    print('Setting weight')
    command = 'SM{}\r\n'.format(weight)
    command = bytes(command, 'ascii')
    sock.sendall(command)
    response = sock.recv(4096)
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    print(response.decode('ascii'))
    responses+=response
    print('Setting Limit Low')
    command = 'SL{}\r\n'.format(low)
    command = bytes(command, 'ascii')
    sock = socket.create_connection(addr)
    sock.sendall(command)
    response = sock.recv(4096)
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    responses+=response
    print(response.decode('ascii'))
    print('Setting Limit High')
    command = 'SH{}\r\n'.format(high)
    command = bytes(command, 'ascii')
    sock = socket.create_connection(addr)
    sock.sendall(command)
    response = sock.recv(4096)
    responses+=response
    print(response.decode('ascii'))
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    return responses.decode('ascii')

def scale_get_weight(addr, app):

    # if app.camera_port is None:
    #     print('Camera is not ready, skip get weight.')
    #     return 0

    # camera_string = query_camera_string(app.camera_port)


    # if (camera_string is not None) and (camera_string.count('#')==13):
    #     # check if first char is valid
    #     if camera_string[0].isalnum is False:
    #         app.last_camera_string = camera_string[1:]
    #     else:
    #         app.last_camera_string = camera_string

    sock = socket.create_connection(addr)
    command = 'SI\r\n'
    command = bytes(command, 'ascii')
    sock.sendall(command)
    time.sleep(0.1)
    response = b''

    while len(response)<16:
        r = sock.recv(1028)
        print(r)
        print(str(len(r)))
        response += r
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    response = response.decode('ascii')
    # weight = response[2:9].strip().replace(',','.')
    weight = response.strip().split(" ")[0].replace(',','.')
    try:
        weight = float(weight)
    except:
        weight = "0.0"
    print('The weight is: {}'.format(weight))

    return weight

def write_weight_to_db(db_params, weight, app, weigt_within_limits=True):
    client = MongoClient(host=db_params['database_ip'], port=int(db_params['database_port']), username=db_params['database_user'],
    password=db_params['database_password'])
    db = client.partdata
    now = datetime.datetime.now()
    camera_values = {
        "PartNo":None,
        "PartIndex":None,
        "SupplierID": None,
        "ManfDay": None,
        "SerialNo": None,
        "Cavity": None,
        "Overall": None,
        "Axial_Non_Conformity": None,
        "Unused_Error_Correction": None,
        "Cell_Contrast": None,
        "Cell_Modulation": None,
        "Fixed_Pattern_Damage": None,
        "Grid_Non_Uniformity": None,
        "Minimum_Reflectance": None
    }
    if app.last_camera_string is not None:
        #update camera values here
        # Example string, spaces inserted for readability
        # YHBB2502303 #Cb #123987 #T30120 #S0000265 #N01 #4.0 #4.0 #4.0# 4.0#4.0#4.0#4.0#4.0
        camera_string = app.last_camera_string.split('#')
        print("DEBUG: writting db camera string: {}".format(app.last_camera_string))
        camera_values =  {
        "PartNo":camera_string[0],
        "PartIndex":camera_string[1],
        "SupplierID": int(camera_string[2]),
        #"ManfDay": int(camera_string[3]),
        "ManfDay": camera_string[3],
        "SerialNo": camera_string[4],
        "Cavity": camera_string[5],
        "Overall": float(camera_string[6]),
        "Axial_Non_Conformity": float(camera_string[7]),
        "Unused_Error_Correction": float(camera_string[8]),
        "Cell_Contrast": float(camera_string[9]),
        "Cell_Modulation": float(camera_string[10]),
        "Fixed_Pattern_Damage": float(camera_string[11]),
        "Grid_Non_Uniformity": float(camera_string[12]),
        "Minimum_Reflectance": float(camera_string[13])
    }

    if camera_values["PartNo"] == "HHAR2502301":
        camera_values["Measurement_Values"] = {
            "Locking_Torque" : "",
            "Distance" : ""
        }

    if camera_values["PartNo"] == "HHAR2502307":
        camera_values["Measurement_Values"] = {
            "Pullout_Strength" : "",
            "Distance" : ""
        }
    # now.strftime("%d.%m.%Y")
    query = {"Weight":weight, "Part_Date": now.strftime("%d.%m.%Y"),
    "Part_Time":"{}:{}:{}".format(now.hour, now.minute, now.second)}
    query.update(camera_values)
    if weigt_within_limits:
        res = db.mfg_partdata.insert_one(query)
    else:
        res = db.res = db.mfg_DMC_errorlog.insert_one(query)

    print("DEBUG: DB Inserted id: {}".format(res.inserted_id))
    return query

def query_camera_string(cameraport):

    result = cameraport.read_until()

    if result == b'\xff':
        return
    if len(result)==0:
        return
    if type(result)==type(b'adsa'):
        print(result)
        if result[-1]==b'\n':
            logger.info(result.decode('utf-8'))
            return result.decode('utf-8')

        else:
            result+=cameraport.read_until()
            print(result)
            logger.info(result.decode('utf-8'))
            return result.decode('utf-8')
    else:
        print(result)
        if result[-1]=='\n':
            logger.info(result)
            return result
        else:
            result+=cameraport.read_until()
            logger.info(result)
            return result
            # TODO Looks like this part need more thorough inspection
            # TODO to make sure all data is really collected

def create_camera_port(params):
    if sys.platform == 'linux':
        port = 'virtual-tty'
    else:
        port = params['com_port']
    baudrate = int(params['baud_rate'])
    parity = {"None": serial.PARITY_NONE,
        "Even": serial.PARITY_EVEN,
        "Odd":serial.PARITY_ODD,
        "Names": serial.PARITY_NAMES,
        "Mark": serial.PARITY_MARK,
        "Space":serial.PARITY_SPACE}[params['parity']]
    stopbits = {
        '1': serial.STOPBITS_ONE,
        '1.5': serial.STOPBITS_ONE_POINT_FIVE,
        '2': serial.STOPBITS_TWO
    }[params['stop_bits']]

    bytesize = int(params['byte_size'])
    xonxoff = (params['flow_control'] == 'XON/XOFF')
    rtscts = (params['flow_control'] == 'RTS/CTS')
    dsrdtr = (params['flow_control'] == 'DSR/DTR')
    camera_port = serial.Serial(
    port = port,
    baudrate = baudrate,
    parity = parity,
    bytesize=bytesize,
    stopbits = stopbits,
    xonxoff=xonxoff,
    rtscts = rtscts,
    dsrdtr = dsrdtr,
    timeout = 0.1)
    return camera_port
