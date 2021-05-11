import DB
from flask import Flask, request, jsonify
import json
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials
from datetime import datetime
from flask import current_app, g
from flask.cli import with_appcontext
import sys
from datetime import timedelta
import DBInterface
import math
from threadNotifica import ThreadNotifica
from threadCliente import ThreadCliente
from DAO.PrenotazioneDAO import PrenotazioneDAO
from DAO.BigliettoDAO import BigliettoDAO
from DAO.ClienteDAO import ClienteDAO
from DAO.OspiteDAO import OspiteDAO
from DAO.GiostraDAO import GiostraDAO
from urllib import unquote
from datetime import time
#prova
ORACHIUSURA = time(hour=21,minute=00)
LIMITENOTIFICA = 15
TEMPONOTIFICA = 10
TEMPOFASCIA = 15

server = Flask(__name__)
print(sys.version)

if not firebase_admin._apps:
    cred = credentials.Certificate('./serverKey/serverkey.json')
    default_app = firebase_admin.initialize_app(cred)
    DBInterface.open_db()

@server.route("/")
def home():
    return "Server onlinePROVA"

@server.route("/registrati", methods=['POST'])
def registrati():
    req_data = request.get_json()
    utenteDAO = ClienteDAO(req_data['nickname'], req_data['email'], req_data['password'], req_data['eta'], req_data['altezza'], None)
    try:
        DBInterface.createUtente(utenteDAO)
        return jsonify (
            status = 200
        )
    except: 
        return 'utente already exists', 403

@server.route("/login", methods=['GET'])
def login():
    username = request.args.get("username")
    password = unquote(request.args.get("password")).decode('utf-8')

    try :
        utente = DBInterface.readUtente(username)
        if (password == utente.password):
            return jsonify(
                nickname = utente.nickname,
                password = utente.password,
                altezza = utente.altezza,
                eta = utente.eta,
                email = utente.email
            )
        return 'utente unauthorized', 401
    except:
        return 'utente not found', 404

@server.route("/accodati", methods=['POST'])
def accodati():
    req_data = request.get_json()

    try:
        fasciaOrariaInizio = req_data['fascia_oraria'].split('-')
        fasciaOrariaInizioData = datetime.strptime(fasciaOrariaInizio[0], "%H:%M")
        fasciaOrariaFineData = datetime.strptime(fasciaOrariaInizio[1], "%H:%M")
        now = datetime.strptime(datetime.now().time().strftime("%H:%M"), "%H:%M")

        if(fasciaOrariaInizioData.time()>ORACHIUSURA):
            return 'La giostra  piena per oggi', 408

        DBInterface.createPrenotazione(PrenotazioneDAO(req_data['fascia_oraria'], req_data['numero_persone_da_accodare'], req_data['nome_giostra'], req_data['nickname']))
        tempoEliminazioneDallaCoda = fasciaOrariaFineData-now
        ThreadCliente(req_data['nickname'],req_data['nome_giostra'], req_data['fascia_oraria'],tempoEliminazioneDallaCoda)
        
        tempoAttesa = fasciaOrariaInizioData-now
        if (tempoAttesa >= timedelta(minutes=LIMITENOTIFICA)):
            print("notifica tra: " + str(tempoAttesa-timedelta(minutes=TEMPONOTIFICA)))
            tempoAttesa=(tempoAttesa-timedelta(minutes=TEMPONOTIFICA)).total_seconds()
            ThreadNotifica(req_data['token_cliente'], tempoAttesa ,req_data['nome_giostra'], req_data['nickname'], req_data['fascia_oraria'])

        return jsonify(
            status = 200
        )
    except:
        return 'bad request', 400

@server.route("/getGiostre", methods=['GET'])
def getGiostre():
    giostre = DBInterface.readGiostre()
    giostreJSON = []
    for giostra in giostre:
        data_set = {"nome_giostra": giostra.nome, "limite_altezza":giostra.limite_altezza, "limite_eta":giostra.limite_eta, "capienza":giostra.capienza,"durata":giostra.durata,"descrizione":giostra.descrizione,"stato_funzionamento":giostra.stato_funzionamento, "numero_persone" : giostra.numero_persone}
        jsondump = json.dumps(data_set)
        giostraJSON = json.loads(jsondump)
        giostreJSON.append(giostraJSON)

    return jsonify(
        giostre = json.loads(json.dumps(giostreJSON))
    )

