from flask import Flask, render_template, request, jsonify
import osmnx as ox
import networkx as nx
import numpy as np
import random
import math
import time

app = Flask(__name__)
CITY_NAME = "Krasnodar, Russia"
CENTER_COORDS = (45.03547, 38.97529)
print("Загрузка дорожной сети Краснодара")
try:
    G = ox.graph_from_place(CITY_NAME, network_type='drive', simplify=True)
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    print(f"✓ Граф загружен: {len(G.nodes)} узлов, {len(G.edges)} ребер")
except Exception as e:
    print(f"Ошибка загрузки: {e}")
    G = nx.Graph()
    grid_size = 20
    step = 0.002
    base_lat, base_lon = 45.03547, 38.97529

    for i in range(grid_size):
        for j in range(grid_size):
            node_id = i * grid_size + j
            lat = base_lat + (i - grid_size / 2) * step
            lon = base_lon + (j - grid_size / 2) * step
            G.add_node(node_id, y=lat, x=lon)

    for i in range(grid_size):
        for j in range(grid_size):
            node_id = i * grid_size + j
            if i < grid_size - 1:
                neighbor = (i + 1) * grid_size + j
                dist = step * 111000
                speed = 50
                time_val = dist / 1000 / (speed / 3.6)
                G.add_edge(node_id, neighbor, length=dist, speed_kph=speed, travel_time=time_val)
            if j < grid_size - 1:
                neighbor = i * grid_size + (j + 1)
                dist = step * 111000 * math.cos(math.radians(base_lat + i * step))
                speed = 50
                time_val = dist / 1000 / (speed / 3.6)
                G.add_edge(node_id, neighbor, length=dist, speed_kph=speed, travel_time=time_val)


