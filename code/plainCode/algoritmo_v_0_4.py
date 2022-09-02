import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from grafo_v_0_4 import GrafoRed

# Versión del algoritmo utilizando tablas de recompensa y calidad. 
# Con estructura de clases y recompensa mediante función.
# 
# NUEVO: utiliza clase de grafo separada
#
# Author: Diego García Muñoz

class AgenteMalware():

    # constructor, se le pasarán la red de ordenadores
    # 
    # Parámetros:
    #  - red: red de ordenadores del tipo de objeto GrafoRed
    def __init__(self, red):
        np.set_printoptions(suppress=True)
        self.red = red
        self.NNODOS = self.red.NNODOS
        self.Q = np.matrix(np.zeros([self.NNODOS*2,self.NNODOS*2]))
    

    # Método que entrena al agente rellenando la tabla de calidades
    # 
    # Parámetros:
    #  - alpha: tasa de aprendizaje
    #  - gamma: factor de descuento
    #  - iteraciones: número de iteraciones del entrenamiento
    # Return:
    #  - Q: tabla de calidades
    def entrena_agente(self, alpha, gamma, iteraciones):
        for i in range(iteraciones):
            # obtenemos un nodo al azar (esté infectado o no)
            actual = np.random.randint(0,self.NNODOS*2-1)

            # de las acciones posibles, seleccionamos una al azar
            siguiente = np.random.choice(self.red.get_posibles_acciones(actual))

            # actualizamos el valor de la celda correspondiente con la función de diferencia temporal
            self.Q[actual,siguiente] += alpha * self.red.obtener_recompensa(actual, siguiente) +  gamma * \
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
        # declaramos la posición final de la tabla
        metaReal=self.red.meta+self.NNODOS

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
            puntuacion += self.red.obtener_recompensa(estado_actual,siguiente_estado)
            ruta.append(siguiente_estado)
            # realizamos dicha acción
            estado_actual = siguiente_estado

        return ruta, puntuacion
        


# --- Uso del algoritmo: ---

# guardamos el número de nodos
NNODOS = 30

# declaramos los nodos de inicio y fin
meta = 15
inicio = 17

# creamos la red de ordenadores
#red = GrafoRed(NNODOS, meta, seed=123456)
red = GrafoRed(predefinido=3)
G = red.grafo
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G,pos)
nx.draw_networkx_edges(G,pos)
nx.draw_networkx_labels(G,pos)
plt.show()

# creamos el agente
agente = AgenteMalware(red)


# definimos el factor de descuento y la tasa de aprendizaje respectivamente
gamma = 0.9
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
