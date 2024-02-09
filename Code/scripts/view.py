from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from scripts.models import *
import re 
import datetime


class user():
  def __init__(self, Mail_ID, PWD):
    self.Mail_ID = Mail_ID
    self.PWD   = PWD
    self.U_ID  = -1 
    self.Valid = False
    self.SPAtt = False
    self.authenticate()


  def authenticate(self):
    #get rec
    db.session.begin()
    record = U_Reg.query.filter_by(Mail_ID=self.Mail_ID).first()
    db.session.close()
    # auth here
    if record:
      if record.PWD == self.PWD:
        self.Valid = True
        self.U_ID  = record.U_ID
        if record.ATT == 1:
          self.SPAtt = True 

  #we dont use generalized func for fetching in hopes that its safer
  def fetch_cats(self):
    db.session.begin()
    records = Category.query.all()
    db.session.close()
    if records == None:
      return None
    cats = []
    for record in records:
      inspector = inspect(record)
      column_names = [column.key for column in inspector.mapper.column_attrs]
      values = [getattr(record, column_name) for column_name in column_names]
      cats.append(values)
    try:
      db.session.close()
    finally:
      return cats


  def fetch_one_cat(self,cat_Name):
    db.session.begin()
    record = Category.query.filter_by(Name=cat_Name).first()
    db.session.close()
    if record == None:
      return None

    return record

  def fetch_cat_ID(self,ID):
    db.session.begin()
    record = Category.query.filter_by(ID=ID).first()
    db.session.close()
    if record == None:
      return None

    return record

  def fetch_prods(self,cat_Name):
    db.session.begin()
    try:
      cat = Category.query.filter_by(Name=cat_Name).first()
      ID  = cat.ID
      records = Product.query.filter_by(Category_ID=ID)
    except:
      print("NOOOOOOOOOOOOOOOOOOOOOOOO")
      print(cat_Name, cat, ID,records)
    finally:
      db.session.close()

    if records == None:
      return None
    prods = []
    for record in records:
      inspector = inspect(record)
      column_names = [column.key for column in inspector.mapper.column_attrs]
      values = [getattr(record, column_name) for column_name in column_names]
      prods.append(values)
    db.session.close()
    return prods


  def fetch_all_prods(self):
    db.session.begin()
    prods = []
    try:
      records = Product.query.all()
      if records !=None:
        for record in records:
          inspector = inspect(record)
          column_names = [column.key for column in inspector.mapper.column_attrs]
          values = [getattr(record, column_name) for column_name in column_names]
          prods.append(values)
    except:
      print("NOOOOOOOOOOOOOOOOOOOOOOOO")
    finally:
      db.session.close()
    return prods

  def add_cat(self, cat_name):
    flag = 0
    db.session.begin()
    try:
      new_Cat = Category(Name=cat_name,No_Prods=0)
      db.session.add(new_Cat)
      db.session.commit()
      flag = 1
    except:
      db.session.rollback()
    finally:
      db.session.close()
      return flag


  def edit_cat(self,cat_Name, new_Name):
    flag = 0
    db.session.begin()
    record = Category.query.filter_by(Name=cat_Name).first()
    try:
      record.Name = new_Name
      db.session.commit()
      flag = 1
    except:
      db.session.rollback()
    finally:
      db.session.close()

    return flag

  def delete_cat(self,cat_Name,Category_ID):
    flag=0
    db.session.begin()
    try:
      category = Category.query.filter_by(Name=cat_Name,ID=Category_ID).first()
      ID       = category.ID 
      product  = Product.query.filter_by(Category_ID=ID)
      for prod in product:
        db.session.delete(prod)
      db.session.delete(category)
      db.session.commit()
      flag = 1
    except:
      db.session.rollback()
    finally:
      db.session.close()
      return flag


  def fetch_one_prod(self,prod_Name,product_ID):
    db.session.begin()
    record = Product.query.filter_by(Name=prod_Name,ID=product_ID).first()
    
    product = []
    if record != None:
      inspector = inspect(record)
      column_names = [column.key for column in inspector.mapper.column_attrs]
      values = [getattr(record, column_name) for column_name in column_names]
      product.append(values)
    else:
      product.append([])
    db.session.close()
    return product[0]

  def add_prod(self, prod_name,units,Rateper,Quantity,cat_Name):
    flag = 0
    Category_ID = self.fetch_one_cat(cat_Name)
    if Category_ID == None:
      return flag
    Category_ID = Category_ID.ID

    db.session.begin()
    try:
      new_prod = Product(Name=prod_name,Units=units,Rateper=Rateper,Stock=Quantity,Category_ID=Category_ID)
      db.session.add(new_prod)
      db.session.commit()
      flag = 1
    except:
      db.session.rollback()
    finally:
      db.session.close()
      return flag


  def edit_prod(self, product_ID,prod_name,units,Rateper,Quantity,cat_Name,category_ID,discount=None):
    flag = 0
    Category = self.fetch_one_cat(cat_Name)
    if Category == None:
      return flag

    db.session.begin()
    try:
      prod = Product.query.filter_by(ID=product_ID).first()
      prod.Name    = prod_name
      prod.Units   = units
      prod.Rateper = Rateper
      prod.Stock   = Quantity
      if discount !=None:
        prod.Discount = discount
      db.session.commit()
      flag = 1
    except:
      db.session.rollback()
    finally:
      db.session.close()
      return flag


  def feat_prod(self, product_ID,prod_name):
    product   = self.fetch_one_prod(prod_name,product_ID)
    flag = 0
    if len(product)<=0:
      return flag

    db.session.begin()
    try:
      record = Feature(Product_ID=product_ID,Product_Name=prod_name)
      db.session.add(record)
      db.session.commit()
      flag = 1
    except:
      db.session.rollback()
    finally:
      db.session.close()
      return flag


  def fetch_feat_prods(self):
    db.session.begin()
    prods = []
    try:
      records = Feature.query.all()
    except:
      print("NOOOOOOOOOOOOOOOOOOOOOOOO")
    finally:
      db.session.close()

    for record in records:
      product = self.fetch_one_prod(record.Product_Name,record.Product_ID)
      if product != [] and product !=None and len(product)>0:
        prods.append(product)
    return prods


  def fetch_cart_items(self):
    db.session.begin()
    prods = []
    try:
      records = U_Cart.query.all()
    except:
      print("NOOOOOOOOOOOOOOOOOOOOOOOO")
    finally:
      db.session.close()

    if records == None:
      return prods

    for record in records:
      inspector = inspect(record)
      column_names = [column.key for column in inspector.mapper.column_attrs]
      values = [getattr(record, column_name) for column_name in column_names]
      prods.append(values)

    db.session.close()
    return prods


  def add_cart_item(self,usr, product_ID, prod_name):
    flag = 0
    db.session.begin()
    record = U_Cart.query.filter_by(U_ID=usr,Product_ID=product_ID).first()
    try:
      if record != None:
        print(record)
        flag = 1
    except:
       flag = 0
    db.session.close()
    if flag==1:
      return flag

    db.session.begin()
    try:
      record = U_Cart(U_ID=usr,Product_ID=product_ID,Product_Name=prod_name,Product_Status=1)
      db.session.add(record)
      db.session.commit()
      flag = 1
    except:
      print("NOOOOOOOOOOOOOOOOOOOOOOOO")
      db.session.rollback()
    finally:
      db.session.close()
      return flag


  def remove_cart_item(self,product_ID,prod_name):
    flag = 0
    db.session.begin()
    try:
      record = U_Cart.query.filter_by(Product_ID=product_ID,Product_Name=prod_name).first()
      db.session.delete(record)
      db.session.commit()
      flag = 1
    except:
      db.session.rollback()
    finally:
      db.session.close()
      return flag


  def is_feat(self,product_ID,prod_name):
    prods = self.fetch_feat_prods()
    for product in prods:
      if str(product[0]) == str(product_ID) and product[1] == prod_name :
        return 1
    return 0


  def remove_feat(self, product_ID,prod_name):
    db.session.begin()
    flag = 0
    try:
      record = Feature.query.filter_by(Product_ID=product_ID, Product_Name=prod_name).first()
      if record:
        db.session.delete(record)
        db.session.commit()
        flag = 1
    except:
      db.session.rollback()
    finally:
      db.session.close()
      return flag


  def buy_product(self,product_ID,prod_name,amount,total,U_ID):
    flag = 0
    product = self.fetch_one_prod(prod_name,product_ID)
    if len(product)<=0:
      return flag

    db.session.begin()
    try:
      prod = Product.query.filter_by(ID=product_ID,Name=prod_name).first()
      db.session.add(self.make_log(product,U_ID,amount,total))
      if (float(prod.Stock) - float(amount)) >=0:
        prod.Stock   -= float(amount)
      db.session.commit()
      flag = 1
    except:
      #print("NOOOOOOOOOOOOOOOOOOOOOOOO")
      db.session.rollback()
    finally:
      db.session.close()
      return flag


  def make_log(self,product,U_ID,amount,total):
    log = Trans_rec(U_ID          = U_ID,
                    Product_ID    = product[0],
                    Product_Name  = product[1],
                    Product_Units = product[2],
                    Product_Unit_Price = product[3],
                    Amount_Bought = amount,
                    Category_ID   = product[5],
                    Discount      = product[6],
                    Total         = total,
                    Date_Time     = str(datetime.datetime.now()))
    return log


  def delete_prod(self,prod_Name,ID):
    flag=0
    db.session.begin()
    try:
      product  = Product.query.filter_by(Name=prod_Name, ID=ID).first()
      db.session.delete(product)
      db.session.commit()
      flag = 1
    except:
      db.session.rollback()
    finally:
      db.session.close()
      return flag


  def search_DB(self,squery):
    result     = []
    categories = []
    products   = []
    cats       = self.fetch_cats()
    prods      = self.fetch_all_prods()
    pattern    = r'\w*{}\w*'.format(re.escape(squery))
    pattern2    = r'\b{}\b'.format(re.escape(squery))
    for category in cats:
      match = re.findall(pattern,category[1],flags=re.IGNORECASE)
      if len(match)>0:
        categories.append(category[1])

    for product in prods:
      match1 = re.findall(pattern,product[1],flags=re.IGNORECASE)
      match2 = re.findall(pattern2,str(product[3]))
      if (len(match1) or len(match2)) and (product not in result):
        products.append(product)

    result.append(categories)
    result.append(products)
    return result