@server.route("/checkout", methods=['POST'])
def checkout():
    req_data = request.get_json()
    data = req_data['cliente_data']
    nickname = req_data['cliente_nickname']

    if (DBInterface.isBigliettoDup(nickname, data)):
        return 'Biglietto duplicato', 406


    lista_ospiti = []
    ospitiJSON = []
    for ospite in req_data['cliente_ospiti']:
        lista_ospiti.append(OspiteDAO(ospite['nome'], ospite['eta'], ospite['altezza']))
        data_set = {"nome": ospite['nome'], "eta": ospite['eta'], "altezza": ospite['altezza']}
        jsondump = json.dumps(data_set)
        ospiteJSON = json.loads(jsondump)
        ospitiJSON.append(ospiteJSON)

    biglietto = DBInterface.createBiglietto(data, lista_ospiti, nickname)

    return jsonify(
        codice = biglietto.codice,
        data = biglietto.data,
        ospiti = ospitiJSON
        )

@server.route("/getFasciaOraria", methods=['GET'])
def getFasciaOraria():
    nome_giostra = request.args.get('nome_giostra')
    numero_clienti = DBInterface.readClientiInCoda(nome_giostra)
    giostra = DBInterface.getGiostra(nome_giostra)
    minuti_attesa = math.floor(numero_clienti/(giostra.capienza/giostra.durata))
    ora_inizio = datetime.now()+timedelta(minutes=minuti_attesa)
    ora_fine = ora_inizio+timedelta(minutes=TEMPOFASCIA)
    return jsonify(
        ora_inizio = ora_inizio.strftime("%H:%M"),
        ora_fine = ora_fine.strftime("%H:%M")
    )

@server.route("/getPrenotazioni", methods=['GET'])
def getPrenotazioni():
    nome_cliente = request.args.get('nome_cliente')
    giostre = DBInterface.getPrenotazioni(nome_cliente)
    lista_giostreJSON = []
    lista_clienti_coda = []
    for giostra in giostre:
        data_set = {"nome": giostra.nome_giostra, "fascia_oraria": giostra.fascia_oraria, "numero_ospiti": giostra.numero_ospiti}
        lista_clienti_coda.append(PrenotazioneDAO(giostra.fascia_oraria, giostra.numero_ospiti, giostra.nome_giostra, nome_cliente))
        jsondump = json.dumps(data_set)
        giostraJSON = json.loads(jsondump)
        lista_giostreJSON.append(giostraJSON)

    return jsonify (
        prenotazioni = lista_giostreJSON
    )

@server.route("/getBiglietto", methods=['GET'])
def getBiglietto():
    try:
        nome_cliente = request.args.get("nome_cliente")
        data = datetime.today()
        dataString = datetime.strftime(data, "%d/%m/%Y")
        bigliettoDAO = DBInterface.getBiglietto(nome_cliente, str(dataString))
        ospitiJSON = []
        for ospite in bigliettoDAO.ospiti:
            data_set = {"nome": ospite.nome, "eta": ospite.eta, "altezza": ospite.altezza}
            jsondump = json.dumps(data_set)
            ospiteJSON = json.loads(jsondump)
            ospitiJSON.append(ospiteJSON)

        return jsonify(
            codice = bigliettoDAO.codice,
            data = bigliettoDAO.data,
            ospiti = ospitiJSON
        )
    except:
        return "biglietto not found", 404

@server.route("/registraAccesso", methods=['POST'])
def registraAccesso():
    req_data = request.get_json()
    fasciaOraria = DBInterface.getFasciaOraria(req_data['nome_cliente'], req_data['nome_giostra'])
    fasciaOrariaSplit = fasciaOraria.split('-')
    print(fasciaOraria)
    fasciaOrariaInizioData = datetime.strptime(fasciaOrariaSplit[0], "%H:%M")
    fasciaOrariaFineData = datetime.strptime(fasciaOrariaSplit[1], "%H:%M")
    now = datetime.strptime(datetime.now().time().strftime("%H:%M"), "%H:%M")

    if(fasciaOrariaInizioData.time() <= now.time() and fasciaOrariaFineData.time() >= now.time()):
        DBInterface.eliminaPrenotazione(req_data['nome_cliente'], req_data['nome_giostra'])
        return jsonify(
            status = 200
        )
    return "Fascia oraria non corretta", 412

@server.route("/eliminaPrenotazione", methods=['POST'])
def eliminaPrenotazione():
    try:
        req_data = request.get_json()
        DBInterface.eliminaPrenotazione(req_data['nome_cliente'], req_data['nome_giostra'])
        return jsonify(
            status = 200
        )
    except:
        return "bad request", 400

    
if __name__ == "__main__":
        server.run()
