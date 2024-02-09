from flask import Flask, request
from flask import render_template, redirect, session, url_for
from scripts.config import *
from scripts.models import *
from scripts.view   import *

tempvar = 0

#MAIN LANDING
@app.route('/', methods=["GET","POST"])
def Landing():
  return f"<h1>Hola</h1>"


#LOGIN TO THE WEBSITE
@app.route('/login', methods=["GET","POST"])
def login():
  if request.method == "POST":
    mail_id = request.form.get("email_id")
    pwd     = request.form.get("password")
    remember= bool(request.form.get('remember_me'))
    global tempvar

    if remember:
      session.permanent = True
   
    #validate here

    #Auth here
    Curr_Usr= user(mail_id,pwd) 
    usr_val = validate(None,None,pwd,None)

    if not (usr_val.validatePwd()):
      return render_template("login1.html", badCred=1, jusReg=0,msg=" Only special characters allowed are: !,@,#,%,^")

    if Curr_Usr.Valid:
      Usr_dat = {'Mail_ID':Curr_Usr.Mail_ID,'U_ID':Curr_Usr.U_ID, 'Valid':Curr_Usr.Valid, 'SPAtt':Curr_Usr.SPAtt}
      session["Curr_Usr"] = Usr_dat
      return redirect(url_for("user_page",usr=Curr_Usr.U_ID))

    else:
      return render_template("login1.html", badCred=1, jusReg=0,msg="")
      
  if "Curr_Usr" in session:
    return redirect(url_for("user_page",usr= session["Curr_Usr"]["U_ID"]))

  if tempvar:
    tempvar = 0
    return render_template("login1.html", badCred=0, jusReg=1,msg="")

  return render_template("login1.html", badCred=0,jusReg=0,msg="")


#LOGOUT
@app.route('/logout', methods=["GET"])
def logout():
  session.pop("Curr_Usr", None)
  return redirect(url_for("login"))


#REGISTER NEW USERS
@app.route('/register',methods=["GET","POST"])
def register():
  if request.method == "POST":
    U_ID    = request.form.get("name")
    mail_id = request.form.get("email_id")
    pwd     = request.form.get("password")
    pwd_conf= request.form.get("Conf_password")

    new_usr = validate(mail_id,U_ID, pwd, pwd_conf)

    #validate
    if new_usr.validateName() != 0:
      return render_template("register.html", badpwd=0, badname=new_usr.validateName(),popup="None")

    #check password
    if not(new_usr.checkPwd()):
      return render_template("register.html", badpwd=1, badname=0,popup="None")

    if not(new_usr.validatePwd()):
      return render_template("register.html", badpwd=0, badname=0,popup=" Only special characters allowed are: !,@,#,%,^")

    global tempvar
    tempvar = 1

    #ADD TO DB
    if new_usr.add():
      return redirect(url_for("login"))
  return render_template("register.html", badpwd=0,badname=0,popup="None")

