from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, Date, select, update, delete
from sqlalchemy.orm import relationship, sessionmaker, Session, mapped_column, declarative_base
from sqlalchemy import create_engine
import os, dotenv, requests, datetime, json, math, subprocess, re, glob
from datetime import datetime

dotenv.load_dotenv()
BDD_URL=os.getenv('DATABASE_URL')
# Connection à la BDD
engine = create_engine(BDD_URL) # , echo=True
# classe de base dont no objets ORM vont dériver
Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'
    id  = Column(Integer, primary_key=True)
    name = Column(String)
    adr = Column(String)
    cat = Column(String)
    # 'factures' permet d'accéder aux factures (1..N) du clients
    factures = relationship("Facture", back_populates="client")

    def __str__(this):
        return f"CLIENT [{this.id}] {this.name} ({this.adr})"

class Facture(Base):
    __tablename__ = 'factures'
    no = Column(String, primary_key=True)
    dt = Column(DateTime)
    cumul = Column(Float)
    total = Column(Float)
    # client_id est la FK
    client_id = Column(Integer, ForeignKey("clients.id"))
    # 'client' permet d'accéder au client lié à la facture
    client = relationship("Client", back_populates="factures")
    commandes = relationship("Commandes", back_populates="facture")
    
    def __str__(self):
        return f"FACTURE [{self.no}] {self.total}€"
    @staticmethod
    def read_file(no):
        '''méthode de classe'''
        with Session(engine) as session:
            query = select(Facture).where(Facture.no==no)
            res = session.execute(query).scalar()
            if not res:
                dico_données ={}
                with open(f"statics/{no}.pngqr.txt", "r") as qrcode:
                    contenu_qrcode = qrcode.read()
                    contenu_qrcode = contenu_qrcode.split("\n")
                    for element in contenu_qrcode:
                        if element.startswith("DATE:"):
                            dico_données["dt"] = datetime.strptime(element.split(":",1)[1], "%Y-%m-%d %H:%M:%S")
                            print("dt",dico_données["dt"])
                        if element.startswith("CUST:"):
                            dico_données["id"] = element.split(":")[1]
                            print("id",dico_données["id"])
                        if element.startswith("CAT:"):
                            dico_données["cat"] = element.split(":")[1]
                            print("cat",dico_données["cat"])
                    print("qrcode",contenu_qrcode)

                with open(f"statics/{no}.png.txt", "r") as facture:
                    contenu_facture = facture.read()
                    contenu_facture=contenu_facture.split("\n")
                    contenu_facture.remove("")
                    liste_produce =[]
                    adress = None
                    cumul_total = 0
                    dico_données["adr"] = None
                    for id,element in enumerate(contenu_facture):
                        if element.startswith("TOTAL"):
                            element_sans_virgule = element.replace(",",".")
                            dico_données["total"] = float(element_sans_virgule.split(" ")[1])
                            print("total",dico_données["total"])
                        if element.startswith("Address") or element.startswith("‘Address"):
                            if adress == None:
                                dico_données["adr"] = element.split(" ",1)[1]+" "+contenu_facture[id+1]
                                print("adr",dico_données["adr"])
                                adress = True
                        if element.startswith("Bill to"):
                            dico_données["name"] = element.split(" ",2)[2]
                            print("name",dico_données["name"])
                        if element.endswith("Euro") and not element.startswith("TOTAL"):
                            print("element",element)
                            element_sans_espace = element.replace(" ","")
                            element_sans_espace = element_sans_espace.replace(",",".")
                            print("el",element_sans_espace)
                            dico_prod = {"name_produit":element.split(".")[0],"qtt":element_sans_espace.split(".")[1][0],"price":float(element.split(" ")[-2].replace(",","."))}
                            if dico_prod["qtt"]=="B":
                                dico_prod["qtt"] = 8
                            if dico_prod["qtt"]=="Z":
                                dico_prod["qtt"] = 2
                            
                            


                            cumul_total+= int(dico_prod["qtt"]) * float(dico_prod["price"])
                            print("dico",dico_prod["name_produit"])
                            liste_produce.append(dico_prod)
                    
                    print(liste_produce)
                    print("facture",contenu_facture)
                client = session.get(Client,dico_données["id"])
                if not client:
                    client=Client(id = dico_données["id"], name = dico_données["name"],adr =dico_données["adr"] ,cat = dico_données["cat"])
                    session.add(client)
                    session.commit()
                fac = Facture(no = no, dt = dico_données["dt"],cumul =cumul_total ,total = dico_données["total"], client = client )
                count_produce = 0
                for produce in liste_produce:
                    count_produce += 1
                    print(produce["name_produit"])
                    prod = session.get(Produits,produce["name_produit"])
                    if not prod:
                        prod = Produits(name = produce["name_produit"], price = produce["price"] )
                        session.add(prod)
                        session.commit()
                    cmd = Commandes(facture = fac, produit = prod, idx = count_produce, qty = produce["qtt"])
                    print(cmd)
                    session.add(cmd)
                    session.commit()
                session.add(fac)
                session.commit()
            return  # facture créee à partir des info des TXT

    
    
class Commandes(Base):
    __tablename__ = 'commandes'
    facture_no = Column(String, ForeignKey("factures.no"),primary_key=True)
    facture = relationship("Facture", back_populates="commandes")
    

    produit_name = Column(String, ForeignKey("produits.name"),primary_key=True)
    produit = relationship("Produits", back_populates="commandes")
    
    idx = Column(Integer,primary_key=True)
    qty = Column(Integer)

    def __str__(self):
        return f"Commandes [{self.produit.name}] {self.qty}"
    

class Produits(Base):
    __tablename__ = 'produits'
    name = Column(String, primary_key=True)
    price = Column(Integer)
    
    commandes = relationship("Commandes", back_populates="produit")

    def __str__(self):
        return f"Produits [{self.name}] {self.price}€"
    

Base.metadata.create_all(bind=engine)
DATABASE_URL = os.getenv("DATABASE_URL")
if __name__=="__main__":
    print('DATABASE_URL=', DATABASE_URL)
    

    with Session(engine) as session:
    

        # fac=Facture(no="FAC_2024_0337-2264460", total=0.0)
        Facture.read_file("FAC_2024_0338-2603475")
        # session.add()
        # session.commit()
    
    #     client = Client(id=1, name="Essai", adr="Ici")
    #     print(client)
    #     session.add(client)
    #     session.commit()
        

    #     query=select(Client).where(Client.id==1)
    #     print(query)
    #     client = session.execute(query).scalar()
    #     print(client)

    #     fac = Facture("FAC_2019_0001-112650")
    #     fac.readfile()
    #     fac.client=client
    #     session.add(fac)
    #     session.commit()


    #     query=select(Client)
    #     clients = session.execute(query).all()
    #     print(clients)
    #     for row in clients:
    #         client=row[0]
    #         print(client, client.factures)