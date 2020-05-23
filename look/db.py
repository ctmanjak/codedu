import traceback

from hashlib import sha256

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from look.config import Config
from look.model.user import User
from look.model.category import Category
from look.model.board import Board
from look.model.chapter import Chapter
from look.model.subchapter import Subchapter

def init_db():
    print("init_db")
    engine = create_engine(f"mysql+mysqldb://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset=utf8")

    db_session = sessionmaker(bind=engine)

    User.metadata.create_all(engine)
    Category.metadata.create_all(engine)
    Board.metadata.create_all(engine)
    Chapter.metadata.create_all(engine)
    Subchapter.metadata.create_all(engine)

    return db_session

def insert_dummy_data(db_session):
    print("insert_dummy_data")

    models = {}
    dummy_data = {
        'User' : [
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
        'Category' : [
            {
                'title':'Category1',
                'subtitle':'Category1\'s subtitle',
            },
            {
                'title':'Category2',
                'subtitle':'Category2\'s subtitle',
            },
        ],
        'Board' : [
            {
                'title':'Board1',
                'subtitle':'Board1\'s subtitle',
            },
            {
                'title':'Board2',
                'subtitle':'Board2\'s subtitle',
            },
        ],
        'Chapter' : [{'title':f'Chapter{i+1}'} for i in range(4)],
        'Subchapter' : [{'title':f'Subchapter{i+1}'} for i in range(8)],
    }
    for data in dummy_data["User"]:
        data["password"] = sha256(data["password"].encode()).hexdigest()

    relationships = {
        "User" : {
            "target" : "Subchapter",
            "rel_name" : "learning_progress",
            "data" : [
                [1, 1],
                [1, 2],
                [2, 1],
            ],
        },
        "Category" : {
            "target" : "Board",
            "rel_name" : "board",
            "data" : [
                [1, 1],
                [1, 2],
                [2, 1],
            ],
        },
        "Board" : {
            "target" : "Chapter",
            "rel_name" : "chapter",
            "data" : [
                [1, 1],
                [1, 2],
                [2, 3],
                [2, 4],
            ],
        },
        "Chapter" : {
            "target" : "Subchapter",
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
            models[table].append(globals()[table](**data))

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