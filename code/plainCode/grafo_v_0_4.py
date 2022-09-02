import random

import networkx as nx
import matplotlib.pyplot as plt

# Clase que creará la red de ordenadores mediante NetworkX, y 
# devolverá las acciones posibles y recompensas de cada acción
#
# Author: Diego García Muñoz

class GrafoRed():

    # constructor de la clase, genera una red de ordenadores de forma aleatoria
    # 
    # Parámetros:
    #  - NNODOS: el número de nodos de la red
    #  - meta: el número del nodo objetivo
    #  - seed: la semilla para la generación aleatoria
    #  - ratio_riesgo: el porcentaje de nodos que se considerarán de alto riesgo
    def __init__(self, NNODOS=30, meta=5, seed=None, ratio_riesgo=0.25, predefinido=0):
        # guardamos las variables
        self.NNODOS = NNODOS
        self.meta = meta
        if predefinido > 0 and predefinido < 5:
            self.genera_predefinido(predefinido, ratio_riesgo)
        else:
            # generamos el grafo
            self.grafo = nx.random_internet_as_graph(NNODOS, seed)

            # seleccionamos al azar un porcentaje de los nodos como nodos de alto riesgo
            dict_riesgos = {}
            random.seed(seed)
            for i in range(NNODOS):
                if random.random() < ratio_riesgo:
                    dict_riesgos[i] = {"riesgo" : 10}
                else:
                    dict_riesgos[i] = {"riesgo" : 1}

            nx.set_node_attributes(self.grafo, dict_riesgos)
    
    def genera_predefinido(self, predefinido, ratio_riesgo):
        self.grafo = nx.Graph()

        if predefinido == 1:
            self.NNODOS = 9
            self.meta=5
            conexiones = [(0,1), (1,2), (1,3), (2,4), (2,5), (3,6), (3,7), (3,8)]
            self.grafo.add_edges_from(conexiones)
            lista_riesgo = [6]
            self.define_alto_riesgo(lista_riesgo)
        
        elif predefinido == 2:
            self.meta=15
            self.NNODOS=30
            self.grafo = nx.random_internet_as_graph(self.NNODOS, seed=123456)
            lista_riesgo = [1,4,5,7,8]
            self.define_alto_riesgo(lista_riesgo)
            
        elif predefinido == 3:
            self.meta=15
            self.NNODOS=30
            self.grafo = nx.random_internet_as_graph(self.NNODOS, seed=123456)
            lista_riesgo = [0,1,4,5,8]
            self.define_alto_riesgo(lista_riesgo)
            
        elif predefinido == 4:
            self.meta=65
            self.NNODOS=100
            self.grafo = nx.random_internet_as_graph(self.NNODOS, seed=12345678)
            # seleccionamos al azar un porcentaje de los nodos como nodos de alto riesgo
            dict_riesgos = {}
            random.seed(12345678)
            for i in range(self.NNODOS):
                if random.random() < ratio_riesgo:
                    dict_riesgos[i] = {"riesgo" : 10}
                else:
                    dict_riesgos[i] = {"riesgo" : 1}

            nx.set_node_attributes(self.grafo, dict_riesgos)


    # Método para regenerar la red
    # 
    # Parámetros:
    #  - NNODOS: el número de nodos de la red
    #  - meta: el número del nodo objetivo
    #  - seed: la semilla para la generación aleatoria
    #  - ratio_riesgo: el porcentaje de nodos que se considerarán de alto riesgo
    # Return: el grafo que se ha creado 
    def regenera_red(self, NNODOS, meta, seed=None, ratio_riesgo=0.25):
        # guardamos las variables
        self.NNODOS = NNODOS
        self.meta = meta
        # generamos el grafo
        self.grafo = nx.random_internet_as_graph(NNODOS, seed)

        # seleccionamos al azar un porcentaje de los nodos como nodos de alto riesgo
        dict_riesgos = {}
        for i in range(NNODOS):
            if random.random() < ratio_riesgo:
                dict_riesgos[i] = {"riesgo" : 10}
            else:
                dict_riesgos[i] = {"riesgo" : 1}

        nx.set_node_attributes(self.grafo, dict_riesgos)
        # devolvemos el grafo
        return self.grafo
    
    # Método para seleccionar el nodo objetivo
    # 
    # Parámetros:
    #  - meta: el número del nodo objetivo
    def selecciona_meta(self, meta):
        self.meta = meta
    
    # Método para redefinir la lista de nodos de alto riesgo 
    # si no se desea su selección de forma aleatoria
    # 
    # Parámetros:
    #  - lista_alto_riesgo: la lista con los nuevos nodos de alto riesgo
    def define_alto_riesgo(self, lista_alto_riesgo):
        
        # Reiniciamos los riesgos de los nodos
        for i in range(self.NNODOS):
            self.grafo.nodes[i]["riesgo"] = 1

        # Asignamos los nuevos riesgos
        for i in lista_alto_riesgo:
            self.grafo.nodes[i]["riesgo"] = 10


    # Método que obtiene la recompensa de una acción
    # 
    # Parámetros:
    #  - actual: estado actual
    #  - siguiente: estado siguiente o acción a realizar
    # Return: la recompensa de dicha acción partiendo de dicho estado
    def obtener_recompensa(self, actual, siguiente):

        # si se está infectando al nodo actual
        if(siguiente == actual + self.NNODOS):
            # si el nodo actual es el objetivo, devuelve la máxima recompensa
            if(actual == self.meta):
                return 999
            # en caso contrario, penaliza la acción
            return -5

        # si se mantiene en el estado actual
        if(actual == siguiente):
            # si está en el estado objetivo, devuelve la máxima recompensa
            if(actual == self.meta + self.NNODOS):
                return 999
            # en caso contrario, penalización de -1 al haber pasado el tiempo
            return -1
        
        # si se mueve por una conexión válida
        if( self.grafo.has_edge(actual, siguiente) or
            self.grafo.has_edge(actual-self.NNODOS, siguiente) ):
            # si el destino aporta poca información, se penaliza ligeramente
            if(self.grafo.degree(siguiente)==1):
                return -3
            # en caso contrario, devolvemos el riesgo del nodo (el riesgo mínimo 
            # será 1, equivalente a la penalización por tiempo)
            return - self.grafo.nodes[siguiente]["riesgo"]

        # si no es ninguno de los casos anteriores, penalización máxima al ser un movimiento imposible.
        return -111


    # Método que obtiene los estados a los que se puede llegar desde el estado actual
    # 
    # Parámetros:
    #  - actual: el estado actual
    # Return:
    #  - acciones: las acciones posibles desde ese estado
    def get_posibles_acciones(self, actual):

        if actual < self.NNODOS:
            #inicializamos la lista de acciones con los nodos conectados al actual
            acciones = [a for a in self.grafo[actual]]
            # si es un estado no infectado, añadimos la acción de infectarlo
            acciones.append(actual+self.NNODOS)
        else:
            #inicializamos la lista de acciones con los nodos conectados al actual
            acciones = [a for a in self.grafo[actual-self.NNODOS]]
        return acciones
                
