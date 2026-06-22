from flask import Flask, render_template, request, jsonify
import osmnx as ox
import networkx as nx
import numpy as np
import random
import math
import time

app = Flask(__name__)
CITY_NAME = "Krasnodar, Russia"
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
    print(f"Ошибка загрузки графа: {e}")
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
            path = nx.shortest_path(
                self.graph,
                start,
                end,
                weight='travel_time'
            )
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
                coordinates.append((
                    self.graph.nodes[node]['y'],
                    self.graph.nodes[node]['x']
                ))
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
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=False,
        port=5000
    )