@app.route('/user=<usr>',methods=["GET","POST"])
def user_page(usr):
  if "Curr_Usr" in session:
    Usr_dat  = session["Curr_Usr"]
    usr_hndl = user(Usr_dat["Mail_ID"],None)
    featured = usr_hndl.fetch_feat_prods()
    response_txt = "Sorry we couldn't find what you were looking for :("

    if request.method == "GET":
      if Usr_dat["U_ID"] == usr:
        if len(featured)>0:
          print(featured)
          return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=featured,clist=None,source="featured",squery="",r_txt=None,popup="Default")
        else:
          return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=featured,clist=None,source="featured",squery="",r_txt=response_txt,popup="Default")
      else:
        return redirect(url_for("login"))

    else:
      S_query    = request.form.get("search")
      text_val  = validate(None,None,None,None)
      if not text_val.validateTxT(S_query):
        return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=[],clist=None,source="search",squery=S_query,r_txt="Dont enter special characters into the search box (* ￣︿￣)",popup="Default")

      found      = usr_hndl.search_DB(S_query)
      products   = found[1]
      categories = found[0]

      if len(products)>0:
        if len(categories) <= 0:
          return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,clist=None,source="search",squery=S_query,r_txt=None,popup="Default")
        else:
          return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,clist=categories,source="search",squery=S_query,r_txt=None,popup="Default")
      else:
        if len(categories) <= 0:
          return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,clist=None,source="search",squery=S_query,r_txt=response_txt,popup="Default")
        return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,clist=categories,source="search",squery=S_query,r_txt=response_txt,popup="Default")

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>,popup=<popup>',methods=["GET","POST"])
def user_page_msg(usr, popup):
  if "Curr_Usr" in session:
    Usr_dat  = session["Curr_Usr"]
    usr_hndl = user(Usr_dat["Mail_ID"],None)
    featured = usr_hndl.fetch_feat_prods()
    response_txt = "Sorry we couldn't find what you were looking for :("

    if request.method == "GET":
      if Usr_dat["U_ID"] == usr:
        if len(featured)>0:
          return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=featured,clist=None,source="featured",squery="",r_txt=None,popup=popup)
        else:
          return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=featured,clist=None,source="featured",squery="",r_txt=response_txt,popup=popup)
      else:
        return redirect(url_for("login"))

    else:
      S_query    = request.form.get("search")
      found      = usr_hndl.search_DB(S_query)
      products   = found[1]
      categories = found[0]
      if len(products)>0:
        if len(categories) <= 0:
          return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,clist=None,source="search",squery=S_query,r_txt=None,popup=popup)
        else:
          return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,clist=categories,source="search",squery=S_query,r_txt=None,popup=popup)
      else:
        if len(categories) <= 0:
          return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,clist=None,source="search",squery=S_query,r_txt=response_txt,popup=popup)
        return render_template("user.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,clist=categories,source="search",squery=S_query,r_txt=response_txt,popup=popup)

  else:
    return redirect(url_for("login"))



@app.route('/user=<usr>/cart=<popup>',methods=["GET"])
def cart(usr, popup):
  if "Curr_Usr" in session:
    Usr_dat  = session["Curr_Usr"]
    usr_hndl = user(Usr_dat["Mail_ID"],None)
    items    = usr_hndl.fetch_cart_items()
    #print(usr_hndl.fetch_cart_items())
    products = []
    response_txt = "Your cart is empty!"

    if request.method == "GET":
      if Usr_dat["U_ID"] == usr:
        if len(items)>0:
          for item in items:
            product = []
            if item[1] == Usr_dat["U_ID"]:
              product = usr_hndl.fetch_one_prod(item[3],item[2])
              if len(product)<=0:
                product = [item[2],item[3],0,0,0,0,0]
              products.append(product)
          return render_template("cart.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,clist=None,squery="",r_txt=None,popup=popup)
        else:
          return render_template("cart.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,clist=None,squery="",r_txt=response_txt,popup=popup)
      else:
        return redirect(url_for("login"))

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/add_cart=<product_ID>,<prod_name>',methods=["POST"])
def add_cart_item(usr, product_ID, prod_name):
  if "Curr_Usr" in session:
    Usr_dat  = session["Curr_Usr"]
    usr_hndl = user(Usr_dat["Mail_ID"],None)

    if usr_hndl.add_cart_item(usr,product_ID,prod_name):
      return redirect(url_for("cart",usr=usr,popup="Item Added"))
    return redirect(url_for("cart",usr=usr,popup="Unable to Add item"))

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/remove_cart=<product_ID>,<prod_name>',methods=["POST"])
def remove_cart_item(usr, product_ID, prod_name):
  if "Curr_Usr" in session:
    Usr_dat  = session["Curr_Usr"]
    usr_hndl = user(Usr_dat["Mail_ID"],None)

    if usr_hndl.remove_cart_item(product_ID,prod_name):
      return redirect(url_for("cart",usr=usr,popup="Item removed"))
    return redirect(url_for("cart",usr=usr,popup="Unable to remove"))

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/Buy=<product_ID>,<prod_name>',methods=["GET"])
def buy_product(usr,product_ID, prod_name,popup=""):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]

    product    = None
    usr_hndl   = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    product    = usr_hndl.fetch_one_prod(prod_name,product_ID)
    flag = 0
    
    if len(product)>0:
      flag = 1

    if not flag:
      return redirect(url_for("user_page",usr=usr))

    category = usr_hndl.fetch_cat_ID(product[5])
    cat_Name = category.Name
    if product[6] == None:
      product[6] = 0 

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          return render_template("buy.html",usr=usr,admin=Usr_dat["SPAtt"],product_ID=product_ID,prod_name=prod_name,plist=product,cat=cat_Name,fonts=fonts,popup=popup)
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("user_page",usr=usr))

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/Buy=<product_ID>,<prod_name>,popup=<popup>',methods=["GET"])
def buy_product_err(usr,product_ID, prod_name,popup):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]

    product    = None
    usr_hndl   = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    product    = usr_hndl.fetch_one_prod(prod_name,product_ID)
    flag = 0
    
    if len(product)>0:
      flag = 1

    if not flag:
      return redirect(url_for("user_page",usr=usr))

    category = usr_hndl.fetch_cat_ID(product[5])
    cat_Name = category.Name
    if product[6] == None:
      product[6] = 0 

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          return render_template("buy.html",usr=usr,admin=Usr_dat["SPAtt"],product_ID=product_ID,prod_name=prod_name,plist=product,cat=cat_Name,fonts=fonts,popup=popup)
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("user_page",usr=usr))

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/Bought=<product_ID>,<prod_name>,<currency>/<unit>,<prod_rate>,<prod_stock>,<prod_cat_ID>,<total>',methods=["POST"])
def finalize_buy(usr,product_ID, prod_name, currency,unit, prod_rate, prod_stock, prod_cat_ID,total):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]

    product    = None
    usr_hndl   = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    product    = usr_hndl.fetch_one_prod(prod_name,product_ID)
    amount     = request.form.get("Amount")
    prod_units = currency + "/" + unit
    assembled  = [product_ID,prod_name,prod_units,prod_rate,prod_stock,prod_cat_ID]
    category = usr_hndl.fetch_cat_ID(product[5])
    cat_Name = category.Name
    flag = 0
    ctr  = 0
    for item in assembled:
      if str(product[ctr]) != str(item):
        print(products[ctr],item)
        break
      ctr += 1

    if ctr == 6:
      if product[6] != None:
        new_total = (product[3] - product[3]*(product[6]/100))*float(amount)
      else:
        new_total = product[3]*float(amount)
      if float(total) == new_total: 
        flag = 1

    if not flag:
      return redirect(url_for("user_page",usr=usr))

    try:
      if Usr_dat["U_ID"] == usr:
        #print("################TRANSACTION!!!!###################")
        if usr_hndl.buy_product(product_ID,prod_name,amount,total,Usr_dat["U_ID"]):
          return redirect(url_for("Reciept",usr=usr,product_ID=product_ID,prod_name=prod_name,amount=amount,total=new_total))
        else:
          return redirect(url_for("buy_product_err",usr=usr,product_ID=product_ID,prod_name=prod_name,popup="Please try again"))
      else:
        return redirect(url_for("login"))
    except:
      return redirect(url_for("buy_product_err",usr=usr,product_ID=product_ID,prod_name=prod_name,popup="Please try again"))

  else:
    return redirect(url_for("login"))



