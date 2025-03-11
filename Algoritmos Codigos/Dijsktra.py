import heapq

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name):
        if name not in self.nodes:
            self.nodes[name] = {}

    def add_edge(self, node1, node2, cost):
        self.add_node(node1)
        self.add_node(node2)
        self.nodes[node1][node2] = cost
        self.nodes[node2][node1] = cost  # Grafo no dirigido

    def dijkstra(self, start, goal):
        pq = [(0, start)]  # Cola de prioridad con (costo, nodo)
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        previous_nodes = {node: None for node in self.nodes}

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node == goal:
                break

            for neighbor, cost in self.nodes[current_node].items():
                distance = current_distance + cost
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        # Reconstrucción del camino
        path, node = [], goal
        while previous_nodes[node] is not None:
            path.append(node)
            node = previous_nodes[node]
        path.append(start)
        path.reverse()
        
        return path, distances[goal]

# 🔹 Ejemplo de mapa del videojuego
game_map = Graph()
game_map.add_edge("Inicio", "Bosque", 2)
game_map.add_edge("Bosque", "Cueva", 3)
game_map.add_edge("Bosque", "Río", 1)
game_map.add_edge("Cueva", "Montaña", 4)
game_map.add_edge("Río", "Montaña", 2)
game_map.add_edge("Montaña", "Final", 1)

# Encontrar el camino más corto
path, cost = game_map.dijkstra("Inicio", "Final")
print(f"Ruta óptima: {path} con un costo total de: {cost}")