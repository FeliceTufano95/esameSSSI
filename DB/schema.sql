DROP TABLE IF EXISTS Cliente;
DROP TABLE IF EXISTS Giostra;
DROP TABLE IF EXISTS Biglietto;
DROP TABLE IF EXISTS Ospite;
DROP TABLE IF EXISTS Prenotazione;

PRAGMA foreign_keys = ON;


CREATE TABLE Cliente (
    nickname TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    eta INTEGER NOT NULL,
    altezza REAL NOT NULL
);

CREATE TABLE Giostra (
    nome TEXT PRIMARY KEY,
    capienza INTEGER NOT NULL,
    durata REAL NOT NULL,
    limite_eta INTEGER NOT NULL,
    limite_altezza REAL NOT NULL,
    descrizione TEXT NOT NULL,
    stato_funzionamento INTEGER NOT NULL,
    numero_persone INTEGER NOT NULL
);

CREATE TABLE Biglietto (
    codice INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    Clientenickname NOT NULL,
    FOREIGN KEY(Clientenickname) REFERENCES Cliente(nickname) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Ospite (
    nome TEXT NOT NULL,
    altezza REAL NOT NULL,
    eta INTEGER NOT NULL,
    Bigliettocodice INTEGER NOT NULL,
    PRIMARY KEY(nome, Bigliettocodice),
    FOREIGN KEY(Bigliettocodice) REFERENCES Biglietto(codice) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Prenotazione (
    Clientenickname TEXT NOT NULL,
    Giostranome TEXT NOT NULL,
    fascia_oraria TEXT NOT NULL,
    numero_ospiti INTEGER NOT NULL,
    PRIMARY KEY(Clientenickname, Giostranome),
    FOREIGN KEY(Clientenickname) REFERENCES Cliente(nickname) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(Giostranome) REFERENCES Giostra(nome) ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT INTO Giostra VALUES("Bruco mela",20,1.0,3,1.2,"Una divertentissima giostra per tutti i bambini!",1,50);
INSERT INTO Giostra VALUES("Autoscontro",15,5.0,8,1.4,"Sfreccia come un vero pilota",1,75);
INSERT INTO Giostra VALUES("Tronchi",15,3.0,5,1.5,"Attento agli schizzi e divertiti",1,500);
INSERT INTO Giostra VALUES("Ottovolante",15,3.0,12,1.7,"Una giostra per i più temerari",1,110);
INSERT INTO Giostra VALUES("Trenino",15,1.0,2,1.0,"Esplora il parco sul nostro accogliente trenino",0,0);
INSERT INTO Giostra VALUES("Casa degli orrori",60,20.0,15,1.5,"Sei abbastanza coraggioso per affrontare la casa degli orrori?",1,100);
INSERT INTO Giostra VALUES("Ruota panoramica",40,10.0,8,1.0,"Goditi il panorama da una posizione esclusiva!",0,0);
INSERT INTO Giostra VALUES("Carosello",20,4.0,3,0.75,"Una giostra adatta ai più piccoli",1,50);

-- INSERT INTO Cliente VALUES("Test", "123", "email@email.it", 20, 1.6);
-- INSERT INTO Biglietto(data, Clientenickname) VALUES("13/02/2021","Test");
-- INSERT INTO Ospite VALUES("OspiteTest", 1.5, 15, 1);
-- INSERT INTO Prenotazione Values("Test", "Bruco mela", "15:30-15:45", 1);