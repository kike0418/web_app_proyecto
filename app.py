# encoding: utf-8
import csv
import web
from web import form
from hashlib import md5
import model
urls = ('/', 'index', '/analisis(.*)', 'analisis', '/mapa(.*)', 'mapa', '/login(.*)', 'Login', '/signup', 'SignUp',
    "/logout", "LogOut",'/bd(.*)','Bd', '/view/(\d+)', 'View','/new', 'New','/delete/(\d+)', 'Delete','/edit/(\d+)', 'Edit')

t_globals = {
    'datestr': web.datestr
}
render = web.template.render('templates/', globals=t_globals)

app = web.application(urls, globals())

data = []
estado = []
init = 0
with open("data/DataCNCH.csv", "r") as file_open:
    dat = csv.reader(file_open, delimiter=",")
    for row in dat:
        data.append(row)  
            
    for row in data:
        estado.append(data[init][5])
        init+=1
                
    for i in range(len(estado)-1, -1, -1):
        if estado[i] in estado[:i]:
            del(estado[i])      
   
myform = form.Form(form.Dropdown('Estado', list(estado)),
                  form.Dropdown('Municipio Indigena',['SI', 'NO']))
                
class index:  
    def GET(self):
        return render.index()
    
class analisis:
    
    data = []
    with open("data/DataCNCH.csv", "r") as file_open:
        dat = csv.reader(file_open, delimiter=",")
        for row in dat:
            data.append(row)
            
    def GET(self, form):
        form = myform()
        return render.analisis(form, self.data)
    
    def POST(self, form):
        temp = []
        begin = 0
        form = myform
        if not form.validates(): 
            return render.analisis(form, temp)
        else:
            seleccion = form['Estado'].value
            tipo = form['Municipio Indigena'].value
            for row in self.data:
                if seleccion == self.data[begin][5] and tipo == self.data[begin][10]:
                    temp.append(row)
                begin+=1
            return render.analisis(form, temp)
        
class mapa:
    def GET(self, form): 
        form = myform
        return render.mapa(form)     
        
class SignUp:    
    def GET(self):
        return render.signup()
    
    def POST(self):
        i = web.input()
        if not i.username or not i.password:
            return "Ingrese todos los datos."
        db = web.database(dbn='postgres', host='ec2-54-221-254-72.compute-1.amazonaws.com', db='d5tk0u6f532jff', user='jckdnmwgccphuk', pw='mf9OUObWFXqnhZMmpQbjtrGCuE')
        db.insert("Users", username=i.username,
                  passwords=md5(i.password).hexdigest())
        web.seeother("/bd")

class LogOut:
    def GET(self):
        web.setcookie("webusername", "", expires=-1)
        web.setcookie("webpassword", "", expires=-1)
        web.seeother("/")
        
class Bd:
     def GET(self, form):
        form = myform()
        posts = model.get_posts()
        cookies = web.cookies()
        username = cookies.get("webusername")    
        return render.bd(form, posts, username)
    
     def POST(self,form):
        form = myform()
        i = web.input()
        db = web.database(dbn='postgres', host='ec2-54-221-254-72.compute-1.amazonaws.com', db='d5tk0u6f532jff', user='jckdnmwgccphuk', pw='mf9OUObWFXqnhZMmpQbjtrGCuE')
        q = db.select("Users", where="username=$username",
                      what="passwords", vars={"username": i.username})
        
        if q:
            db_password = list(q)[0]["passwords"]
            if db_password == md5(i.password).hexdigest():
                web.setcookie("webusername", i.username)
                web.setcookie("webpassword", db_password)
                web.seeother("/bd")
            else:
                return "Usuario o clave incorrecto."
        else:
            return "Usuario o clave incorrecto."
        return render.login(form)

        
class View:

    def GET(self, id):
        """ View single post """
        post = model.get_post(int(id))
        return render.view(post)


class New:
    form = web.form.Form(
        web.form.Textbox('MD', web.form.notnull, 
            size=30,
            description="Marca del dispositivo: "),
        web.form.Textbox('ModelD', web.form.notnull, 
            size=30,
            description="Modelo del Dispositivo: "),
        web.form.Textbox('Descripcion', web.form.notnull, 
            size=30,
            description="Descripcion: "),
        web.form.Button('Enviar'),
    )

    def GET(self):
        form = self.form()
        return render.new(form)

    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new(form)
        model.new_post(form.d.MD, form.d.ModelD,form.d.Descripcion)
        raise web.seeother('/bd')


class Delete:

    def POST(self, id):
        model.del_post(int(id))
        raise web.seeother('/bd')


class Edit:
    
    def GET(self, id):
        post = model.get_post(int(id))
        form = New.form()
        form.fill(post)
        return render.edit(post, form)


    def POST(self, id):
        form = New.form()
        post = model.get_post(int(id))
        if not form.validates():
            return render.edit(post, form)
        model.update_post(int(id), form.d.MD, form.d.ModelD, form.d.Descripcion)
        raise web.seeother('/bd')


app = web.application(urls, globals())

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()
