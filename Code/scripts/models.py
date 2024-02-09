from flask_sqlalchemy import SQLAlchemy
from scripts.config import *

class U_ATT(db.Model):
  __tablename__ = "U_Attributes"
  ATT_ID        = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
  Name          = db.Column(db.Text, unique=True, nullable=False)
  
  Registrations = db.relationship("U_Reg", back_populates="Attribute")

class U_Reg(db.Model):
  __tablename__ = "U_Register"
  S_NO          = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
  U_ID          = db.Column(db.Text, unique=True, nullable=False)
  PWD           = db.Column(db.Text, nullable=False)  
  Mail_ID       = db.Column(db.Text, unique=True, nullable=False)
  ATT           = db.Column(db.Integer, db.ForeignKey("U_Attributes.ATT_ID"), nullable=False)
  
  Attribute     = db.relationship("U_ATT", back_populates="Registrations")


class Category(db.Model):
  __tablename__ = "Categories"
  ID            = db.Column(db.Integer, autoincrement=True, primary_key=True,unique=True, nullable=False)
  Name          = db.Column(db.Text, nullable=False)
  No_Prods      = db.Column(db.Integer,nullable=False)

  products      = db.relationship("Product",backref="Category")

class Product(db.Model):
  __tablename__ = "Products"
  ID            = db.Column(db.Integer,  autoincrement=True, primary_key=True,unique=True, nullable=False)
  Name          = db.Column(db.Text, nullable=False)
  Units         = db.Column(db.Text, nullable=False)
  Rateper       = db.Column(db.Integer, nullable=False)
  Stock         = db.Column(db.Integer, nullable=False)
  Category_ID   = db.Column(db.Integer, db.ForeignKey("Categories.ID"),nullable=False)
  Discount      = db.Column(db.Integer, nullable=True)


class Feature(db.Model):
  __tablename__ = "Featured"
  ID            = db.Column(db.Integer,  autoincrement=True, primary_key=True,unique=True, nullable=False)
  Product_ID    = db.Column(db.Integer, db.ForeignKey("Products.ID"),nullable=False)
  Product_Name  = db.Column(db.Text, nullable=False)


class Trans_rec(db.Model):
  __tablename__ = "Bought"
  ID            = db.Column(db.Integer,  autoincrement=True, primary_key=True,unique=True, nullable=False)
  U_ID          = db.Column(db.Integer, nullable=False)
  Product_ID    = db.Column(db.Integer, nullable=False)
  Product_Name  = db.Column(db.Text, nullable=False)
  Product_Units = db.Column(db.Text, nullable=False)
  Product_Unit_Price = db.Column(db.Integer, nullable=False)
  Amount_Bought = db.Column(db.Integer, nullable=False)
  Category_ID   = db.Column(db.Integer, nullable=False)
  Discount      = db.Column(db.Integer, nullable=True)
  Total         = db.Column(db.Integer, nullable=False)
  Date_Time     = db.Column(db.Text, nullable=True)


class U_Cart(db.Model):
  __tablename__ = "Cart"
  ID            = db.Column(db.Integer,  autoincrement=True, primary_key=True,unique=True, nullable=False)
  U_ID          = db.Column(db.Integer, nullable=False)
  Product_ID    = db.Column(db.Integer, nullable=False)
  Product_Name  = db.Column(db.Text, nullable=False)
  Product_Status= db.Column(db.Integer, nullable=False)