@app.route('/user=<usr>/Reciept=<product_ID>,<prod_name>,<amount>,<total>',methods=["GET"])
def Reciept(usr,product_ID, prod_name,amount,total):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]

    product    = None
    usr_hndl   = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    product    = usr_hndl.fetch_one_prod(prod_name,product_ID)
    if product[6] == None:
      product[6] = 0
    category = usr_hndl.fetch_cat_ID(product[5])
    cat_Name = category.Name

    if Usr_dat["U_ID"] == usr:
      return render_template("bought_msg.html",usr=usr,admin=Usr_dat["SPAtt"],plist=product,cat=cat_Name,Amount=amount,total=total,fonts=fonts,popup="")
    else:
      return redirect(url_for("login"))

  else:
    return redirect(url_for("login"))



@app.route('/user=<usr>/Category=<cat>',methods=["GET"])
def category_page(usr, cat):
  if "Curr_Usr" in session:
    Usr_dat  = session["Curr_Usr"]
    usr_hndl = user(Usr_dat["Mail_ID"],None)
    products = usr_hndl.fetch_prods(cat)
    response_txt = "Sorry we couldn't find what you were looking for :("
    print(products)

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          if len(products)>0:
            print("here")
            return render_template("category.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,cat=cat,r_txt=None)
          else:
            return render_template("category.html",usr=usr, admin=Usr_dat["SPAtt"],plist=products,cat=cat,r_txt=response_txt)
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("login"))
  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/Categories',methods=["GET"])
