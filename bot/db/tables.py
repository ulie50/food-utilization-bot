from sqlalchemy import Column, Integer, String, Date, Boolean, MetaData, DateTime
from sqlalchemy.ext.declarative import declarative_base

# meta = MetaData(schema="basic")
meta_new = MetaData(schema="k70047_foodstorage")

Base = declarative_base(metadata=meta_new)
# Base = declarative_base()

class Chats(Base):
    """
    id
    chat_id
    language
    entrance_timestamp
    """
    __tablename__ = "chat_info"
    id = Column("id", String(32), primary_key=True)
    chat_id = Column("chat_id", String(15))
    language = Column("language", String(15))
    entrance_timestamp = Column("entrance_timestamp", DateTime) 

class Notifications(Base):
    __tablename__ = "notifications"
    id = Column("id", String(32), primary_key=True)
    chat_id = Column("chat_id", String(15))
    is_notified = Column("is_notified", Boolean)
    notification_date = Column(
        "notification_date", DateTime
    )  # Datetime is better and explicit name!
    is_freezable = Column("is_freezable", Boolean)  # ren*ame to is_freezable//
    link = Column("link_to_site", String(255))
    user_input_text = Column("user_input_text", String(255))  # rename to explicit name


class Entrances(Base):
    """
    id
    chat_id
    notification_id
    entrance_timestamp
    input_text
    in_storage 
    
    """
    __tablename__ = "entrances"
    id = Column("id", String(32), primary_key=True)
    chat_id = Column("chat_id", String(32), nullable=False)
    notification_id = Column("notification_id", String(32))
    entrance_timestamp = Column("entrance_timestamp", Date)  # Date
    input_text = Column("produinput_textct", String(100), nullable=False)
    in_storage = Column("in_storage", Boolean)  # Another name!


class Products(Base):
    __tablename__ = "products"
    id = Column("id", String(32), primary_key=True)
    storage_days = Column("storage_days", Integer)
    is_freezable = Column("is_freezable", Boolean)
    link = Column("link", String(255))


class Products_en(Base):
    __tablename__ = "products_en"
    id = Column("id", String(32), primary_key=True)
    product_name = Column("product_name", String(255))
    product_id = Column("product_id", String(32))


class Products_de(Base):
    __tablename__ = "products_de"
    id = Column("id", String(32), primary_key=True)
    product_name = Column("product_name", String(255))
    product_id = Column("product_id", String(32))

class Products_ru(Base):
    __tablename__ = "products_ru"
    id = Column("id", String(32), primary_key=True)
    product_name = Column("product_name", String(255))
    product_id = Column("product_id", String(32))

class Phrases(Base):
    __tablename__ = "phrases"
    id = Column("id",Integer,autoincrement=False,primary_key=True)
    language = Column("language",String(15),primary_key=True)
    phrase = Column("phrase",String(1000))
