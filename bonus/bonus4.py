import random
import threading
import time
import logging

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(threadName)s] - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

botellasSobrantes = 0
latasSobrantes = 0
heladeras = []
monitorBeode = threading.Condition()

cantidadHeladeras = 10
cantidadProveedores = 30


def hayHeladerasDisponibles():
    i = 0
    resultado = False
    while i < len(heladeras):
        h = heladeras[i]
        if h.hayEspacio():
            resultado = True
        i += 1
    return resultado

def hayEspacioParaBotellas():
    i = 0
    resultado = False
    while i < len(heladeras):
        h = heladeras[i]
        if h.hayEspacioParaBotellas():
            resultado = True
        i += 1
    return resultado

def hayEspacioParaLatas():
    i = 0
    resultado = False
    while i < len(heladeras):
        h = heladeras[i]
        if h.hayEspacioParaLatas():
            resultado = True
        i += 1
    return resultado

def elegirHeladera(listaHeladeras=heladeras):
    i = 0
    indiceHeladeraConEspacio = 0
    heladeraMasVacia = listaHeladeras[0]
    while i < len(listaHeladeras):
        heladeraActual = listaHeladeras[i]
        if  heladeraActual.hayEspacio():
            if heladeraActual.cantidadDeCervezas() < heladeraMasVacia.cantidadDeCervezas():
                heladeraMasVacia = heladeraActual
                indiceHeladeraConEspacio = i
        i +=1
    return heladeraMasVacia, indiceHeladeraConEspacio
  

def lataPinchada():
    global heladeras
    indiceRandom = random.randint(0,len(heladeras)-1)
    h = heladeras[indiceRandom]
    if h.hayLatas():
        caso = random.choice([0,1,2,3])
        if caso == 3:
            h.latas.pop(0)
            print("Se ha pinchado una lata en la heladera ", h.nombre, "\n")


        
class Heladera():
    def __init__(self, nombre):
        self.botellas = []
        self.latas = []
        self.nombre = nombre

    def hayEspacio(self):
        return self.hayEspacioParaBotellas() and self.hayEspacioParaLatas()

    def hayEspacioParaBotellas(self):
        if len(self.botellas) == 10:
            return False
        else:
            return True
    
    def hayEspacioParaLatas(self):
        if len(self.latas) == 15:
            return False
        else:
            return True
    
    def hayBotellas(self):
        return len(self.botellas) > 0
    
    def hayLatas(self):
        return len(self.latas) > 0

    def agregarBotella(self, cantidad):
        aPoner = cantidad
        try:
            while aPoner > 0:
                if len(self.botellas) == 10:
                    raise Exception("La heladera se lleno de botellas")
                self.botellas.append(1)
                aPoner -= 1
        except:
            pass
        time.sleep(random.randint(3, 10))

        if aPoner > 0:
            return aPoner
        else:
            return 0
    
    def agregarLata(self, cantidad):
        aPoner = cantidad
        
        try:
            while aPoner > 0:
                if len(self.latas) == 15:
                    raise Exception("La heladera se lleno de latas")
                self.latas.append(1)
                aPoner -= 1
        except:
            pass
        time.sleep(random.randint(3, 10))
        
        if aPoner > 0:
            return aPoner
        else:
            return 0
    
    def estadoActual(self):
        return "La heladera "+ str(self.nombre) +" tiene " + str(len(self.botellas)) + " Botellas y "+ str(len(self.latas)) + " Latas"
    
    def cantidadDeCervezas(self):
        cantidad = len(self.botellas) + len(self.latas)
        return cantidad



