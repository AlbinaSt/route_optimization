from flask import Flask, render_template, request, jsonify
import osmnx as ox
import networkx as nx
import numpy as np
import random
import math
import time

app = Flask(__name__)
CITY_NAME = "Krasnodar, Russia"
<<<<<<< HEAD
=======
CENTER_COORDS = (45.03547, 38.97529)
>>>>>>> 6306e2a051aa4e5271d135907cbb05bb3657e7fe
print("Загрузка дорожной сети Краснодара")
try:
    G = ox.graph_from_place(
        CITY_NAME,
        network_type='drive',
        simplify=True
    )
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    print(f"Граф загружен: {len(G.nodes)} узлов")
except Exception as e:
<<<<<<< HEAD
    print(f"Ошибка загрузки графа: {e}")
=======
    print(f"Ошибка загрузки: {e}")
>>>>>>> 6306e2a051aa4e5271d135907cbb05bb3657e7fe
    G = nx.Graph()
class RouteOptimizer:
    def __init__(self, graph):
        self.graph = graph
        self.simple_population_size = 40
        self.simple_generations = 60
        self.population_size = 80
        self.generations = 120
        self.crossover_rate = 0.9
        self.mutation_rate = 0.15
        self.time_weight = 0.7
        self.distance_weight = 0.3
        self.path_cache = {}
    def get_nearest_node(self, lat, lon):
        return ox.distance.nearest_nodes(
            self.graph,
            lon,
            lat
        )
    def get_path_between_nodes(self, start, end):
        cache_key = (start, end)
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
        try:
<<<<<<< HEAD
            path = nx.shortest_path(
                self.graph,
                start,
                end,
                weight='travel_time'
            )
=======
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
>>>>>>> 6306e2a051aa4e5271d135907cbb05bb3657e7fe
            total_distance = 0
            total_time = 0
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                edge_data = self.graph.get_edge_data(u, v)
                if edge_data:
                    edge = list(edge_data.values())[0]
                    total_distance += (
                            edge.get('length', 0) / 1000
                    )
                    total_time += (
                            edge.get('travel_time', 0) / 3600
                    )
            result = (
                path,
                total_distance,
                total_time
            )
            self.path_cache[cache_key] = result
            return result
<<<<<<< HEAD
        except Exception:
            return (
                [start, end],
                float('inf'),
                float('inf')
            )
    def evaluate_route(
            self,
            order,
            distance_matrix,
            time_matrix
    ):
        total_distance = 0
        total_time = 0
        for i in range(len(order) - 1):
            a = order[i]
            b = order[i + 1]
            total_distance += distance_matrix[(a, b)]
            total_time += time_matrix[(a, b)]
        return total_distance, total_time
    def weighted_score(self, distance, time_val):
        return (
                self.time_weight * time_val
                +
                self.distance_weight * distance
        )
    def greedy_initial_order(self, n, distance_matrix):
=======
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
>>>>>>> 6306e2a051aa4e5271d135907cbb05bb3657e7fe
        order = [0]
        remaining = set(range(1, n))
        while remaining:
            last = order[-1]
            nearest = min(
                remaining,
                key=lambda x: distance_matrix[(last, x)]
            )
            order.append(nearest)
            remaining.remove(nearest)
        return order