class validate():
  def __init__(self,Mail_ID,Usrname,Pwd,Pwd_conf):
    self.Mail_ID  = Mail_ID
    self.Pwd     = Pwd
    self.U_ID     = Usrname
    self.Pwd_conf = Pwd_conf

  def checkPwd(self):
    if self.Pwd_conf == self.Pwd:
      return True
    return False 

  def validatePwd(self):
    #retun 0 if bad
    Blist = ("/","*","%","&","(",")","{","}","[","]","$")
    
    for char in Blist:
      if char in self.Pwd:
        return 0
    return 1

  def validateTxT(self, text):
    #retun 0 if bad
    Blist = ("/","*","%","&","(",")","{","}","[","]","$")
    
    for char in Blist:
      if char in text:
        return 0
    return 1

  def validateName(self):
    #if name exists return 1
    #if name has bad characters return 2
    #if mail exists return 3
    #if name is ok return 0
    db.session.begin()
    name = U_Reg.query.filter_by(U_ID=self.U_ID).first()
    mail = U_Reg.query.filter_by(Mail_ID=self.Mail_ID).first()
    db.session.close()
    if name:
      if name.U_ID:
        return 1
    if not(self.U_ID.isalnum()):
      return 2
    if mail:
      return 3
    return 0

  def add(self):
    if not self.validateName():
      db.session.begin()
      try:
        newUser = U_Reg(U_ID=self.U_ID, Mail_ID=self.Mail_ID,PWD=self.Pwd, ATT=2)
        db.session.add(newUser)
        db.session.flush()
        db.session.commit()
      except:
        db.session.rollback()
      finally:
        db.session.close()
        return 1
    else:
      return 0

  def change_PWD(self, old_PWD):
    db.session.begin()
    try:
      usr = U_Reg.query.filter_by(U_ID=self.U_ID).first()
    
      print(usr.PWD)
      if usr.PWD == old_PWD:
        usr.PWD = self.Pwd
        db.session.commit()
        db.session.close()
        return 1
      else:
        db.session.close()
        return 2
    except:
      db.session.rollback()
      return 0
    finally:
      db.session.close()
