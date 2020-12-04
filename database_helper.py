import json
import os

from flask import send_file
from mysql import connector

from util import get_current_time, get_common_response, RESPONSE_CODE, MSG, DATA, get_time_by_format, \
    DATE_TIME_SHORT_FORMAT

USER = os.environ['DATABASE_USER']
PASSWORD = os.environ['DATABASE_PASSWORD']

def get_db_connector():
    cvdb = connector.connect(
        host="localhost",
        user=USER,
        password=PASSWORD,
        database="congvan_db"
    )
    return cvdb


def init_database():
    mydb = connector.connect(
        host="localhost",
        user=USER,
        password=PASSWORD
    )
    mydb_cusor = mydb.cursor()
    mydb_cusor.execute("CREATE DATABASE IF NOT EXISTS congvan_db")
    mydb.close()

    cvdb = get_db_connector()
    cv_cursor = cvdb.cursor()
    create_user_table_script = "CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, fullname nchar(100) not null,username char(50) unique not null, password char(50) not null, title nchar(100) not null, state tinyint not null, datechange datetime not null)"
    cv_cursor.execute(create_user_table_script)

    check_table_script = "SHOW TABLES LIKE %s"
    cv_cursor.execute(check_table_script, ("doc_levels",))
    result = cv_cursor.fetchone()
    if not result:
        create_doc_levels_table_script = "CREATE TABLE IF NOT EXISTS doc_levels(id int auto_increment primary key, content nvarchar(50) not null)"
        cv_cursor.execute(create_doc_levels_table_script)
        insert_format = "INSERT INTO doc_levels (content) VALUES (%s)"
        cv_cursor.execute(insert_format, ("Binh thuong",))
        cv_cursor.execute(insert_format, ("Quan trong",))
        cv_cursor.execute(insert_format, ("Khan",))

    cv_cursor.execute(check_table_script, ("doc_states",))
    result2 = cv_cursor.fetchone()
    if not result2:
        create_doc_states_table_script = "CREATE TABLE IF NOT EXISTS doc_states(id int auto_increment primary key, content nvarchar(50) not null)"
        cv_cursor.execute(create_doc_states_table_script)

        insert_state_format = "INSERT INTO doc_states (content) VALUES (%s)"
        cv_cursor.execute(insert_state_format, ("Hoan thanh",))
        cv_cursor.execute(insert_state_format, ("Chua hoan thanh",))
        cv_cursor.execute(insert_state_format, ("Gia han",))
        cv_cursor.execute(insert_state_format, ("Khong hoan thanh",))

    create_doc_states_table_script = "CREATE TABLE IF NOT EXISTS doc_states(id int auto_increment primary key, content nvarchar(50) not null)"
    cv_cursor.execute(create_doc_states_table_script)

    create_document_table_script = "CREATE TABLE IF NOT EXISTS documents(id int auto_increment primary key, docId char(50) not null, creator int not null, foreign key (creator) references users (id), create_date datetime not null, title char(250) not null, content mediumBlob, location nchar(200), level int not null, foreign key (level) references doc_levels (id), state int not null, foreign key (state) references doc_states (id))"
    cv_cursor.execute(create_document_table_script)

    create_document_details_script = "CREATE TABLE IF NOT EXISTS doc_process_details (id int auto_increment primary key, document_id int not null, foreign key (document_id) references documents (id), assignee int not null, foreign key (assignee) references users (id), start_date datetime not null, end_date datetime not null, create_date datetime not null)"
    cv_cursor.execute(create_document_details_script)

    create_cc_table_script = "CREATE TABLE IF NOT EXISTS cc (id int auto_increment primary key, document_id int not null, foreign key (document_id) references documents (id), user_id int not null, foreign key (user_id) references users (id))"
    cv_cursor.execute(create_cc_table_script)

    cv_cursor.close()


def create_user(name, user_name, password, title):
    print("creating " + name)
    response = get_common_response()
    db = get_db_connector()
    db_cursor = db.cursor()
    try:
        sql = "INSERT INTO users (fullname, username, password, title, state, datechange) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (name, user_name, password, title, 1, get_current_time())
        db_cursor.execute(sql, val)
        user_id = db_cursor.lastrowid
        response_info = {"user_id": user_id}
        response[DATA] = response_info
        db.commit()
    except mysql.connector.Error as err:
        print(err)
        print(err.msg)
        response[RESPONSE_CODE] = 400
        response[MSG] = err.msg
    finally:
        db_cursor.close()
        db.close()
    return response