class Proveedor(threading.Thread):
    def __init__(self, nombre, monitor):
        super().__init__()
        self.name = nombre
        self.monitor = monitor

    def cantAPoner(self):
        return random.randint(1,10)
                
    def reponer(self, heladera, botellasAPoner, latasAPoner):
        global botellasSobrantes, latasSobrantes

        logging.info("Ingreso " + str(botellasAPoner) + " Botellas y " + str(latasAPoner) + " Latas")
        
        sobranteBotellas = heladera.agregarBotella(botellasAPoner)
        sobranteLatas = heladera.agregarLata(latasAPoner)

        time.sleep(random.randint(3,5))
        logging.info(heladera.estadoActual() + ". Cantidad total de cervezas = " + str(heladera.cantidadDeCervezas()))
        logging.info("Sobraron " + str(sobranteBotellas) + " Botellas y " + str(sobranteLatas) + " latas.\n")

        if sobranteBotellas > 0 or sobranteLatas > 0:
            self.reponerSobrantes(sobranteBotellas, sobranteLatas)

    def reponerSobrantes(self, botellasAPoner, latasAPoner):
        global botellasSobrantes, latasSobrantes, heladeras

        heladerasDisponibles = heladeras.copy()
        sobranteBotellas = botellasAPoner
        sobranteLatas = latasAPoner

        while sobranteBotellas > 0 or sobranteLatas > 0:
            heladera, indice = elegirHeladera(heladerasDisponibles)

            if botellasAPoner > 0:
                if hayEspacioParaBotellas():
                    if heladera.hayEspacioParaBotellas():
                        logging.info("Ingreso " + str(botellasAPoner) + " Botellas sobrantes")
                        sobranteBotellas = heladera.agregarBotella(botellasAPoner)
                    else:
                        logging.info("No hay lugar para botellas en la heladera " + str(heladera.nombre))
                else:
                    botellasSobrantes += sobranteBotellas
                    sobranteBotellas = 0

            if latasAPoner > 0:
                if hayEspacioParaLatas():
                    if heladera.hayEspacioParaLatas():
                        logging.info("Ingreso " + str(latasAPoner) + " Latas sobrantes")
                        sobranteLatas = heladera.agregarLata(latasAPoner)
                    else:
                        logging.info("No hay lugar para latas en la heladera " + str(heladera.nombre))
                else:
                    latasSobrantes += sobranteLatas
                    sobranteLatas = 0
            
            heladerasDisponibles.pop(indice)

            logging.info(heladera.estadoActual() + ". Cantidad total de cervezas = " + str(heladera.cantidadDeCervezas()))
            logging.info("Sobraron " + str(botellasSobrantes) + " Botellas y " + str(latasSobrantes) + " latas.\n")

    def run(self):
        with self.monitor:
            if hayHeladerasDisponibles():
                heladera, indice = elegirHeladera()
                self.reponer(heladera, self.cantAPoner() + botellasSobrantes, self.cantAPoner() + latasSobrantes)
                lataPinchada()
                self.monitor.notify()
            else:
                logging.info("Las heladeras estan llenas!")


class Beode(threading.Thread):
    def __init__(self,monitor, nombre, limite,tipoDeConsumo):
        super().__init__()
        self.name = nombre
        self.limite = limite
        self.consumo = 0
        self.tipoDeConsumo = tipoDeConsumo
        self.monitor = monitor
    
    def elegirHeladera(self):
        h = random.randint(0,len(heladeras)-1)
        return heladeras[h]
    
    def consumirBotella(self, heladera):
        if heladera.hayBotellas():
            heladera.botellas.pop(0)
            self.consumo += 1
            logging.info("Estoy bebiendo "+ self.tipoDeConsumo + " de la heladera " + str(heladera.nombre) + " voy tomando "+ str(self.consumo) + "\n")
        else:
            logging.info("No hay lo que quiero tomar en la heladera " + str(heladera.nombre) + "\n")
            self.monitor.wait()

    
    def consumirLata(self, heladera):
        if heladera.hayLatas():
            heladera.latas.pop(0)
            self.consumo += 1
            logging.info("Estoy bebiendo "+ self.tipoDeConsumo + " de la heladera " + str(heladera.nombre) + " voy tomando "+ str(self.consumo) + "\n")
        else:
            logging.info("No hay lo que quiero tomar en la heladera " + str(heladera.nombre) + "\n")
            self.monitor.wait()

    def consumir(self,heladera):

        if self.tipoDeConsumo.lower() == "botella":
            self.consumirBotella(heladera)
        elif self.tipoDeConsumo.lower() == "lata":
            self.consumirLata(heladera)
        elif self.tipoDeConsumo.lower() == "ambos":
            alAzar = random.choice([0,1])
            if alAzar == 0:
                self.consumirBotella(heladera)
            if alAzar == 1:
                self.consumirLata(heladera)
        time.sleep(random.randint(1, 3))   

    def run(self):
        while self.consumo < self.limite:
            with self.monitor:
                self.consumir(self.elegirHeladera())
        logging.info("Me canse de tomar me voy a dormir")
                
             

            
for i in range(cantidadHeladeras):
    heladeras.append(Heladera(i))

bb = Beode(monitorBeode,"Pepe",5,"botella")  
bb.start()  

bl= Beode(monitorBeode, "Eduardo", 2, "lata")
bl.start()

ba= Beode(monitorBeode,"Barbi", 5, "ambos")
ba.start()

for i in range(cantidadProveedores):
    nombre = 'Proveedor ' + str(i)
    Proveedor(nombre, monitorBeode).start()





