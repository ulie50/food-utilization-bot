#!/usr/bin/env python3
from sqlalchemy import Column, Integer, String, Date, Boolean, MetaData, DateTime
from sqlalchemy.ext.declarative import declarative_base

# meta = MetaData(schema="basic")
meta_new = MetaData(schema="k70047_foodstorage")

Base = declarative_base(metadata=meta_new)
# Base = declarative_base()


class Notification_new(Base):
    __tablename__ = "notification_tbl"
    notification_id = Column("notification_id", String(32), primary_key=True)
    chat_id = Column("chat_id", String(15))
    is_notified = Column("is_notified", Boolean)
    notification_date = Column(
        "notification_date", DateTime
    )  # Datetime is better and explicit name!
    is_freezable = Column("is_freezable", Boolean)  # ren*ame to is_freezable//
    link = Column("link_to_site", String(255))
    user_product = Column("user_product", String(255))  # rename to explicit name


class Entrance_new(Base):
    __tablename__ = "entrance_tbl"
    entrance_id = Column("entrance_id", String(32), primary_key=True)
    chat_id = Column("chat_id", String(32), nullable=False)
    notification_id = Column("notification_id", String(32))
    entrance_timestamp = Column("entrance_timestamp", Date)  # Date
    product = Column("product", String(100), nullable=False)
    in_storage = Column("in_storage", Boolean)  # Another name!


class Product_names(Base):
    __tablename__ = "product_names_tbl"
    name_var = Column("name_var", String(255), primary_key=True, nullable=False)
    product_name = Column("product_name", String(255))


class Storage_info(Base):
    __tablename__ = "fridge_info_tbl"
    product_name = Column("product_name", String(255), primary_key=True, nullable=False)
    lasts_days = Column("lasts_days", Integer)
    is_freezable = Column("is_freezable", Boolean)
    website_link = Column("website_link", String(255))
