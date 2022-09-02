import numpy as np
import pylab as plt

# Versión inicial del algoritmo, utilizando tablas de recompensa y calidad y sin estructura de clases
#
# Author: Diego García Muñoz


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

# creamos una matriz de recompensas con el doble del número de nodos como 
# dimensiones (cada nodo podrá estar sin infectar o infectado)
R = np.matrix(np.ones(shape=(NNODOS*2, NNODOS*2)))
R *= -111

# definimos el nodo objetivo
meta = 5

# recorremos la lista de conexiones
for conex in conexiones:
    # damos recompensa -1 al camino entre 2 nodos, simulando la penalización por cada unidad de tiempo
    R[conex] = -1
    R[conex[::-1]] = -1
    # también damos esa recompensa si el nodo inicio está infectado y viaja a otro no infectado
    R[conex[0]+NNODOS,conex[1]] = -1
    R[conex[1]+NNODOS,conex[0]] = -1

# definimos la recompensa de infectar un nodo no objetivo
for i in range(NNODOS):
    R[i, i+NNODOS] = -5

# actualizamos las recompensas de visitar nodos con poca información
for nodo in lista_sin_valor:
    for i in range(NNODOS*2):
        if R[i,nodo] == -1:
            R[i,nodo] = -3
            
# actualizamos las recompensas de visitar nodos con mucho riesgo
for nodo in lista_alto_riesgo:
    for i in range(NNODOS):
        if R[i,nodo] == -1:
            R[i,nodo] = -10

# definimos la recompensa por infectar el nodo objetivo
R[meta, meta+NNODOS] = 999

# por último, definimos la recompensa para quedarse en un nodo cualquiera
for i in range(NNODOS*2):
    R[i, i] = -1
R[meta+NNODOS,meta+NNODOS]= 999

print("Tabla de recompensas")
print(R)

# creamos la matriz de calidad
Q = np.matrix(np.zeros([NNODOS*2,NNODOS*2]))

# definimos el factor de descuento y la tasa de aprendizaje respectivamente
gamma = 0.7
alpha = 0.9

# --- ENTRENAMIENTO ---

for i in range(1000):
    # obtenemos un nodo al azar (esté infectado o no)
    actual = np.random.randint(0,NNODOS*2-1)

    # obtenemos las acciones que tiene permitido tomar (aquellas con recompensa mayor que -111)
    posibles_acciones = []
    for j in range(NNODOS*2):
        if R[actual,j] > -100:
            posibles_acciones.append(j)
    # de las acciones posibles, seleccionamos una al azar
    siguiente = np.random.choice(posibles_acciones)

    # actualizamos el valor de la celda correspondiente con la función de diferencia temporal
    Q[actual,siguiente] += alpha * R[actual,siguiente] + gamma * Q[siguiente, np.argmax(Q[siguiente,])] - Q[actual,siguiente]

#normalizamos la tabla Q
Q = Q/np.max(Q)

print("Tabla de calidades (normalizada)")
print(Q)


# --- BÚSQUEDA DE RUTA ---

# declaramos el nodo de inicio
inicio = 7
# declaramos la posición final de la tabla
metaReal=meta+NNODOS

# inicializamos el vector en el que se guardará la ruta, la puntuación, y 
# los estados intermedios que usaremos al buscar el camino
ruta = [inicio]
estado_actual = inicio
siguiente_estado = estado_actual
puntuacion = 0
# hasta llegar a la meta
while(estado_actual != metaReal):
    # buscamos la acción con mayor calidad
    siguiente_estado = np.argmax(Q[estado_actual,])
    # actualizamos la puntuación y la ruta
    puntuacion += R[estado_actual,siguiente_estado]
    ruta.append(siguiente_estado)
    # realizamos dicha acción
    estado_actual = siguiente_estado


print("Ruta:")
print(ruta)
print("Puntuación:")
print(puntuacion)
