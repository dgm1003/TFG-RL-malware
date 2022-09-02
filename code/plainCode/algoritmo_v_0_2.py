from string import punctuation
import numpy as np
import pylab as plt

# Versión del algoritmo utilizando tablas de recompensa y calidad. Con estructura de clases.
#
# NUEVO: recompensa mediante función
#
# Author: Diego García Muñoz

class AgenteMalware():

    # constructor, se le pasarán las configuraciones sobre la red de ordenadores
    # 
    # Parámetros:
    #  - conexiones: las conexiones entre los nodos
    #  - lista_sin_valor: lista de nodos hoja que no ofrecen información
    #  - lista_alto_riesgo: lista de nodos con seguridad alta
    #  - NNODOS: número total de nodos
    def __init__(self, conexiones, lista_sin_valor, lista_alto_riesgo, NNODOS, meta):
        np.set_printoptions(suppress=True)
        self.conexiones = conexiones
        self.lista_sin_valor = lista_sin_valor
        self.lista_alto_riesgo = lista_alto_riesgo
        self.NNODOS = NNODOS
        self.meta = meta
        
        self.Q = np.matrix(np.zeros([self.NNODOS*2,self.NNODOS*2]))
    

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
        if( (actual, siguiente) in self.conexiones or 
            (siguiente, actual) in self.conexiones or
            (actual-self.NNODOS, siguiente) in self.conexiones):
            # si el destino es de alto riesgo, se penaliza gravemente
            if(siguiente in self.lista_alto_riesgo):
                return -10
            # si el destino aporta poca información, se penaliza ligeramente
            if(siguiente in self.lista_sin_valor):
                return -3
            # en caso contrario, penalización de -1 al haber pasado el tiempo
            return -1

        # si no es ninguno de los casos anteriores, penalización máxima al ser un movimiento imposible.
        return -111


    # Método que obtiene los estados a los que se puede llegar desde el estado actual
    # Ahora mismo es más lento que la versión anterior pero al implementar grafos dejará de serlo. 
    # 
    # Parámetros:
    #  - actual: el estado actual
    # Return:
    #  - acciones: las acciones posibles desde ese estado
    def get_posibles_acciones(self, actual):

        #inicializamos la lista de acciones incluyendo la acción de quedarse en el sitio
        acciones = [actual]

        # variable auxiliar
        actual2 = actual

        # si es un estado no infectado, añadimos la acción de infectarlo
        if actual < self.NNODOS:
            acciones.append(actual+self.NNODOS)
        # si es un estado infectado, obtenemos el número original
        else:
            actual2 = actual - self.NNODOS

        # recorremos todas las conexiones
        for conn in self.conexiones:
            if actual in conn:
                # añadimos los estados a los que está conectado el actual
                if conn[0] == actual2:
                    acciones.append(conn[1])
                else:
                    acciones.append(conn[0])

        return acciones
                

    # Método que entrena al agente rellenando la tabla de calidades
    # 
    # Parámetros:
    #  - alpha: tasa de aprendizaje
    #  - gamma: factor de descuento
    # Return:
    #  - Q: tabla de calidades
    def entrena_agente(self, alpha, gamma):
        # --- ENTRENAMIENTO ---
        for i in range(1000):
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
        



# definición de las conexiones entre dispositivos
# 
#       0
#       |
#       1
#       |
#   ---------
#   |       |
#   2       3
#   |       |
# -----  -------
# |   |  |  |  |
# 4   5  6  7  8
conexiones = [(0,1), (1,2), (1,3), (2,4), (2,5), (3,6), (3,7), (3,8)]

# indicamos los dispositivos que solo están conectados a un único 
# dispositivo y por lo tanto no nos aportan información
lista_sin_valor = [4,8]

# indicamos los dispositivos con alto nivel de seguridad
lista_alto_riesgo = [6]

# guardamos el número de nodos
NNODOS = 9

# definimos el nodo objetivo
meta = 5

# creamos el agente
agente = AgenteMalware(conexiones, lista_sin_valor, lista_alto_riesgo, NNODOS, meta)

# definimos el factor de descuento y la tasa de aprendizaje respectivamente
gamma = 0.7
alpha = 0.9

# entrenamos el agente
print("Tabla de calidades (normalizada): ")
print(agente.entrena_agente(alpha, gamma))

# declaramos el nodo de inicio
inicio = 7

# obtenemos la ruta óptima
ruta, puntuacion = agente.busca_ruta(inicio)

print("Ruta:")
print(ruta)
print("Puntuación:")
print(puntuacion)