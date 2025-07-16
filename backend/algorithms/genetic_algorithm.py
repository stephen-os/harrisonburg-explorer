import random
from typing import List, Dict, Any, Tuple
from .base import TSPAlgorithm
from models.domain import Place, Route

class GeneticAlgorithm(TSPAlgorithm):
    """Genetic Algorithm for TSP"""
    
    def __init__(self, population_size: int = 100, generations: int = 500, 
                 mutation_rate: float = 0.02, elite_size: int = 20):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
    
    def name(self) -> str:
        return "genetic"
    
    def description(self) -> str:
        return f"Genetic algorithm with population size {self.population_size}, {self.generations} generations"
    
    def solve(self, places: List[Place], distance_matrix: List[List[float]], 
              constraints: Dict[str, Any] = None) -> Route:
        """
        Solve TSP using genetic algorithm.
        
        Algorithm:
        1. Create initial population of random routes
        2. Evaluate fitness of each route
        3. Select best routes for breeding
        4. Create offspring through crossover
        5. Apply mutations
        6. Repeat for specified generations
        """
        if not self.validate_input(places):
            raise ValueError("Need at least 2 places for TSP")
        
        n = len(places)
        start_idx = self._get_start_index(places, constraints)
        return_to_start = self._should_return_to_start(constraints)
        
        # Create initial population
        population = self._create_initial_population(n, start_idx)
        
        # Evolution loop
        for generation in range(self.generations):
            # Calculate fitness for all individuals
            fitness_scores = [self._calculate_fitness(individual, distance_matrix) 
                            for individual in population]
            
            # Create new population
            new_population = []
            
            # Keep elite individuals
            elite_indices = sorted(range(len(fitness_scores)), 
                                 key=lambda i: fitness_scores[i], reverse=True)[:self.elite_size]
            for idx in elite_indices:
                new_population.append(population[idx][:])
            
            # Generate offspring
            while len(new_population) < self.population_size:
                # Tournament selection
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                # Crossover
                child1, child2 = self._order_crossover(parent1, parent2, start_idx)
                
                # Mutation
                if random.random() < self.mutation_rate:
                    child1 = self._mutate(child1, start_idx)
                if random.random() < self.mutation_rate:
                    child2 = self._mutate(child2, start_idx)
                
                new_population.extend([child1, child2])
            
            # Trim to population size
            population = new_population[:self.population_size]
        
        # Get best solution
        final_fitness = [self._calculate_fitness(individual, distance_matrix) 
                        for individual in population]
        best_idx = max(range(len(final_fitness)), key=lambda i: final_fitness[i])
        best_route = population[best_idx]
        
        # Calculate total distance
        total_distance = self._calculate_route_distance(best_route, distance_matrix, return_to_start)
        
        # Add return to start if needed
        if return_to_start and best_route[-1] != start_idx:
            best_route.append(start_idx)
        
        # Convert to place IDs
        places_order = [places[i].id for i in best_route]
        
        return Route(
            places_order=places_order,
            total_distance=total_distance,
            algorithm_used=self.name()
        )
    
    def _create_initial_population(self, n: int, start_idx: int) -> List[List[int]]:
        """Create initial population of random routes"""
        population = []
        cities = list(range(n))
        
        for _ in range(self.population_size):
            # Create random permutation starting with start_idx
            route = cities[:]
            route.remove(start_idx)
            random.shuffle(route)
            route.insert(0, start_idx)
            population.append(route)
        
        return population
    
    def _calculate_fitness(self, route: List[int], distance_matrix: List[List[float]]) -> float:
        """Calculate fitness (1/distance - higher is better)"""
        total_distance = self._calculate_route_distance(route, distance_matrix, return_to_start=True)
        return 1 / (total_distance + 1)  # Add 1 to avoid division by zero
    
    def _calculate_route_distance(self, route: List[int], distance_matrix: List[List[float]], 
                                return_to_start: bool = True) -> float:
        """Calculate total distance for a route"""
        total_distance = 0.0
        
        for i in range(len(route) - 1):
            total_distance += distance_matrix[route[i]][route[i + 1]]
        
        # Add return distance if needed
        if return_to_start and len(route) > 1:
            total_distance += distance_matrix[route[-1]][route[0]]
        
        return total_distance
    
    def _tournament_selection(self, population: List[List[int]], 
                            fitness_scores: List[float], tournament_size: int = 3) -> List[int]:
        """Select parent using tournament selection"""
        tournament_indices = random.sample(range(len(population)), 
                                          min(tournament_size, len(population)))
        best_idx = max(tournament_indices, key=lambda i: fitness_scores[i])
        return population[best_idx][:]
    
    def _order_crossover(self, parent1: List[int], parent2: List[int], 
                        start_idx: int) -> Tuple[List[int], List[int]]:
        """Order crossover (OX) preserving start city"""
        n = len(parent1)
        
        # Remove start city for crossover
        p1_cities = [city for city in parent1 if city != start_idx]
        p2_cities = [city for city in parent2 if city != start_idx]
        
        if len(p1_cities) < 2:
            return parent1[:], parent2[:]
        
        # Random crossover points
        start, end = sorted(random.sample(range(len(p1_cities)), 2))
        
        # Create children
        child1 = [None] * len(p1_cities)
        child2 = [None] * len(p2_cities)
        
        # Copy segments
        child1[start:end] = p1_cities[start:end]
        child2[start:end] = p2_cities[start:end]
        
        # Fill remaining positions
        self._fill_remaining_positions(child1, p2_cities, start, end)
        self._fill_remaining_positions(child2, p1_cities, start, end)
        
        # Add start city back
        return [start_idx] + child1, [start_idx] + child2
    
    def _fill_remaining_positions(self, child: List[int], parent: List[int], 
                                start: int, end: int):
        """Fill remaining positions in crossover"""
        parent_idx = 0
        for i in range(len(child)):
            if child[i] is None:
                while parent[parent_idx] in child:
                    parent_idx += 1
                child[i] = parent[parent_idx]
                parent_idx += 1
    
    def _mutate(self, route: List[int], start_idx: int) -> List[int]:
        """Swap mutation preserving start city"""
        route = route[:]
        cities = [city for city in route if city != start_idx]
        
        if len(cities) >= 2:
            idx1, idx2 = random.sample(range(len(cities)), 2)
            cities[idx1], cities[idx2] = cities[idx2], cities[idx1]
        
        return [start_idx] + cities