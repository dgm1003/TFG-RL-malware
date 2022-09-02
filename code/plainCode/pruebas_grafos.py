
import networkx as nx
import matplotlib.pyplot as plt

# función que crea un grafo de n nodos y muestra su representación gráfica
def crea_grafo(n):

    #G = nx.gnp_random_graph(n, 0.1)        ## difícil encontrar un valor de probabilidad bueno que no 
                                             # deje nodos sueltos ni cause demasiadas conexiones
    #G = nx.gnm_random_graph(n, 50)         ## difícil calcular el número apropiado de conexiones
    #G = nx.erdos_renyi_graph(n, 0.15)      ## no suele haber nodos hoja, o quedan nodos sueltos
    #G = nx.binomial_graph(n, 0.2)          ## no hay casi nodos hoja
    #G = nx.random_tree(n)                  ## algo simple pero útil para topologías en árbol, aunque ramas muy largas
    #G = nx.barabasi_albert_graph(n, 1)     ## serviría para árboles, mas hijos que comparten padres
    #G = nx.watts_strogatz_graph(n, 4, 0.1) ## para topologías en anillo igual?
    G = nx.random_internet_as_graph(n)     ## probablemente el más apropiado

    # se probaron muchos otros generadores pero se han dejado solamente aquellos que pudiesen aportar algún valor al trabajo

    # dibujamos el grafo
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G,pos)
    nx.draw_networkx_edges(G,pos)
    nx.draw_networkx_labels(G,pos)
    plt.show()

# llamamos a la función
crea_grafo(30)