def edit_user(name, user_name, password, title):
    response = get_common_response()
    db = get_db_connector()
    db_cursor = db.cursor()
    try:
        sql = "UPDATE users SET fullname = %s, password = %s, title = %s, datechange = %s WHERE username = %s"
        val = (name, password, title, get_current_time(), user_name)
        db_cursor.execute(sql, val)
        db.commit()
        if db_cursor.rowcount < 1:
            response[RESPONSE_CODE] = 400
            response[MSG] = "Row not found"
    except mysql.connector.Error as err:
        print(err)
        print(err.msg)
        response[RESPONSE_CODE] = 400
        response[MSG] = err.msg
    finally:
        db_cursor.close()
        db.close()

    return response


def remove_user(user_name):
    print("remove user " + user_name)
    response = get_common_response()
    db = get_db_connector()
    db_cursor = db.cursor()

    try:
        sql = "UPDATE users SET state = %s, datechange = %s WHERE username = %s"
        val = (0, get_current_time(), user_name)
        db_cursor.execute(sql, val)
        db.commit()
        if db_cursor.rowcount < 1:
            response[RESPONSE_CODE] = 400
            response[MSG] = "Row not found"
    except mysql.connector.Error as err:
        print(err)
        print(err.msg)
        response[RESPONSE_CODE] = 400
        response[MSG] = err.msg
    finally:
        db_cursor.close()
        db.close()
    return response


def add_doc(from_user, to_user, cc_list, doc_id, doc_name, level, state, start_date, end_date, final_file_name):
    print("add doc from " + from_user)
    response = get_common_response()
    db = get_db_connector()
    db_cursor = db.cursor()
    try:
        script_get_user_id = "SELECT id FROM users WHERE username = %s"

        # add new row to documents table
        db_cursor.execute(script_get_user_id, (from_user,))
        user_object = db_cursor.fetchone()
        if not user_object:
            response[RESPONSE_CODE] = 400
            response[MSG] = "From user not found"
            return response

        db_cursor.execute(script_get_user_id, (to_user,))
        assignee_object = db_cursor.fetchone()
        if not assignee_object:
            response[RESPONSE_CODE] = 400
            response[MSG] = "To user not found"
            return response
        print(get_current_time())
        sql = "INSERT INTO documents (docId, creator, create_date, title, location, level, state) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (doc_id, user_object[0], get_current_time(), doc_name, final_file_name, level, state)
        db_cursor.execute(sql, val)
        document_id = db_cursor.lastrowid

        # add new row to document process detail table

        assignee_id = assignee_object[0]
        insert_to_details_script = "INSERT INTO doc_process_details (document_id, assignee, start_date, end_date, create_date) VALUES (%s, %s, %s, %s, %s)"
        insert_details_val = (
            document_id, assignee_id, get_time_by_format(start_date), get_time_by_format(end_date), get_current_time())
        db_cursor.execute(insert_to_details_script, insert_details_val)

        # add new row to cc table
        for cc_username in cc_list:
            db_cursor.execute(script_get_user_id, (cc_username,))
            cc_object = db_cursor.fetchone()
            if not cc_object:
                response[RESPONSE_CODE] = 400
                response[MSG] = "CC user not found"
                return response
            cc_id = cc_object[0]
            insert_to_cc_script = "INSERT INTO cc (document_id, user_id) VALUES (%s, %s)"
            insert_to_cc_val = (document_id, cc_id)
            db_cursor.execute(insert_to_cc_script, insert_to_cc_val)

        db.commit()
        response[DATA] = {"document_id": document_id}
    except mysql.connector.Error as err:
        print(err)
        print(err.msg)
        response[RESPONSE_CODE] = 400
        response[MSG] = err.msg
    finally:
        db_cursor.close()
        db.close()
    return response


