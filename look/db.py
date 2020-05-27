import traceback
import os
import sys
from time import sleep
from hashlib import sha256

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from look.config import Config
from look.model.base import Base

def init_db():
    print("init_db")

    for i in range(15):
        try:
            engine = create_engine(f"mysql+mysqldb://{Config.DB_USER}{':'+Config.DB_PASSWORD if not Config.DB_PASSWORD=='travis' else ''}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset=utf8")
            
            db_session = sessionmaker(bind=engine)

            Base.metadata.create_all(bind=engine)
        except OperationalError as e:
            pass
        except:
            print("Unknown Error in init_db")
        else:
            break
        sleep(2)
    else:
        print(f"mysql+mysqldb://{Config.DB_USER}{':'+Config.DB_PASSWORD if not Config.DB_PASSWORD=='travis' else ''}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset=utf8")
        print(Config.DB_HOST, Config.DB_PORT, Config.DB_USER, Config.DB_PASSWORD, os.environ["DB_PASSWORD"])
        print("Can't connect to MySQL server")
        sys.exit(1)

    return db_session, engine

def truncate_table(db_session, engine, tablename=None):
    print("truncate_table")

    tablename = tablename if tablename and not tablename == 'all' else None
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            if tablename and not table.__tablename__ == tablename: continue
            conn.execute(table.delete())

    try:
        db_session.commit()
    except:
        traceback.print_exc()
        db_session.rollback()

def get_class_by_tablename(tablename):
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c

def insert_dummy_data(db_session):
    print("insert_dummy_data")

    models = {}
    dummy_data = {
        'user' : [
            {
                'username':'test',
                'email':'test@gmail.com',
                'password':'test123!',
            },
            {
                'username':'xptmxmek',
                'email':'xptmxmek@naver.com',
                'password':'xptmxmek123!',
            },
            {
                'username':'rudehdzja12',
                'email':'rudehdzja12@kduiv.ac.kr',
                'password':'rudehdzja123!',
            },
            {
                'username':'annyeong',
                'email':'annyeong@gmail.com',
                'password':'annyeong123!',
            },
            {
                'username':'test2',
                'email':'test2@gmail.com',
                'password':'test123!',
            },
        ],
        'category' : [
            {
                'title':'Category1',
                'subtitle':'Category1\'s subtitle',
            },
            {
                'title':'Category2',
                'subtitle':'Category2\'s subtitle',
            },
        ],
        'board' : [
            {
                'title':'Board1',
                'subtitle':'Board1\'s subtitle',
            },
            {
                'title':'Board2',
                'subtitle':'Board2\'s subtitle',
            },
        ],
        'chapter' : [{'title':f'Chapter{i+1}'} for i in range(4)],
        'subchapter' : [{'title':f'Subchapter{i+1}'} for i in range(8)],
    }
    for data in dummy_data["user"]:
        data["password"] = sha256(data["password"].encode()).hexdigest()

    relationships = {
        "user" : {
            "target" : "subchapter",
            "rel_name" : "learning_progress",
            "data" : [
                [1, 1],
                [1, 2],
                [2, 1],
            ],
        },
        "category" : {
            "target" : "board",
            "rel_name" : "board",
            "data" : [
                [1, 1],
                [1, 2],
                [2, 1],
            ],
        },
        "board" : {
            "target" : "chapter",
            "rel_name" : "chapter",
            "data" : [
                [1, 1],
                [1, 2],
                [2, 3],
                [2, 4],
            ],
        },
        "chapter" : {
            "target" : "subchapter",
            "rel_name" : "subchapter",
            "data" : [
                [1, 1],
                [1, 2],
                [2, 3],
                [2, 4],
                [3, 5],
                [3, 6],
                [4, 7],
                [4, 8],
            ],
        },
    }

    for table in dummy_data:
        models[table] = []
        for data in dummy_data[table]:
            models[table].append(get_class_by_tablename(table)(**data))

    for rel in relationships:
        tmp = {}
        for data in relationships[rel]["data"]:
            if not data[0]-1 in tmp: tmp[data[0]-1] = []
            tmp[data[0]-1].append(models[relationships[rel]["target"]][data[1]-1])
        for m in tmp:
            setattr(models[rel][m], relationships[rel]["rel_name"], tmp[m])

    for table in models:
        for model in models[table]:
            db_session.add(model)

    try:
        db_session.commit()
    except:
        traceback.print_exc()
        db_session.rollback()