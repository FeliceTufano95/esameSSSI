from DAO.ClienteDAO import ClienteDAO
from flask import Flask
from flask.cli import with_appcontext
from DB import db
from DAO.GiostraDAO import GiostraDAO
from DAO.BigliettoDAO import BigliettoDAO
from DAO.OspiteDAO import OspiteDAO
from DAO.PrenotazioneDAO import PrenotazioneDAO
app = Flask(__name__)
    

def readUtente(nickname):
    with app.app_context():
        cliente = db.query_db('SELECT * FROM Cliente WHERE Cliente.nickname="'+nickname+'"', one=True)
        try:
            clienteDAO = ClienteDAO(cliente['nickname'], cliente['email'], cliente['password'], cliente['eta'], cliente['altezza'], None)
            return clienteDAO
        except:
            print('Utente non trovato')
            raise
    
# with app.app_context():
#     t = readUtente("Test")
#     print(t.nickname, t.password, t.altezza, t.eta, t.biglietto)
    
def createUtente(cliente):
    with app.app_context():
        try:
            db.query_db('INSERT INTO Cliente VALUES("'+cliente.nickname+'","'+cliente.password+'","'+cliente.email+'",'+str(cliente.eta)+','+str(cliente.altezza)+')')
            return
        except:
            print('Inserimento fallito')
            raise

# with app.app_context():
#     createUtente(ClienteDAO("Test2", "mail@mail.it", "123", 16, 1.8, None))
    
def readClientiInCoda(nomeGiostra):
    with app.app_context():
        coda = db.query_db('SELECT * FROM Giostra WHERE Giostra.nome="'+nomeGiostra+'"', one=True)
        return coda['numero_persone']

# with app.app_context():
#      t = readClientiInCoda("Bruco mela")
#      print(t)
        
def readGiostre():
    with app.app_context():
        giostre = db.query_db('SELECT * FROM Giostra')
        arrayGiostre = []
        for giostra in giostre:
            arrayGiostre.append(GiostraDAO(giostra['nome'],giostra['capienza'],giostra['durata'],giostra['limite_eta'],giostra['limite_altezza'],giostra['descrizione'],giostra['stato_funzionamento'], giostra['numero_persone']))
        return arrayGiostre

# with app.app_context():
#      t = readGiostre()
#      for g in t:
#         print(g.nome)

def createBiglietto(data, ospiti, nickname):
    with app.app_context():
        db.query_db('INSERT INTO Biglietto(data, Clientenickname) VALUES("'+data+'", "'+nickname+'")')
        biglietto = db.query_db('SELECT * FROM Biglietto WHERE last_insert_rowid()=Biglietto.ROWID', one=True)

        listaOspitiDAO = []
        for ospite in ospiti:
            db.query_db('INSERT INTO Ospite(Bigliettocodice, nome, eta, altezza) VALUES('+str(biglietto['codice'])+',"'+ospite.nome+'",'+str(ospite.eta)+','+str(ospite.altezza)+')')
            listaOspitiDAO.append(OspiteDAO(ospite.nome, ospite.eta, ospite.altezza))
        
        bigliettoDAO = BigliettoDAO(biglietto['codice'], biglietto['data'], listaOspitiDAO)
        return bigliettoDAO

# with app.app_context():
#     listaO = []
#     listaO.append(OspiteDAO("Ospite1", 15, 1.5))
#     t = createBiglietto("14/02/2021",listaO, "Test")
#     print(t.codice, t.data, t.ospiti)
    
def createPrenotazione(prenotazione):
    with app.app_context():
        try:
            db.query_db('INSERT INTO Prenotazione VALUES("'+prenotazione.nome_cliente+'","'+prenotazione.nome_giostra+'","'+prenotazione.fascia_oraria+'",'+str(prenotazione.numero_ospiti)+')')
            numero_persone_in_coda = readClientiInCoda(prenotazione.nome_giostra)+prenotazione.numero_ospiti+1
            db.query_db('UPDATE Giostra SET numero_persone='+str(numero_persone_in_coda)+' WHERE Giostra.nome="'+prenotazione.nome_giostra+'"')
        except:
            raise

# with app.app_context():
#     insertClienteInCoda(PrenotazioneDAO("11:30-12:00", 1, "Carosello", "Test"))
        
def getGiostra(nomeGiostra):
    with app.app_context():
        giostra_query = db.query_db('SELECT * FROM Giostra WHERE Giostra.nome = \''+nomeGiostra+'\'',one = True)
        giostra = GiostraDAO(giostra_query['nome'],giostra_query['capienza'],giostra_query['durata'],
        giostra_query['limite_eta'],giostra_query['limite_altezza'],giostra_query['descrizione'],giostra_query['stato_funzionamento'], giostra_query['numero_persone'])
        return giostra

# with app.app_context():
#     g = getGiostra("Bruco mela")
#     print(g.nome, g.numero_persone)

