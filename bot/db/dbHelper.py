"""This class should be used to execute sql queries"""
from calendar import c
import os
import uuid
from glob import glob
import datetime

import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from bot.db.tables import (
    Base,
    Entrances,
    Notifications,
    Products,
    Products_en,
    Products_de,
    Products_ru,
    Chats,
    Phrases
)
PATH = os.path.dirname(os.path.abspath(__file__))


class dbHelper:
    def __init__(self, db_user:str):

        db_host = str(self.get_secret("db_host",""))
        db_name = str(self.get_secret("db_name",""))
        db_username = self.get_secret(f'db_{db_user}_login',"")
        db_password = self.get_secret(f'db_{db_user}_password',"")    

        self.engine = sqlalchemy.create_engine(
            f"mysql+pymysql://{db_username}:{db_password}@{db_host}:3306/{db_name}",
            echo=True,pool_pre_ping =True
        )
        self.metadata = sqlalchemy.MetaData(schema="basic")
        self.Session = sessionmaker(bind=self.engine)

        with self.engine.begin() as conn:
            Base.metadata.create_all(conn)

    def add_chat(self, chat, language):
        db_ind = uuid.uuid4().hex
        with self.Session() as session:
            session.add(
                Chats(
                    id = db_ind,
                    chat_id = chat,
                    language = language,
                    entrance_timestamp=datetime.date.today(),
                )
            )
            session.commit()

    def get_chat(self,chat_id):
        with self.Session() as session:
            chat_info =  session.query(Chats).filter(Chats.chat_id==chat_id).order_by(
                                        sqlalchemy.desc(Chats.entrance_timestamp)).limit(1).one()
            return chat_info
        

    def get_user_language(self,chat_id):
        chat_info = self.get_chat(chat_id)
        if chat_info:
            return chat_info.language
        else:
            return None


    def get_phrase(self,phrase_id,language):
        with self.Session() as session:
            return session.query(Phrases).filter(sqlalchemy.and_(Phrases.id==phrase_id,Phrases.language==language)).one()


    def add_entrance(self, chat, message,notification_id=None, inDB=False):
        db_ind = uuid.uuid4().hex
        with self.Session() as session:
            session.add(
                Entrances(
                    id=db_ind,
                    chat_id=chat,
                    notification_id = notification_id,
                    input_text=message,
                    in_storage=inDB,
                    entrance_timestamp=datetime.datetime.now(),
                )
            )
            session.commit()

    def get_secret(self,key, default):
        value = os.getenv(key, default)
        if os.path.isfile(value):
            with open(value) as f:
                return f.read()
        return value

    def getDays(self, product_id):
        with self.engine.connect() as conn:
            result = conn.execute(
                Products.__table__.select().where(
                    Products.__table__.c.id == str(product_id)
                )
            )

        return result.fetchone()


    def add_notification(self, chat, message, days):
        db_ind = uuid.uuid4().hex
        date = datetime.datetime.now() + datetime.timedelta(days=days)

        with self.Session() as session:
            session.add(
                Notifications(
                    id=db_ind,
                    chat_id=chat,
                    notification_date=date,
                    user_product=message,
                    # is_freezable=False,
                    # link="test",
                )
            )
            session.commit()
        return db_ind

    def is_item_in_db(self, message,language):
        if language=='en':
            table = Products_en.__table__
        elif language == 'de':
            table = Products_de.__table__
        elif language == 'ru':
            table = Products_ru.__table__
        with self.engine.connect() as conn:
            result = conn.execute(
                table.select().where(
                    table.c.product_name == str(message)
                )
            )

        return result.fetchone()

    def check_notification(self, date:datetime.datetime):
        with self.engine.connect() as conn:
            result = conn.execute(
                Notification_new.__table__.select().where(sqlalchemy.and_(
                    func.date(Notification_new.__table__.c.notification_date) == date.date(),
                    func.extract('hour',Notification_new.__table__.c.notification_date) == date.hour
                )  
                )
            )

        return result.fetchall()

    def update_is_notified(self, nid):
        with self.engine.connect() as conn:
            with conn.begin() as trans:
                conn.execute(
                    Notification_new.__table__.update()
                    .where(Notification_new.__table__.c.notification_id == nid)
                    .values(is_notified=True)
                )
                trans.commit()