<<<<<<< HEAD
    def create_initial_population(
            self,
            n,
            distance_matrix,
            size
    ):
        population = []
        greedy = self.greedy_initial_order(
            n,
            distance_matrix
        )
        population.append(greedy)
        for i in range(size - 1):
            chromosome = list(range(n))
            random.shuffle(chromosome)
            population.append(chromosome)
        return population
    def ordered_crossover(self, parent1, parent2):
        size = len(parent1)
        start, end = sorted(
            random.sample(range(size), 2)
        )
        child = [-1] * size
        child[start:end + 1] = parent1[start:end + 1]
        pointer = 0
        for gene in parent2:
            if gene not in child:
                while child[pointer] != -1:
                    pointer += 1
                child[pointer] = gene
        return child
    def mutate(self, chromosome):
        mutated = chromosome.copy()
        i, j = random.sample(
            range(len(mutated)),
            2
        )
        mutated[i], mutated[j] = (
            mutated[j],
            mutated[i]
        )
        return mutated
    def simple_genetic_algorithm(
            self,
            nodes,
            distance_matrix,
            time_matrix
    ):
        n = len(nodes)
        raw_population = self.create_initial_population(
            n,
            distance_matrix,
            self.simple_population_size
        )
        population = []
        for chromosome in raw_population:
            dist, time_val = self.evaluate_route(
                chromosome,
                distance_matrix,
                time_matrix
            )
            score = self.weighted_score(
                dist,
                time_val
            )
            population.append({
                'order': chromosome,
                'distance': dist,
                'time': time_val,
                'fitness': score
            })
        best_solution = min(
            population,
            key=lambda x: x['fitness']
        )
        for generation in range(self.simple_generations):
            new_population = []
            elite = min(
                population,
                key=lambda x: x['fitness']
            )
            new_population.append(elite)
            while len(new_population) < self.simple_population_size:
                tournament = random.sample(population, 3)
                parent1 = min(
                    tournament,
                    key=lambda x: x['fitness']
                )
                tournament = random.sample(population, 3)
                parent2 = min(
                    tournament,
                    key=lambda x: x['fitness']
                )
                child_order = parent1['order'].copy()
                if random.random() < 0.8:
                    child_order = self.ordered_crossover(
                        parent1['order'],
                        parent2['order']
                    )
                if random.random() < 0.1:
                    child_order = self.mutate(
                        child_order
                    )
                dist, time_val = self.evaluate_route(
                    child_order,
                    distance_matrix,
                    time_matrix
                )
                score = self.weighted_score(
                    dist,
                    time_val
                )
                child = {
                    'order': child_order,
                    'distance': dist,
                    'time': time_val,
                    'fitness': score
                }
                new_population.append(child)
                if score < best_solution['fitness']:
                    best_solution = child
            population = new_population
        return best_solution
    def dominates(self, a, b):
        return (
                a['time'] <= b['time']
                and
                a['distance'] <= b['distance']
                and
                (
                        a['time'] < b['time']
                        or
                        a['distance'] < b['distance']
                )
        )
    def non_dominated_sort(self, population):
        fronts = [[]]
        for p in population:
            p['dominated_solutions'] = []
            p['domination_count'] = 0
            for q in population:
                if self.dominates(p, q):
                    p['dominated_solutions'].append(q)
                elif self.dominates(q, p):
                    p['domination_count'] += 1
            if p['domination_count'] == 0:
                p['rank'] = 0
                fronts[0].append(p)
        i = 0
        while fronts[i]:
            next_front = []
            for p in fronts[i]:
                for q in p['dominated_solutions']:
                    q['domination_count'] -= 1
                    if q['domination_count'] == 0:
                        q['rank'] = i + 1
                        next_front.append(q)
            i += 1
            fronts.append(next_front)
        fronts.pop()
        return fronts
    def crowding_distance(self, front):
        if not front:
            return
        for p in front:
            p['crowding_distance'] = 0
        objectives = ['distance', 'time']
        for obj in objectives:
            front.sort(key=lambda x: x[obj])
            front[0]['crowding_distance'] = float('inf')
            front[-1]['crowding_distance'] = float('inf')
            obj_min = front[0][obj]
            obj_max = front[-1][obj]
            if obj_max == obj_min:
                continue
            for i in range(1, len(front) - 1):
                prev_val = front[i - 1][obj]
                next_val = front[i + 1][obj]
                front[i]['crowding_distance'] += (
                        (next_val - prev_val)
                        /
                        (obj_max - obj_min)
                )
    def tournament_selection(self, population):
        a = random.choice(population)
        b = random.choice(population)
        if a['rank'] < b['rank']:
            return a
        if b['rank'] < a['rank']:
            return b
        if a['crowding_distance'] > b['crowding_distance']:
            return a
        return b
    def two_opt(
            self,
            order,
            distance_matrix,
            time_matrix
    ):
        best = order.copy()
        best_distance, best_time = self.evaluate_route(
            best,
            distance_matrix,
            time_matrix
        )
        best_score = self.weighted_score(
            best_distance,
            best_time
        )
        improved = True
        while improved:
            improved = False
            for i in range(1, len(best) - 2):
                for j in range(i + 1, len(best)):
                    candidate = (
                            best[:i]
                            +
                            best[i:j][::-1]
                            +
                            best[j:]
                    )
                    dist, time_val = self.evaluate_route(
                        candidate,
                        distance_matrix,
                        time_matrix
                    )
                    score = self.weighted_score(
                        dist,
                        time_val
                    )
                    if score < best_score:
                        best = candidate
                        best_score = score
