import threading
import time
from DB import db
import DBInterface

class ThreadCliente():
    def __init__(self,nome_cliente,nome_giostra,fascia_oraria,tempo):
         t = threading.Thread(target=run, args=(nome_cliente,nome_giostra,fascia_oraria,tempo))
         t.start()

def run(nome_cliente, nome_giostra, fascia_oraria, tempo):
    print('Thread partito')
    time.sleep(tempo.total_seconds())
    if DBInterface.checkPrenotazione(nome_cliente,nome_giostra,fascia_oraria):
        DBInterface.eliminaPrenotazione(nome_cliente,nome_giostra)  
        print('Cliente ed ospiti rimossi dalla coda')

    else:
        print('Prenotazione gia\' rimossa')