def all_categories(usr):
  if "Curr_Usr" in session:
    Usr_dat  = session["Curr_Usr"]
    usr_hndl = user(Usr_dat["Mail_ID"],None)
    categories = usr_hndl.fetch_cats()

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          return render_template("all_categories.html",usr=usr, admin=Usr_dat["SPAtt"],clist=categories,r_txt=None)
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("login"))
  else:
    return redirect(url_for("login"))


@app.route('/profile=<usr>',methods=["GET"])  
def about_user(usr):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["U_ID"] == usr:
      return render_template("user_Profile.html",usr=usr, mail=Usr_dat["Mail_ID"], admin=Usr_dat["SPAtt"])
    else:
        return redirect(url_for("login"))
  else:
    return redirect(url_for("login"))


@app.route('/profile=<usr>/change_Password',methods=["GET","POST"])  #This endpoint isnt open... TAKE DIVERSION
def change_PWD(usr):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]

    if request.method == "GET":
      if Usr_dat["U_ID"] == usr:
        return render_template("change_password.html",usr=usr, mail=Usr_dat["Mail_ID"], admin=Usr_dat["SPAtt"],popup="")
      else:
        return redirect(url_for("login"))

    elif request.method == "POST":
      old_pwd     = request.form.get("old_password")
      new_pwd     = request.form.get("new_password")
      pwd_conf    = request.form.get("Conf_new_password")
      status      = 0

      usr_hndl = validate(Usr_dat["Mail_ID"],usr, new_pwd, pwd_conf)

      if usr_hndl.validateName() == 1:
        if not(usr_hndl.checkPwd()):
          return render_template("change_password.html",usr=usr, mail=Usr_dat["Mail_ID"], admin=Usr_dat["SPAtt"], popup="Password doesn't match!")
        elif not(usr_hndl.validatePwd()):
          return render_template("change_password.html",usr=usr, mail=Usr_dat["Mail_ID"], admin=Usr_dat["SPAtt"], popup="Only special characters allowed are: !,@,#,%,^")
        elif status := usr_hndl.change_PWD(old_pwd):
          if status == 1:
            return render_template("change_password.html",usr=usr, mail=Usr_dat["Mail_ID"], admin=Usr_dat["SPAtt"], popup="Successfully changed!!!")
          elif status == 2:
            return render_template("change_password.html",usr=usr, mail=Usr_dat["Mail_ID"], admin=Usr_dat["SPAtt"], popup="Wrong password")

      return render_template("change_password.html",usr=usr, mail=Usr_dat["Mail_ID"], admin=Usr_dat["SPAtt"], popup="Failed operation!")

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/management',methods=["GET"])
def management(usr):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page",usr=usr))
    if Usr_dat["U_ID"] == usr:
      cats = None
      usr_hndl = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data

      cats = usr_hndl.fetch_cats()

      return render_template("management.html",usr=usr,category=cats,fonts=fonts)
    else:
        return redirect(url_for("login"))
  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/Add_Category',methods=["GET","POST"])
