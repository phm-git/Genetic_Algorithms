import time
import random
import string
import numpy as np
import pandas as pd
import Levenshtein



class candidate:
    
    def __init__(self, length):
        self.length = length
        self.generate()
        self.fitness = 0

    def generate(self):
        self.genome = "".join(random.choice(string.ascii_letters + ' .,') for i in range(self.length))

    def reproduce(self, partner, rate, cross_points):

        x_points = random.choices(range(self.length), k=cross_points)
        x_points.sort()
        parents = [self, partner]
        offspring = candidate(self.length)
        p_choice = random.randint(0,1)

        for i, v, in enumerate(x_points):
            
            p_choice = abs(p_choice - 1)          
            last = 0
            offspring.genome = parents[p_choice].genome[last:v] + parents[abs(p_choice - 1)].genome[v:]
            
            last = v

        offspring.mutate(rate)
        return offspring
    
    def mutate(self, rate):
        for i, v in enumerate(self.genome):
            
            if np.random.rand() < rate:
                self.genome = self.genome[:i] + "".join(random.choice(string.ascii_letters + ' .,')) + self.genome[i+1:]

    
    def update_fitness(self, target):

        self.fitness = 0
        for i, v in enumerate(self.genome):
            self.fitness += 1 if self.genome[i] == target[i] else 0
        
        self.fitness = self.fitness / self.length


class population:
    
    def __init__(self, size, target):
        self.pop_size = size
        self.population = [candidate(len(target)) for x in range(size)]
        self.gen_log = []

        self.update_fitness(target, 0)
        self.pop_sort()

        self.lev_dist = Levenshtein.distance(self.population[0].genome, self.population[-1].genome)
        self.lev_ratio = Levenshtein.ratio(self.population[0].genome, self.population[-1].genome)

        self.gen_log_headers = ['generation', 'lev_dist', 'lev_ratio', 'best_fitness', 'best_genome']
        
    def update_fitness(self, target, generation):
        for genome in self.population:
            genome.update_fitness(target)
        
        self.pop_sort()

        self.lev_dist = Levenshtein.distance(self.population[0].genome, self.population[-1].genome)
        self.lev_ratio = Levenshtein.ratio(self.population[0].genome, self.population[-1].genome)

        self.gen_log.append([generation, self.lev_dist, self.lev_ratio, self.population[0].fitness, self.population[0].genome])
    
    def pop_sort(self):
        self.population.sort(key = lambda x: x.fitness, reverse = True)
    
    def breed_next_generation(self, fittness_cutoff, mutation_rate, cross_points):
        fittest = self.population[:fittness_cutoff]
        weights = [x.fitness for x in fittest]
        new_population = []

        for i in range(self.pop_size):
            
            parents = random.choices(fittest, weights=weights, k=2)
            new_population.append(parents[0].reproduce(parents[1], mutation_rate, cross_points))
        
        self.population = [ x for x in new_population]
        


def main():
    start = time.perf_counter()
    population_size = 2000
    mutation_rate = 0.01
    success = False
    fittness_cuttoff = int(population_size * 0.1)
    x_points = 1
    generation = 1

    target = 'People tell you the world looks a certain way. Parents tell you how to think. Schools tell you how to think. TV. Religion. And then at a certain point, if youre lucky, you realize you can make up your own mind. Nobody sets the rules but you. You can design your own life.'
    #target = 'How much wood would a woodchuck chuck if a woodchuck could chuck wood'

    print('Target: {}'.format(target))

    pop = population(population_size, target)

    while (success != True):
        print('---Generation {}---'.format(generation))

        pop.update_fitness(target, generation)

        if pop.population[0].fitness == 1:
            success = True
            end = time.perf_counter()
            delta = end - start
            print('Success!')
            print('--------------')
            print('Time elapsed (s): {}'.format(delta))
            print('Best genome: {}'.format(pop.population[0].genome))
            print('Least fit genome: {}'.format(pop.population[-1].genome))
            print('Lowest fitness: {}'.format(pop.population[-1].fitness))
            print('Levenshtein Distance: {}'.format(pop.lev_dist))
            print('Levenshtein Ratio: {}'.format(pop.lev_ratio))

            df = pd.DataFrame(pop.gen_log, columns=pop.gen_log_headers)
            print(df)
            df.to_csv('log_{}.csv'.format(time.time()), index=False)
            #df.plot(x = 'generation', y = ['lev_dist', 'lev_ratio', 'best_fitness'])


            

        
        print('Best genome: {}'.format(pop.population[0].genome))
        print("Best fitnes: {}".format(pop.population[0].fitness))

        pop.breed_next_generation(fittness_cuttoff, mutation_rate, x_points)
        print ('Next generation size: {}'.format(len(pop.population)))
        generation += 1


if __name__ == '__main__':
    main()