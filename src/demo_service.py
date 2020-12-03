import json

from flask import Flask
from src import database_helper
from flask import request
import os

from src.util import get_common_response, RESPONSE_CODE, MSG

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'docs')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/get_doc_states", methods=['GET'])
def get_doc_states():
    result = database_helper.get_doc_states()
    return result

@app.route("/get_doc_levels", methods=['GET'])
def get_doc_levels():
    result = database_helper.get_doc_levels()
    return result

@app.route("/get_user_info", methods=['GET'])
def get_user_info():
    response = get_common_response()
    try:
        data = request.get_json()
        if 'user_id' in data:
            user_id = data['user_id']
            response = database_helper.get_user_info(user_id)
        else:
            response[RESPONSE_CODE] = 400
            response[MSG] = "No user id in json"
    except:
        response[RESPONSE_CODE] = 400
        response[MSG] = "Body is not json"

    return response

@app.route("/register_user", methods=['POST'])
def register_user():
    response = get_common_response()
    try:
        data = request.get_json()
        if 'full_name' in data and 'user_name' in data and 'password' in data and 'title' in data:
            fullname = data['full_name']
            user_name = data['user_name']
            password = data['password']
            title = data['title']
            response = database_helper.create_user(fullname, user_name, password, title)
        else:
            response[RESPONSE_CODE] = 400
            response[MSG] = "Missing data in json"
    except:
        response[RESPONSE_CODE] = 400
        response[MSG] = "Body is not json"
    return response

@app.route("/edit_user", methods=['PUT'])
def edit_user():
    response = get_common_response()
    try:
        data = request.get_json()
        if 'full_name' in data and 'user_name' in data and 'password' in data and 'title' in data:
            fullname = data['full_name']
            user_name = data['user_name']
            password = data['password']
            title = data['title']
            response = database_helper.edit_user(fullname, user_name, password, title)
        else:
            response[RESPONSE_CODE] = 400
            response[MSG] = "Missing data in json"
    except:
        response[RESPONSE_CODE] = 400
        response[MSG] = "Body is not json"
    return response

@app.route("/delete_user", methods=['PUT'])
def remove_user():
    response = get_common_response()
    try:
        data = request.get_json()
        if 'user_name' in data:
            user_name = data['user_name']
            response = database_helper.remove_user(user_name)
        else:
            response[RESPONSE_CODE] = 400
            response[MSG] = "Missing user_name in json"
    except:
        response[RESPONSE_CODE] = 400
        response[MSG] = "Body is not json"
    return response

@app.route("/add_doc", methods= ['POST'])
def add_doc():
    response = get_common_response()
    try:
        request_data = request.form
        if 'from' in request_data and 'to' in request_data and 'cc' in request_data and 'doc_name' in request_data and 'doc_id' in request_data and 'level' in request_data and 'state' in request_data and 'start_date' in request_data and 'end_date' in request_data:
            from_user = request_data['from']
            to_user = request_data['to']
            cc = request_data['cc']
            cc_list = json.loads(cc)
            doc_name = request_data['doc_name']
            doc_id = request_data['doc_id']
            level = request_data['level']
            state = request_data['state']
            start_date = request_data['start_date']
            end_date = request_data['end_date']

            upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], from_user)
            if not os.path.exists(upload_folder):
                try:
                    os.mkdir(upload_folder)
                except OSError:
                    print("Cannot create path " + upload_folder)
                    response[RESPONSE_CODE] = 400
                    response[MSG] = "Cannot save file"
                    return response
                else:
                    print("Success create folder " + upload_folder)
            f = request.files
            if f and 'file' in f:
                upload_file = f['file']
                print('start receive')
                final_file_name = os.path.join(upload_folder, upload_file.filename)
                upload_file.save(final_file_name)
                response = database_helper.add_doc(from_user, to_user, cc_list, doc_id, doc_name, level, state, start_date, end_date, final_file_name)
            else:
                response[RESPONSE_CODE] = 400
                response[MSG] = "Missing file in request"
        else:
            response[RESPONSE_CODE] = 400
            response[MSG] = "Missing data in json"
    except:
        response[RESPONSE_CODE] = 400
        response[MSG] = "error in body"
    return response

@app.route("/get_all_docs", methods= ['GET'])
def get_all_docs():
    response = get_common_response()
    try:
        data = request.get_json()
        if 'user_name' in data:
            user_name = data['user_name']
            response = database_helper.get_all_doc(user_name)
        else:
            response[RESPONSE_CODE] = 400
            response[MSG] = "Missing user_name in json"
    except Exception as e:
        print(e)
        response[RESPONSE_CODE] = 400
        response[MSG] = "Error"
    return response

@app.route("/get_doc_file", methods= ['GET'])
def get_doc_file():
    response = get_common_response()
    try:
        data = request.get_json()
        if 'doc_db_id' in data:
            db_id = data['doc_db_id']
            return database_helper.get_doc_file(db_id)
        else:
            response[RESPONSE_CODE] = 400
            response[MSG] = "Missing doc_db_id in json"
    except Exception as e:
        print(e)
        response[RESPONSE_CODE] = 400
        response[MSG] = "Body error"
    return response

if __name__ == '__main__':
    database_helper.init_database()
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.mkdir(upload_folder)

    app.run(host="0.0.0.0", port="8080")