def add_category(usr):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    cats = None

    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page",usr=usr))

    usr_hndl = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data

    if request.method == "GET":
      if Usr_dat["U_ID"] == usr:
        return render_template("add_category.html",usr=usr,category=cats,fonts=fonts,popup="")
      else:
        return redirect(url_for("login"))

    else:
      cat_name = request.form.get("cat_name")
      text_val = validate(None,None,cat_name,None)
      if not text_val.validatePwd():
        return render_template("add_category.html",usr=usr,category=cats,fonts=fonts,popup="Only special characters allowed are: !,@,#,%,^")
      
      if usr_hndl.add_cat(cat_name):
        return redirect(url_for("management",usr =usr))
      else:
        return render_template("add_category.html",usr=usr,category=cats,fonts=fonts,popup="Something went wrong!!")

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/<cat>/Add_Product',methods=["GET","POST"])
def add_product(usr, cat):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page"))
    
    cats = None
    usr_hndl = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    cats = usr_hndl.fetch_cats()

    flag = 0
    for category in cats:
      if cat in category:
        flag = 1

    if not flag:
      return redirect(url_for("management",usr=usr))

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          return render_template("add_product.html",usr=usr,category=cat,fonts=fonts,popup="")
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("user_page"))

    else:
      prod_name = request.form.get("prod_name")
      units     = request.form.get("units")
      Rateper   = request.form.get("Rateper")
      Quantity  = request.form.get("Quantity")
      New_cat   = request.form.get("Category")
      text_val  = validate(None,None,None,None)
      new_units = units
      ind = new_units.index("/")
      new_units = new_units[:ind] + new_units[ind+1:]
      tlist     = [prod_name,new_units,Rateper,Quantity]

      if len(New_cat) > 0:
        if usr_hndl.add_cat(New_cat):
          cat = New_cat
        else:
          return render_template("add_product.html",usr=usr,category=cats,fonts=fonts,popup="Couldn't add category :(")

      for text in tlist:
        if not text_val.validateTxT(text):
          return render_template("add_product.html",usr=usr,category=cats,fonts=fonts,popup="Only special characters allowed are: !,@,#,%,^")
      
      if usr_hndl.add_prod(prod_name,units,Rateper,Quantity,cat):
        return redirect(url_for("management",usr =usr))
      else:
        return render_template("add_category.html",usr=usr,category=cats,fonts=fonts,popup="Something went wrong!!")

  else:
    return redirect(url_for("login"))



