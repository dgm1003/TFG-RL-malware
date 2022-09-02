import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt

# Versión del algoritmo utilizando tablas de recompensa y calidad. 
# Con estructura de clases y recompensa mediante función.
# 
# NUEVO: grafos aleatorios con NetworkX 
#
# Author: Diego García Muñoz

class AgenteMalware():

    # constructor, se le pasarán las configuraciones sobre la red de ordenadores
    # 
    # Parámetros:
    #  - NNODOS: número total de nodos
    def __init__(self, NNODOS):
        np.set_printoptions(suppress=True)
        self.NNODOS = NNODOS
        self.Q = np.matrix(np.zeros([self.NNODOS*2,self.NNODOS*2]))
    

    # Método para generar una red de ordenadores de forma aleatoria
    # 
    # Parámetros:
    #  - seed: la semilla para la generación aleatoria
    #  - ratio_riesgo: el porcentaje de nodos que se considerarán de alto riesgo
    # Return: el grafo que se ha creado 
    def genera_red(self, seed=None, ratio_riesgo=0.25):
        # generamos el grafo
        self.grafo = nx.random_internet_as_graph(self.NNODOS, seed)

        # seleccionamos al azar un porcentaje de los nodos como nodos de alto riesgo
        dict_riesgos = {}
        for i in range(self.NNODOS):
            if random.random() < ratio_riesgo:
                dict_riesgos[i] = {"riesgo" : 10}
            else:
                dict_riesgos[i] = {"riesgo" : 1}

        nx.set_node_attributes(self.grafo, dict_riesgos)
        # devolvemos el grafo
        return self.grafo
    
    # Método para seleccionar el nodo objetivo 
    # si no se desea su selección de forma aleatoria
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
            if actual >= self.NNODOS:
                return - self.grafo.nodes[actual-self.NNODOS]["riesgo"]
            return - self.grafo.nodes[actual]["riesgo"]

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
                

    # Método que entrena al agente rellenando la tabla de calidades
    # 
    # Parámetros:
    #  - alpha: tasa de aprendizaje
    #  - gamma: factor de descuento
    #  - iteraciones: número de iteraciones del entrenamiento
    # Return:
    #  - Q: tabla de calidades
    def entrena_agente(self, alpha, gamma, iteraciones):
        # --- ENTRENAMIENTO ---
        for i in range(iteraciones):
            # obtenemos un nodo al azar (esté infectado o no)
            actual = np.random.randint(0,self.NNODOS*2-1)

            # de las acciones posibles, seleccionamos una al azar
            siguiente = np.random.choice(self.get_posibles_acciones(actual))

            # actualizamos el valor de la celda correspondiente con la función de diferencia temporal
            self.Q[actual,siguiente] += alpha * self.obtener_recompensa(actual, siguiente) +  gamma * \
                                        self.Q[siguiente, np.argmax(self.Q[siguiente,])] - self.Q[actual,siguiente]

        #normalizamos la tabla Q
        self.Q = self.Q/np.max(self.Q)
        
        return self.Q


    # Método que, una vez entrenado el modelo, encuentra la ruta más corta hasta la meta desde un nodo cualquiera.
    # 
    # Parámetros:
    #  - inicio: nodo de salida
    # Return:
    #  - ruta: lista con los nodos por los que pasa
    #  - puntuacion: recompensa total del camino
    def busca_ruta(self, inicio):
        # --- BÚSQUEDA DE RUTA ---
        # declaramos la posición final de la tabla
        metaReal=self.meta+self.NNODOS

        # inicializamos el vector en el que se guardará la ruta, la puntuación, y 
        # los estados intermedios que usaremos al buscar el camino
        ruta = [inicio]
        estado_actual = inicio
        siguiente_estado = estado_actual
        puntuacion = 0
        # hasta llegar a la meta
        while(estado_actual != metaReal):
            # buscamos la acción con mayor calidad
            siguiente_estado = np.argmax(self.Q[estado_actual,])
            # actualizamos la puntuación y la ruta
            puntuacion += self.obtener_recompensa(estado_actual,siguiente_estado)
            ruta.append(siguiente_estado)
            # realizamos dicha acción
            estado_actual = siguiente_estado

        return ruta, puntuacion
        


# --- Uso del algoritmo: ---

# guardamos el número de nodos
NNODOS = 30

# creamos el agente
agente = AgenteMalware(NNODOS)

# generamos una red con una seed concreta
G = agente.genera_red(123456)
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G,pos)
nx.draw_networkx_edges(G,pos)
nx.draw_networkx_labels(G,pos)
plt.show()


# declaramos los nodos de inicio y fin
meta = 15
inicio = 17

agente.selecciona_meta(meta)


# definimos el factor de descuento y la tasa de aprendizaje respectivamente
gamma = 0.7
alpha = 0.9

# entrenamos el agente
print("Tabla de calidades (normalizada): ")
print(agente.entrena_agente(alpha, gamma, 10000))

# obtenemos la ruta óptima
ruta, puntuacion = agente.busca_ruta(inicio)

print("Ruta:")
print(ruta)
print("Puntuación:")
print(puntuacion)
