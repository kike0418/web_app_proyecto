import web, datetime

db = web.database(dbn='postgres', host='ec2-54-221-254-72.compute-1.amazonaws.com', db='d5tk0u6f532jff', user='jckdnmwgccphuk', pw='mf9OUObWFXqnhZMmpQbjtrGCuE')

def get_posts():
    return db.select('reporte', order='id_reporte ASC')

def get_post(id):
    try:
        return db.select('reporte', where='id_reporte=$id', vars=locals())[0]
    except IndexError:
        return None

def new_post(MD, ModelD, Descripcion):
    db.insert('reporte', marca_disposito=MD, modelo_dispositivo=ModelD, tiempo_dereporte=datetime.datetime.utcnow(), descripcion=Descripcion)

def del_post(id):
    db.delete('reporte', where="id_reporte=$id", vars=locals())

def update_post(id_reporte, MD, ModelD, Descripcion):
    db.update('reporte', where="id_reporte=$id_reporte", vars=locals(),
        marca_disposito=MD, modelo_dispositivo=ModelD, descripcion=Descripcion)