@app.route('/user=<usr>/edit_Category=<cat>',methods=["GET","POST"])
def edit_cat(usr, cat):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page",usr=usr))
    
    cats = None
    usr_hndl = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    cats = usr_hndl.fetch_cats()

    flag = 0
    for category in cats:
      if cat in category:
        flag = 1

    if not flag:
      return redirect(url_for("management",usr=usr))

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          return render_template("edit_category.html",usr=usr,category=cat,cat=cat,fonts=fonts,popup="")
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("user_page",usr=usr))

    else:
      new_Name = request.form.get("cat_name")
      text_val  = validate(None,None,None,None)
      tlist     = [new_Name]

      for text in tlist:
        if not text_val.validateTxT(text):
          return render_template("edit_Category.html",usr=usr,category=cats,cat=cat,fonts=fonts,popup="Only special characters allowed are: !,@,#,%,^")
      
      if usr_hndl.edit_cat(cat,new_Name):
        return redirect(url_for("management",usr =usr))
      else:
        return render_template("edit_Category.html",usr=usr,category=cats,cat=cat,fonts=fonts,popup="Something went wrong!!")

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/edit_Product=<product_ID>,<prod_name>',methods=["GET","POST"])
def edit_prod(usr, product_ID, prod_name):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page",usr=usr))
    
    product    = None
    usr_hndl   = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    product    = usr_hndl.fetch_one_prod(prod_name,product_ID)
    flag = 0
    
    if len(product)>0:
      flag = 1

    if not flag:
      return redirect(url_for("management",usr=usr))

    category    = usr_hndl.fetch_cat_ID(product[5])
    cat_Name    = category.Name
    category_ID = category.ID 

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          return render_template("edit_product.html",usr=usr,product_ID=product_ID,prod_name=prod_name,plist=product,cat=cat_Name,fonts=fonts,popup="")
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("user_page",usr=usr))

    else:
      Nprod_name = request.form.get("prod_name")
      Nunits     = request.form.get("units")
      NRateper   = request.form.get("Rateper")
      NQuantity  = request.form.get("Quantity")
      NDiscount  = request.form.get("Discount")
      text_val  = validate(None,None,None,None)
      new_units = Nunits
      ind = new_units.index("/")
      new_units = new_units[:ind] + new_units[ind+1:]
      old_tlist = [product[1],product[2],product[3],product[4]]
      tlist     = [Nprod_name,new_units,NRateper,NQuantity]


      for text in tlist:
        if not text_val.validateTxT(text):
          return render_template("edit_product.html",usr=usr,product_ID=product_ID,prod_name=prod_name,plist=product,cat=cat_Name,fonts=fonts,popup="Only special characters allowed are: !,@,#,%,^")

      if Nprod_name == None or Nprod_name=="":
        Nprod_name = product[1]
      if Nunits == None or Nunits=="":
        Nunits = product[2]
      if NRateper == None or NRateper=="":
        NRateper = product[3]
      if NQuantity == None or NQuantity=="":
        NQuantity = product[4]
      if NDiscount == None or NDiscount =="":
        NDiscount = product[6]

      if usr_hndl.edit_prod(product_ID,Nprod_name,Nunits,NRateper,NQuantity,cat_Name,category_ID,NDiscount):
        return redirect(url_for("delete",usr =usr,cat=cat_Name))
      else:
        return render_template("edit_product.html",usr=usr,product_ID=product_ID,prod_name=prod_name,plist=product,cat=cat_Name,fonts=fonts,popup="Something went wrong!!")
  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/feat_Product=<product_ID>,<prod_name>',methods=["GET","POST"])
def feature_prod(usr, product_ID, prod_name):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page",usr=usr))
    
    product    = None
    usr_hndl   = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    product    = usr_hndl.fetch_one_prod(prod_name,product_ID)
    flag = 0
    
    if len(product)>0:
      flag = 1

    if not flag:
      return redirect(url_for("management",usr=usr))

    category    = usr_hndl.fetch_cat_ID(product[5])
    cat_Name    = category.Name
    category_ID = category.ID 
    prods    = usr_hndl.fetch_prods(cat_Name)

    if usr_hndl.is_feat(product_ID,prod_name):
      if usr_hndl.remove_feat(product_ID,prod_name):
        return render_template("delete.html",usr=usr,category_ID=category_ID,cat=cat_Name,products=prods,fonts=fonts,popup="Successfully Removed")
      else:
        return render_template("delete.html",usr=usr,category_ID=category_ID,cat=cat_Name,products=prods,fonts=fonts,popup="Couldn't remove")
    elif usr_hndl.feat_prod(product_ID,prod_name):
      return render_template("delete.html",usr=usr,category_ID=category_ID,cat=cat_Name,products=prods,fonts=fonts,popup="Successfully added")
    else:
      return render_template("delete.html",usr=usr,category_ID=category_ID,cat=cat_Name,products=prods,fonts=fonts,popup="Couldn't add")

  else:
    return redirect(url_for("login"))



