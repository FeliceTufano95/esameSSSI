from DBInterface import checkPrenotazione
import logging
from firebase_admin import messaging
import DBInterface
import threading
import time

class ThreadNotifica ():
    def __init__(self, token_cliente, tempo, nome_giostra, nome_cliente, fascia_oraria):
       t = threading.Thread(target=run, args=(token_cliente, tempo, nome_giostra, nome_cliente, fascia_oraria))
       t.start()

def run(token_cliente, tempo, nome_giostra, nome_cliente, fascia_oraria):
    print('ThreadNotifica: started')
    time.sleep(tempo)

    if(DBInterface.checkPrenotazione(nome_cliente, nome_giostra, fascia_oraria)):
        message = messaging.Message(
            data={
                'titolo': nome_giostra,
                'messaggio': 'Tra 10 minuti potrai salire sulla giostra.',
            },
            token=token_cliente,
        )
        
        response = messaging.send(message)
        
        print('Successfully sent message:', response)
    else:
        print('Prenotazione precedentemente eliminata')