=======

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
>>>>>>> 6306e2a051aa4e5271d135907cbb05bb3657e7fe
                        improved = True
        return best
    def hybrid_nsga2(
            self,
            nodes,
            distance_matrix,
            time_matrix
    ):
        n = len(nodes)
        raw_population = self.create_initial_population(
            n,
            distance_matrix,
            self.population_size
        )
        population = []
        for chromosome in raw_population:
            dist, time_val = self.evaluate_route(
                chromosome,
                distance_matrix,
                time_matrix
            )
            population.append({
                'order': chromosome,
                'distance': dist,
                'time': time_val
            })
        for generation in range(self.generations):
            fronts = self.non_dominated_sort(
                population
            )
            for front in fronts:
                self.crowding_distance(front)
            offspring = []
            while len(offspring) < self.population_size:
                parent1 = self.tournament_selection(
                    population
                )
                parent2 = self.tournament_selection(
                    population
                )
                child_order = parent1['order'].copy()
                if random.random() < self.crossover_rate:
                    child_order = self.ordered_crossover(
                        parent1['order'],
                        parent2['order']
                    )
                if random.random() < self.mutation_rate:
                    child_order = self.mutate(
                        child_order
                    )
                dist, time_val = self.evaluate_route(
                    child_order,
                    distance_matrix,
                    time_matrix
                )
                offspring.append({
                    'order': child_order,
                    'distance': dist,
                    'time': time_val
                })
            combined = population + offspring
            fronts = self.non_dominated_sort(
                combined
            )
            new_population = []
            for front in fronts:
                self.crowding_distance(front)
                front.sort(
                    key=lambda x: (
                        x['rank'],
                        -x['crowding_distance']
                    )
                )
                if (
                        len(new_population)
                        +
                        len(front)
                        <=
                        self.population_size
                ):
                    new_population.extend(front)
                else:
                    needed = (
                            self.population_size
                            -
                            len(new_population)
                    )
                    front.sort(
                        key=lambda x: x['crowding_distance'],
                        reverse=True
                    )
                    new_population.extend(
                        front[:needed]
                    )
                    break
<<<<<<< HEAD
            population = new_population
        final_fronts = self.non_dominated_sort(
            population
        )
        pareto_front = final_fronts[0]
        for solution in pareto_front:
            improved_order = self.two_opt(
                solution['order'],
                distance_matrix,
                time_matrix
            )
            dist, time_val = self.evaluate_route(
                improved_order,
                distance_matrix,
                time_matrix
            )
            solution['order'] = improved_order
            solution['distance'] = dist
            solution['time'] = time_val
        best_solution = min(
            pareto_front,
            key=lambda s: self.weighted_score(
                s['distance'],
                s['time']
            )
        )
        return best_solution, pareto_front
    def calculate_full_route(self, points):
        if len(points) < 2:
            return None
        nodes = [
            self.get_nearest_node(lat, lon)
            for lat, lon in points
        ]
        distance_matrix = {}
        time_matrix = {}
        print("Предварительный расчёт матриц")