def get_all_doc(user_name):
    print("get all doc from " + user_name)
    response = get_common_response()
    db = get_db_connector()
    db_cursor = db.cursor()
    final_result = {}
    try:
        script_get_user_id = "SELECT id FROM users WHERE username = %s"
        db_cursor.execute(script_get_user_id, (user_name,))
        user_object = db_cursor.fetchone()
        if not user_object:
            response[RESPONSE_CODE] = 400
            response[MSG] = "User not found"
            return response

        user_id = user_object[0]
        script_get_all_docs = "SELECT * FROM documents WHERE creator = %s"
        db_cursor.execute(script_get_all_docs, (user_id,))
        list_docs = db_cursor.fetchall()
        final_result['count'] = len(list_docs)
        item_list = []
        for doc in list_docs:
            doc_info = {}
            doc_info['doc_db_id'] = doc[0]
            doc_info['docId'] = doc[1]
            doc_info['creator'] = doc[2]
            doc_info['create_date'] = doc[3].strftime(DATE_TIME_SHORT_FORMAT)
            doc_info['title'] = doc[4]
            doc_info['level'] = doc[7]
            doc_info['state'] = doc[8]

            # details of document
            get_details_script = "SELECT assignee, start_date, end_date FROM doc_process_details WHERE document_id = %s"
            db_cursor.execute(get_details_script, (doc[0],))
            list_details = db_cursor.fetchall()
            details_item = []
            for process_detail in list_details:
                detail_info = {}
                detail_info['start_date'] = process_detail[1].strftime(DATE_TIME_SHORT_FORMAT)
                detail_info['end_date'] = process_detail[2].strftime(DATE_TIME_SHORT_FORMAT)
                get_user_name_script = "SELECT fullname FROM users where id = %s"
                db_cursor.execute(get_user_name_script, (process_detail[0],))
                detail_info['assignee_name'] = db_cursor.fetchone()[0]
                details_item.append(detail_info)
            doc_info['process_details'] = details_item
            item_list.append(doc_info)

        final_result['items'] = item_list
        response[DATA] = final_result
        print("found item")
        print(len(item_list))
    except mysql.connector.Error as err:
        print(err)
        print(err.msg)
        response[RESPONSE_CODE] = 400
        response[MSG] = err.msg
    finally:
        db_cursor.close()
        db.close()

    return response


def get_doc_states():
    db = get_db_connector()
    db_cursor = db.cursor()
    list_states = []
    try:
        sql = "SELECT * FROM doc_states"
        db_cursor.execute(sql)
        states = db_cursor.fetchall()
        for state in states:
            state_info = {'state_id': state[0], 'state_name': state[1]}
            list_states.append(state_info)

    except mysql.connector.Error as err:
        print(err)
        print(err.msg)
    finally:
        db_cursor.close()
        db.close()

    return json.dumps(list_states)


def get_user_info(user_id):
    db = get_db_connector()
    db_cursor = db.cursor()
    response = get_common_response()
    user_info = {}
    try:
        sql = "SELECT id, fullname, username, title, state FROM users WHERE id = %s"
        db_cursor.execute(sql, (user_id,))
        user_object = db_cursor.fetchone()
        if user_object:
            user_info['id'] = user_object[0]
            user_info['fullname'] = user_object[1]
            user_info['username'] = user_object[2]
            user_info['title'] = user_object[3]
            user_info['state'] = user_object[4]
        else:
            response[RESPONSE_CODE] = 400
            response[MSG] = "User not found"
    except mysql.connector.Error as err:
        print(err)
        print(err.msg)
        response[RESPONSE_CODE] = 400
        response[MSG] = err.msg
    finally:
        db_cursor.close()
        db.close()

    if len(user_info) > 0:
        response[DATA] = user_info
    return json.dumps(response)


def get_doc_levels():
    db = get_db_connector()
    db_cursor = db.cursor()
    list_levels = []
    try:
        sql = "SELECT * FROM doc_levels"
        db_cursor.execute(sql)
        levels = db_cursor.fetchall()
        for level in levels:
            level_info = {'level_id': level[0], 'level_name': level[1]}
            list_levels.append(level_info)

    except mysql.connector.Error as err:
        print(err)
        print(err.msg)
    finally:
        db_cursor.close()
        db.close()

    return json.dumps(list_levels)


def get_doc_file(doc_db_id):
    response = get_common_response()
    db = get_db_connector()
    db_cursor = db.cursor()
    try:
        sql = "SELECT location FROM documents WHERE id = %s"
        db_cursor.execute(sql, (doc_db_id,))
        doc_object = db_cursor.fetchone()
        if not doc_object:
            response[RESPONSE_CODE] = 400
            response[MSG] = "document not found"
            return response
        path = doc_object[0]
        return send_file(path, as_attachment=True)
    except mysql.connector.Error as err:
        print(err)
        print(err.msg)
        response[RESPONSE_CODE] = 400
        response[MSG] = err.msg
    finally:
        db_cursor.close()
        db.close()

    return response