class RouteOptimizer:
    def __init__(self, graph):
        self.graph = graph
        self.population_size = 20
        self.generations = 15
        self.path_cache = {}

    def get_nearest_node(self, lat: float, lon: float) -> int:
        try:
            return ox.distance.nearest_nodes(self.graph, lon, lat)
        except:
            min_dist = float('inf')
            nearest = None
            for node, data in self.graph.nodes(data=True):
                if 'y' in data and 'x' in data:
                    dist = (lat - data['y']) ** 2 + (lon - data['x']) ** 2
                    if dist < min_dist:
                        min_dist = dist
                        nearest = node
            return nearest if nearest is not None else list(self.graph.nodes())[0]

    def get_path_between_nodes(self, start: int, end: int):
        cache_key = (start, end)
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]

        try:
            def heuristic(u, v):
                if u in self.graph.nodes and v in self.graph.nodes:
                    u_data = self.graph.nodes[u]
                    v_data = self.graph.nodes[v]
                    if 'y' in u_data and 'x' in u_data and 'y' in v_data and 'x' in v_data:
                        lat1, lon1 = u_data['y'], u_data['x']
                        lat2, lon2 = v_data['y'], v_data['x']
                        return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111000
                return 0
            path = nx.astar_path(self.graph, start, end, heuristic=heuristic, weight='length')
            total_distance = 0
            total_time = 0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = self.graph.get_edge_data(u, v)
                if edge_data:
                    edge = list(edge_data.values())[0] if isinstance(edge_data, dict) else edge_data
                    total_distance += edge.get('length', 0) / 1000
                    total_time += edge.get('travel_time', 0) / 3600

            result = (path, total_distance, total_time)
            self.path_cache[cache_key] = result
            return result
        except:
            if start in self.graph.nodes and end in self.graph.nodes:
                dist = self.haversine_distance(
                    (self.graph.nodes[start]['y'], self.graph.nodes[start]['x']),
                    (self.graph.nodes[end]['y'], self.graph.nodes[end]['x'])
                )
                time_val = dist / 40
                return ([start, end], dist, time_val)
            return ([start, end], float('inf'), float('inf'))

    def haversine_distance(self, point1, point2):
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(min(1, a)))
        return 6371 * c

    def simple_genetic_algorithm(self, nodes, distance_matrix, time_matrix):
        n = len(nodes)
        def route_fitness(order):
            total_dist = 0
            total_time = 0
            for k in range(len(order) - 1):
                i, j = order[k], order[k + 1]
                total_dist += distance_matrix.get((i, j), float('inf'))
                total_time += time_matrix.get((i, j), float('inf'))
            return total_dist, total_time, total_dist
        population = []
        for _ in range(self.population_size):
            order = list(range(n))
            random.shuffle(order)
            population.append(order)
        best_solution = None
        best_fitness = float('inf')
        best_time = 0
        best_distance = 0
        for generation in range(self.generations):
            fitnesses = []
            solutions = []
            for order in population:
                dist, time_val, fitness = route_fitness(order)
                fitnesses.append(fitness)
                solutions.append({
                    'order': order,
                    'distance': dist,
                    'time': time_val,
                    'fitness': fitness
                })

                if fitness < best_fitness:
                    best_fitness = fitness
                    best_solution = solutions[-1]
                    best_time = time_val
                    best_distance = dist
            total_fitness = sum(fitnesses)
            if total_fitness > 0:
                probabilities = [f / total_fitness for f in fitnesses]
            else:
                probabilities = [1 / len(fitnesses)] * len(fitnesses)
            new_population = []
            elite_idx = np.argmin(fitnesses)
            new_population.append(population[elite_idx])

            while len(new_population) < self.population_size:
                parent1 = self.roulette_select(population, probabilities)
                parent2 = self.roulette_select(population, probabilities)
                if random.random() < 0.8:
                    child = self.pmx_crossover(parent1, parent2)
                else:
                    child = parent1.copy()
                if random.random() < 0.1:
                    i, j = random.sample(range(n), 2)
                    child[i], child[j] = child[j], child[i]
                new_population.append(child)

            population = new_population

        return best_solution

    def roulette_select(self, population, probabilities):
        r = random.random()
        cumsum = 0
        for i, prob in enumerate(probabilities):
            cumsum += prob
            if r <= cumsum:
                return population[i]
        return population[-1]

    def hybrid_nsga2_algorithm(self, nodes, distance_matrix, time_matrix):
        n = len(nodes)

        def route_fitness(order):
            total_dist = 0
            total_time = 0
            for k in range(len(order) - 1):
                i, j = order[k], order[k + 1]
                total_dist += distance_matrix.get((i, j), float('inf'))
                total_time += time_matrix.get((i, j), float('inf'))
            fitness = total_time * 0.7 + total_dist * 0.3
            return total_dist, total_time, fitness
        population = []
        greedy_order = self.greedy_initial_order(n, distance_matrix)
        population.append(greedy_order)
        population.append(list(range(n)))
        for i in range(self.population_size - 2):
            order = list(range(n))
            random.shuffle(order)
            population.append(order)
        best_solution = None
        best_fitness = float('inf')
        best_time = 0
        best_distance = 0
        for generation in range(self.generations):
            fitnesses = []
            solutions = []
            for order in population:
                dist, time_val, fitness = route_fitness(order)
                fitnesses.append(fitness)
                solutions.append({
                    'order': order,
                    'distance': dist,
                    'time': time_val,
                    'fitness': fitness
                })
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_solution = solutions[-1]
                    best_time = time_val
                    best_distance = dist
            tournament_size = 3
            selected = []
            for i in range(self.population_size):
                candidates = random.sample(list(zip(population, fitnesses)), tournament_size)
                best = min(candidates, key=lambda x: x[1])[0]
                selected.append(best)
            new_population = []
            elite_size = max(1, self.population_size // 5)
            elite_indices = np.argsort(fitnesses)[:elite_size]
            for idx in elite_indices:
                new_population.append(population[idx])
            while len(new_population) < self.population_size:
                parent1 = random.choice(selected)
                parent2 = random.choice(selected)
                child = self.pmx_crossover(parent1, parent2)
                if random.random() < 0.1:
                    i, j = random.sample(range(n), 2)
                    child[i], child[j] = child[j], child[i]
                new_population.append(child)
            population = new_population
        improved_order = self.two_opt_optimization(best_solution['order'], distance_matrix)
        total_dist = 0
        total_time = 0
        for k in range(len(improved_order) - 1):
            i, j = improved_order[k], improved_order[k + 1]
            total_dist += distance_matrix.get((i, j), 0)
            total_time += time_matrix.get((i, j), 0)
        return {
            'order': improved_order,
            'distance': total_dist,
            'time': total_time,
            'fitness': total_time * 0.7 + total_dist * 0.3
        }

    def greedy_initial_order(self, n, distance_matrix):
        if n <= 1:
            return list(range(n))
        order = [0]
        remaining = set(range(1, n))
        while remaining:
            last = order[-1]
            nearest = min(remaining, key=lambda x: distance_matrix.get((last, x), float('inf')))
            order.append(nearest)
            remaining.remove(nearest)
        return order

    def pmx_crossover(self, parent1, parent2):
        size = len(parent1)
        if size < 2:
            return parent1.copy()
        start, end = sorted(random.sample(range(size), 2))
        child = [-1] * size
        child[start:end + 1] = parent1[start:end + 1]
        for i in range(size):
            if child[i] == -1:
                value = parent2[i]
                while value in child:
                    value = parent2[parent1.index(value)]
                child[i] = value
        return child

    def two_opt_optimization(self, order, distance_matrix):
        improved = True
        best_order = order.copy()

        def route_distance(route):
            dist = 0
            for i in range(len(route) - 1):
                dist += distance_matrix.get((route[i], route[i + 1]), 0)
            return dist
        best_distance = route_distance(best_order)
        iterations = 0
        while improved and iterations < 50:
            improved = False
            iterations += 1
            for i in range(1, len(best_order) - 2):
                for j in range(i + 1, len(best_order) - 1):
                    new_order = best_order[:i] + best_order[i:j + 1][::-1] + best_order[j + 1:]
                    new_distance = route_distance(new_order)
                    if new_distance < best_distance - 0.01:
                        best_order = new_order
                        best_distance = new_distance
                        improved = True
                        break
                if improved:
                    break
        return best_order

    def calculate_full_route(self, points):
        if len(points) < 2:
            return None

        nodes = [self.get_nearest_node(lat, lon) for lat, lon in points]
        if len(points) == 2:
            path, distance, time_val = self.get_path_between_nodes(nodes[0], nodes[1])
            coordinates = []
            for node in path:
                if node in self.graph.nodes:
                    coords = (self.graph.nodes[node]['y'], self.graph.nodes[node]['x'])
                    coordinates.append(coords)
            return {
                'duration': round(time_val, 2),
                'distance': round(distance, 2),
                'coordinates': coordinates,
                'simple_ga': {
                    'time': round(time_val, 2),
                    'distance': round(distance, 2)
                },
                'hybrid': {
                    'time': round(time_val, 2),
                    'distance': round(distance, 2)
                }
            }
        print("Предварительный расчет маршрутов")
        distance_matrix = {}
        time_matrix = {}
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                _, dist, time_val = self.get_path_between_nodes(nodes[i], nodes[j])
                distance_matrix[(i, j)] = dist
                distance_matrix[(j, i)] = dist
                time_matrix[(i, j)] = time_val
                time_matrix[(j, i)] = time_val
        print("Запуск простого генетического алгоритма")
        simple_result = self.simple_genetic_algorithm(nodes, distance_matrix, time_matrix)

        print("Запуск гибридного алгоритма NSGA-II + 2-opt")
        hybrid_result = self.hybrid_nsga2_algorithm(nodes, distance_matrix, time_matrix)
        full_path = []
        for k in range(len(hybrid_result['order']) - 1):
            i, j = hybrid_result['order'][k], hybrid_result['order'][k + 1]
            path, _, _ = self.get_path_between_nodes(nodes[i], nodes[j])
            if k == 0:
                full_path.extend(path)
            else:
                full_path.extend(path[1:])
        coordinates = []
        for node in full_path:
            if node in self.graph.nodes:
                coords = (self.graph.nodes[node]['y'], self.graph.nodes[node]['x'])
                coordinates.append(coords)
        return {
            'duration': round(hybrid_result['time'], 2),
            'distance': round(hybrid_result['distance'], 2),
            'coordinates': coordinates,
            'simple_ga': {
                'time': round(simple_result['time'], 2),
                'distance': round(simple_result['distance'], 2),
                'avg_speed': round(simple_result['distance'] / simple_result['time'], 1) if simple_result[
                                                                                                'time'] > 0 else 0
            },
            'hybrid': {
                'time': round(hybrid_result['time'], 2),
                'distance': round(hybrid_result['distance'], 2),
                'avg_speed': round(hybrid_result['distance'] / hybrid_result['time'], 1) if hybrid_result[
                                                                                                'time'] > 0 else 0
            }
        }

optimizer = RouteOptimizer(G)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        start_time = time.time()
        data = request.json
        points = data.get('points', [])
        if len(points) < 2:
            return jsonify({'error': 'Выберите минимум 2 точки'}), 400
        print(f"Расчет маршрута для {len(points)} точек")
        result = optimizer.calculate_full_route(points)
        if result and len(result['coordinates']) > 0:
            elapsed = time.time() - start_time
            print(f"Время расчета: {elapsed:.2f} секунд")
            print(f"Простой ГА: {result['simple_ga']['time']}ч, {result['simple_ga']['distance']}км")
            print(f"Гибридный: {result['hybrid']['time']}ч, {result['hybrid']['distance']}км")
            time_improvement = ((result['simple_ga']['time'] - result['hybrid']['time']) / result['simple_ga'][
                'time']) * 100
            dist_improvement = ((result['simple_ga']['distance'] - result['hybrid']['distance']) / result['simple_ga'][
                'distance']) * 100
            print(f"Улучшение: время на {time_improvement:.1f}%, расстояние на {dist_improvement:.1f}%")
            return jsonify({
                'success': True,
                'route': result['coordinates'],
                'time': result['duration'],
                'distance': result['distance'],
                'avg_speed': round(result['distance'] / result['duration'], 1) if result['duration'] > 0 else 0,
                'simple_ga': result['simple_ga'],
                'hybrid': result['hybrid']
            })
        else:
            return jsonify({'error': 'Не удалось построить маршрут'}), 500
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)