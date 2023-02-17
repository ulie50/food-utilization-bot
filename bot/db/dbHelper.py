"""This class should be used to execute sql queries"""
from calendar import c
import os
import uuid
from glob import glob
import datetime

import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from db.tables import (
    Base,
    Entrance_new,
    Notification_new,
    Product_names,
    Storage_info,
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

    def add2entrance(self, chat, message, inDB=False):
        db_ind = uuid.uuid4().hex
        with self.Session() as session:
            session.add(
                Entrance_new(
                    entrance_id=db_ind,
                    chat_id=chat,
                    product=message,
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

    def getDays(self, product):
        with self.engine.connect() as conn:
            result = conn.execute(
                Storage_info.__table__.select().where(
                    Storage_info.__table__.c.product_name == str(product)
                )
            )

        return result.fetchone()[1]

    def add2notification(self, chat, message, days):
        db_ind = uuid.uuid4().hex
        date = datetime.datetime.now() + datetime.timedelta(days=days)

        with self.Session() as session:
            session.add(
                Notification_new(
                    notification_id=db_ind,
                    chat_id=chat,
                    notification_date=date,
                    user_product=message,
                    # is_freezable=False,
                    # link="test",
                )
            )
            session.commit()

    def is_item_in_db(self, message):
        with self.engine.connect() as conn:
            result = conn.execute(
                Product_names.__table__.select().where(
                    Product_names.__table__.c.name_var == str(message)
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