@app.route('/user=<usr>/delete=<cat>',methods=["GET","POST"])
def delete(usr, cat):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page",usr=usr))
    
    cats     = None
    usr_hndl = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    cats     = usr_hndl.fetch_cats()
    prods    = usr_hndl.fetch_prods(cat)

    flag = 0
    for category in cats:
      if cat in category:
        cats = category
        flag = 1
        break

    if not flag:
      return redirect(url_for("management",usr=usr))

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          return render_template("delete.html",usr=usr,category_ID=cats[0],cat=cats[1],products=prods,fonts=fonts,popup="")
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("user_page",usr=usr))

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/delete_Category=<category_ID>,<cat>',methods=["GET"])
def delete_cat(usr,category_ID, cat):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page",usr=usr))

    cats     = None
    usr_hndl = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    cats     = usr_hndl.fetch_cats()
    flag = 0
    for category in cats:
      if cat in category:
        flag = 1

    if not flag:
      return redirect(url_for("management",usr=usr))

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          return render_template("delete_category.html",usr=usr,category_ID=category_ID,cat=cat,fonts=fonts,popup="")
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("user_page",usr=usr))

  else:
    return redirect(url_for("login"))


#del cat is a hidden endpoint, its there to descern the users choice, no page is displayed
@app.route('/user=<usr>/Del_cat=<category_ID>,<cat>',methods=["GET","POST"])
def Del_cat(usr, category_ID, cat):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page",usr=usr))

    cats     = None
    usr_hndl = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    cats     = usr_hndl.fetch_cats()
    flag = 0
    for category in cats:
      if cat in category:
        flag = 1

    if not flag:
      return redirect(url_for("management",usr=usr))

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          if usr_hndl.delete_cat(cat,category_ID):
            return redirect(url_for("management",usr=usr))
          else:
            return render_template("delete_category.html",usr=usr,cat=cat,fonts=fonts,popup="Something went wrong!")
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("user_page",usr=usr))

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/delete_Product=<product_ID>,<prod_name>',methods=["GET"])
def delete_product(usr,product_ID, prod_name):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page",usr=usr))

    product    = None
    usr_hndl   = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    product    = usr_hndl.fetch_one_prod(prod_name,product_ID)
    flag = 0
    
    if len(product)>0:
      flag = 1

    if not flag:
      return redirect(url_for("management",usr=usr))

    category = usr_hndl.fetch_cat_ID(product[5])
    cat_Name = category.Name

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          return render_template("delete_product.html",usr=usr,product_ID=product_ID,prod_name=prod_name,cat=cat_Name,fonts=fonts,popup="")
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("user_page",usr=usr))

  else:
    return redirect(url_for("login"))


@app.route('/user=<usr>/Del_prod=<product_ID>,<prod_name>',methods=["GET","POST"])
def Del_prod(usr, product_ID, prod_name):
  if "Curr_Usr" in session:
    Usr_dat = session["Curr_Usr"]
    if Usr_dat["SPAtt"] != 1:
      return redirect(url_for("user_page",usr=usr))

    product    = None
    usr_hndl   = user(Usr_dat["Mail_ID"],None) #creates a dumb user class just to fetch open access data
    product    = usr_hndl.fetch_one_prod(prod_name,product_ID)
    flag = 0
    
    if len(product)>0:
      flag = 1

    if not flag:
      return redirect(url_for("management",usr=usr))

    category = usr_hndl.fetch_cat_ID(product[5])
    cat_Name = category.Name

    if request.method == "GET":
      try:
        if Usr_dat["U_ID"] == usr:
          if usr_hndl.delete_prod(prod_name,product_ID):
            return redirect(url_for("management",usr=usr))
          else:
            return render_template("delete_product.html",usr=usr,product_ID=product_ID,prod_name=prod_name,cat=cat_Name,fonts=fonts,popup="Something went wrong!")
        else:
          return redirect(url_for("login"))
      except:
        return redirect(url_for("user_page",usr=usr))

  else:
    return redirect(url_for("login"))



if __name__ == '__main__':
  app.run(host='0.0.0.0',port=8000,debug = True)