def getPrenotazioni(nomeCliente):
    with app.app_context():
        prenotazioni = db.query_db('SELECT * FROM Prenotazione WHERE Prenotazione.Clientenickname="'+nomeCliente+'"')
        listaPrenotazioniDAO = []
        for prenotazione in prenotazioni:
            listaPrenotazioniDAO.append(PrenotazioneDAO(prenotazione['fascia_oraria'], prenotazione['numero_ospiti'], prenotazione['Giostranome'], prenotazione['Clientenickname']))
        return listaPrenotazioniDAO

# with app.app_context():
#     p = getPrenotazioni("Test")
#     for pi in p:
#         print(pi.nome_giostra)

#     p = getPrenotazioni("Test2")
#     for pi in p:
#         print(pi.nome_giostra)


def checkPrenotazione(nomeCliente, nomeGiostra, fasciaOraria):
    with app.app_context():
        prenotazione = db.query_db('SELECT * FROM Prenotazione WHERE Prenotazione.Clientenickname="'+nomeCliente+'" AND Prenotazione.Giostranome="'+nomeGiostra+'" AND Prenotazione.fascia_oraria="'+fasciaOraria+'"',one=True)

        if prenotazione != None:
            return True
        
        return False

# with app.app_context():
#     print(checkPrenotazione("Test", "Bruco mela", "15:30-15:45"))
#     print(checkPrenotazione("Test2", "Bruco mela", "15:30-15:45"))

def eliminaPrenotazione(nomeCliente, nomeGiostra):
    with app.app_context():
        numero_persone = db.query_db('SELECT numero_ospiti FROM Prenotazione WHERE Prenotazione.Clientenickname= "'+nomeCliente+'" AND Prenotazione.Giostranome="'+nomeGiostra+'"',one=True)
        numero_persone_coda = db.query_db('SELECT numero_persone FROM Giostra WHERE Giostra.nome=\''+nomeGiostra+'\'', one=True)
        persone = numero_persone_coda['numero_persone']-numero_persone['numero_ospiti']-1
        db.query_db('UPDATE Giostra SET numero_persone=\''+str(persone)+'\' WHERE Giostra.nome=\''+nomeGiostra+'\'')
        db.query_db('DELETE FROM Prenotazione WHERE Prenotazione.Clientenickname= "'+nomeCliente+'" AND Prenotazione.Giostranome="'+nomeGiostra+'"')

# with app.app_context():
#     eliminaPrenotazione("Test", "Carosello")

def getFasciaOraria(nomeCliente, nomeGiostra):
    with app.app_context():
        fascia_oraria = db.query_db('SELECT fascia_oraria FROM Prenotazione WHERE Prenotazione.Clientenickname= "'+nomeCliente+'" AND Prenotazione.Giostranome="'+nomeGiostra+'"',one=True)
        return fascia_oraria['fascia_oraria']

# with app.app_context():
#     print(selectFasciaOraria("Test", "Bruco mela"))
def getOspiti(codiceBiglietto):
    with app.app_context():
        ospiti = db.query_db("SELECT * FROM Ospite WHERE Ospite.Bigliettocodice=\'"+str(codiceBiglietto)+'\'')
        ospitiDAO = []
        for ospite in ospiti:
            ospitiDAO.append(OspiteDAO(ospite['nome'], ospite['eta'], ospite['altezza']))
        return ospitiDAO

# with app.app_context():
#     o = getOspiti(1)
#     for os in o:
#         print(os.nome)

def getBiglietto(nomeCliente, data):
    with app.app_context():
        try:
            biglietto = db.query_db('SELECT * FROM Cliente JOIN Biglietto ON Cliente.nickname=Biglietto.Clientenickname WHERE Cliente.nickname=\''+nomeCliente+'\' AND Biglietto.data=\''+data+'\'', one=True)
            ospitiDAO = getOspiti(biglietto['codice'])
            bigliettoDAO = BigliettoDAO(biglietto['codice'], biglietto['data'], ospitiDAO)
            return bigliettoDAO
        except:
            raise

def isBigliettoDup(nomeCliente, data):
    with app.app_context():
        biglietto = db.query_db('SELECT * FROM Cliente JOIN Biglietto ON Cliente.nickname=Biglietto.Clientenickname WHERE Cliente.nickname=\''+nomeCliente+'\' AND Biglietto.data=\''+data+'\'', one=True)
        if (biglietto != None):
            return True
        return False

# with app.app_context():
#     b = getBiglietto("Test", "13/02/2021")
#     print(b.codice,b.data,b.ospiti)

def init_db():
    with app.app_context():
        db.init_app(app)
        db.init_db()

def open_db():
    with app.app_context():
        db.init_app(app)
        db.get_db()
        # db.query_db('INSERT INTO Coda(numero_persone) VALUES(0)')
        # db.query_db('INSERT INTO Giostra VALUES("Trenino",15,1,15,2,1.0,"Giostra per i piu piccoli",0,5)')