=======
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
>>>>>>> 6306e2a051aa4e5271d135907cbb05bb3657e7fe
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i == j:
                    continue
                _, dist, time_val = self.get_path_between_nodes(
                    nodes[i],
                    nodes[j]
                )
                distance_matrix[(i, j)] = dist
                time_matrix[(i, j)] = time_val
<<<<<<< HEAD
        print("Запуск простого ГА")
        simple_result = self.simple_genetic_algorithm(
            nodes,
            distance_matrix,
            time_matrix
        )
        print("Запуск NSGA-II + 2-opt")
        hybrid_result, pareto_front = self.hybrid_nsga2(
            nodes,
            distance_matrix,
            time_matrix
        )
=======
                time_matrix[(j, i)] = time_val
        print("Запуск простого генетического алгоритма")
        simple_result = self.simple_genetic_algorithm(nodes, distance_matrix, time_matrix)

        print("Запуск гибридного алгоритма NSGA-II + 2-opt")
        hybrid_result = self.hybrid_nsga2_algorithm(nodes, distance_matrix, time_matrix)
>>>>>>> 6306e2a051aa4e5271d135907cbb05bb3657e7fe
        full_path = []
        order = hybrid_result['order']
        for i in range(len(order) - 1):
            a = nodes[order[i]]
            b = nodes[order[i + 1]]
            path, _, _ = self.get_path_between_nodes(
                a,
                b
            )
            if i == 0:
                full_path.extend(path)
            else:
                full_path.extend(path[1:])
        coordinates = []
        for node in full_path:
            if node in self.graph.nodes:
<<<<<<< HEAD
                coordinates.append((
                    self.graph.nodes[node]['y'],
                    self.graph.nodes[node]['x']
                ))
=======
                coords = (self.graph.nodes[node]['y'], self.graph.nodes[node]['x'])
                coordinates.append(coords)
>>>>>>> 6306e2a051aa4e5271d135907cbb05bb3657e7fe
        return {
            'coordinates': coordinates,
            'duration': round(
                hybrid_result['time'],
                2
            ),
            'distance': round(
                hybrid_result['distance'],
                2
            ),
            'simple_ga': {
                'time': round(
                    simple_result['time'],
                    2
                ),
                'distance': round(
                    simple_result['distance'],
                    2
                ),
                'avg_speed': round(
                    simple_result['distance']
                    /
                    simple_result['time'],
                    1
                ) if simple_result['time'] > 0 else 0
            },
            'hybrid': {
                'time': round(
                    hybrid_result['time'],
                    2
                ),
                'distance': round(
                    hybrid_result['distance'],
                    2
                ),
                'avg_speed': round(
                    hybrid_result['distance']
                    /
                    hybrid_result['time'],
                    1
                ) if hybrid_result['time'] > 0 else 0
            },
            'pareto_front': [
                {
                    'time': round(s['time'], 2),
                    'distance': round(s['distance'], 2)
                }
                for s in pareto_front
            ]
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
<<<<<<< HEAD
            return jsonify({
                'error': 'Минимум 2 точки'
            }), 400
        print(
            f"Расчёт маршрута для {len(points)} точек"
        )
        result = optimizer.calculate_full_route(
            points
        )
        elapsed = time.time() - start_time
        print(
            f"Время расчёта: {elapsed:.2f} сек"
        )
        print(
            f"Pareto-front size: "
            f"{len(result['pareto_front'])}"
        )
        return jsonify({
            'success': True,
            'route': result['coordinates'],
            'time': result['duration'],
            'distance': result['distance'],
            'simple_ga': result['simple_ga'],
            'hybrid': result['hybrid'],
            'pareto_front': result['pareto_front']
        })
=======
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
>>>>>>> 6306e2a051aa4e5271d135907cbb05bb3657e7fe
    except Exception as e:
        import traceback
        traceback.print_exc()
<<<<<<< HEAD
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=False,
        port=5000
    )
=======
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
>>>>>>> 6306e2a051aa4e5271d135907cbb05bb3657e7fe
