import os
import sys
import time
import hmac
from traceback import print_exc
from time import sleep
from hashlib import sha256

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from look.config import Config
from look.model import Base

def create_db(engine):
    Base.metadata.create_all(bind=engine)

def init_db():
    print("init_db")
    
    for i in range(15):
        try:
            engine = create_engine(
                f"mysql+mysqldb://{Config.DB_USER}{':'+Config.DB_PASSWORD if not Config.DB_PASSWORD=='travis' else ''}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset=utf8",
                pool_recycle=300
            )
            
            db_session = sessionmaker(bind=engine)

            create_db(engine)
        except OperationalError as e:
            pass
        except:
            print("Unknown Error in init_db")
            print_exc()
        else:
            break
        sleep(2)
    else:
        print(f"mysql+mysqldb://{Config.DB_USER}{':'+Config.DB_PASSWORD if not Config.DB_PASSWORD=='travis' else ''}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset=utf8")
        print(Config.DB_HOST, Config.DB_PORT, Config.DB_USER, Config.DB_PASSWORD, os.getenv("DB_PASSWORD", None))
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
        print_exc()
        db_session.rollback()

def drop_db(engine):
        Base.metadata.drop_all(bind=engine)

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
                'username':'admin',
                'email':'admin@codedu.org',
                'password':'admin',
                'admin':True,
            },
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
        'post' : [
            {
                'content':'post 1',
                'user_id':1,
            },
            {
                'content':'post 2',
                'user_id':1,
            },
        ],
        'post_comment' : [
            {
                'post_id':1,
                'content':'comment 1',
                'user_id':1,
                
            },
            {
                'post_id':1,
                'content':'comment 1-1',
                'user_id':1,
                'parent_comment_id':1,
            },
            {
                'post_id':1,
                'content':'comment 1-2',
                'user_id':2,
                'parent_comment_id':1,
            },
            {
                'post_id':1,
                'content':'comment 2',
                'user_id':2,
            },
            {
                'post_id':1,
                'content':'comment 2-1',
                'user_id':1,
                'parent_comment_id':4,
            },
            {
                'post_id':1,
                'content':'comment 2-2',
                'user_id':3,
                'parent_comment_id':4,
            },
        ],
        'chapter' : [{'title':f'Chapter{i+1}'} for i in range(4)],
        'subchapter' : [{'title':f'Subchapter{i+1}', 'content':f'Subchapter{i+1}\'s content'} for i in range(8)],
    }
    for data in dummy_data["user"]:
        data["password"] = hmac.new(Config.SECRET_KEY.encode(), data['password'].encode(), sha256).hexdigest()

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
            "rel_name" : "boards",
            "data" : [
                [1, 1],
                [1, 2],
                [2, 1],
            ],
        },
        "board" : {
            "target" : "chapter",
            "rel_name" : "chapters",
            "data" : [
                [1, 1],
                [1, 2],
                [2, 3],
                [2, 4],
            ],
        },
        "chapter" : {
            "target" : "subchapter",
            "rel_name" : "subchapters",
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
        db_session.add_all(models[table])
        # for model in models[table]:
        #     db_session.add(model)

    try:
        db_session.commit()
    except:
        print_exc()
        db_session.rollback()