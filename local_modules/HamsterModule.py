from __future__ import annotations
import pygame
import config
import random
from pygame.surface import Surface
from local_modules import BaseModule


class HamsterModule(BaseModule.BaseModule):
    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.the_world = TheWorld()
        self.simulate = True
        self.hamsters = []

        # self.timer_interval = 0.1
        self.generation = 0
        self.round_ticks = 0
        self.setup_simulation()

    def setup_simulation(self):
        for i in range(config.HAMSTER_AMOUNT):
            hamster = Hamster(self.the_world)
            hamster.position = self.the_world.try_spawn(hamster)
            self.hamsters.append(hamster)

    def setup_generation(self):
        self.round_ticks = 0

        survivors = list(map(lambda ham: ham if ham.is_alive() else None, self.hamsters))
        self.hamsters = []

        self.the_world = TheWorld()

        # make babies
        # SUGGESTION: foreach survivor pair with a random other survivor
        for i in range(0, len(survivors), 2):
            hamster = Hamster(self.the_world, survivors[i], survivors[i + 1])
            hamster.position = self.the_world.try_spawn(hamster)
            self.hamsters.append(hamster)

        # fill the lost ones
        for i in range(0, config.HAMSTER_AMOUNT - len(self.hamsters)):
            hamster = Hamster(self.the_world)
            hamster.position = self.the_world.try_spawn(hamster)
            self.hamsters.append(hamster)


    def frame(self):
        if not self.simulate:
            return

        if self.round_ticks >= config.TICKS_PER_GENERATION:
            self.setup_generation()
            self.generation += 1

        self.calculate()

    def calculate(self):
        self.execution_counter += 1
        self.round_ticks += 1
        for hamster in self.hamsters:
            hamster.tick()

    def draw(self):
        for hamster in self.hamsters:
            hamster.draw_representation(self._screen)

    def handle_input(self, event):
        if event.key == pygame.K_p:
            self.simulate = not self.simulate


class TheWorld:
    def __init__(self):
        self.grid = []
        for x in range(config.SCREEN_WIDTH):
            self.grid.append([None] * config.SCREEN_HEIGHT)

        self.available_world_positions = []
        self.generate_available_world_positions()

    def try_spawn(self, occupant):
        new_position = self.get_available_world_position()
        if not self.place_in_world(occupant, new_position):
            raise Exception('THE -BOAT- WORLD IS FULL!', len(self.available_world_positions))
        return new_position

    def get_available_world_position(self):
        #return random.sample(self.available_world_positions, 1)[0]
        return self.available_world_positions.pop(random.randint(0, len(self.available_world_positions)))

    def generate_available_world_positions(self):
        self.available_world_positions = []
        for y in range(config.SCREEN_HEIGHT):
            for x in range(config.SCREEN_WIDTH):
                self.available_world_positions.append((x, y))

    def place_in_world(self, occupant, position: tuple) -> bool:
        if self.grid[position[0]][position[1]] is None:
            self.grid[position[0]][position[1]] = occupant
            return True

        return False

    def try_occupy(self, occupant, old_position: tuple, new_position: tuple) -> (bool, tuple):
        if new_position[0] >= 0 and new_position[0] < len(self.grid) and \
            new_position[1] >= 0 and new_position[1] < len(self.grid[0]):

            if self.grid[new_position[0]][new_position[1]] is None:
                self.grid[new_position[0]][new_position[1]] = occupant
                self.grid[old_position[0]][old_position[1]] = None
                return (True, new_position)

        return (False, old_position)



class Hamster:
    ROTATION_NORTH = (0, -1)
    ROTATION_NORTH_EAST = (1, -1)
    ROTATION_EAST = (1, 0)
    ROTATION_SOUTH_EAST = (1, 1)
    ROTATION_SOUTH = (0, 1)
    ROTATION_SOUTH_WEST = (-1, 1)
    ROTATION_WEST = (-1, 0)
    ROTATION_NORTH_WEST = (-1, -1)

    ROTATION_ALL = (
        ROTATION_NORTH,
        ROTATION_NORTH_EAST,
        ROTATION_EAST,
        ROTATION_SOUTH_EAST,
        ROTATION_SOUTH,
        ROTATION_SOUTH_WEST,
        ROTATION_WEST,
        ROTATION_NORTH_WEST
    )

    def __init__(self, the_world: TheWorld, parent1: Hamster = None, parent2: Hamster = None):
        self.__the_world = the_world
        self.brain = Brain(self)

        self.hp = 100
        self.position = (-1, -1)
        self.genes = []  # type: list[Gene]
        self.color = (0, 0, 0)

        if parent1 is None or parent2 is None:
            self.genes = Hamster.get_random_dna()
        else:
            self.genes = Hamster.get_dna_from_parents(parent1, parent2)

        # rotation
        self.rotation_index = 0

        self.__calculate_color()

    @staticmethod
    def get_random_dna():
        genes = []
        for i in range(config.DNA_LENGTH):
            gene = Gene()
            gene.randomize()
            genes.append(gene)
        return genes

    @staticmethod
    def get_dna_from_parents(parent1: Hamster, parent2: Hamster):
        genes = []
        for i in range(config.DNA_LENGTH):
            genes.append(random.choice((parent1, parent2)).genes[i])
        return genes

    def rotate_left(self):
        self.rotation_index -= 1
        if self.rotation_index < 0:
            self.rotation_index = 7

    def rotate_right(self):
        self.rotation_index += 1
        if self.rotation_index > 7:
            self.rotation_index = 0

    def move_forward(self):
        new_position = (
            self.position[0] + Hamster.ROTATION_ALL[self.rotation_index][0],
            self.position[1] + Hamster.ROTATION_ALL[self.rotation_index][1],
        )

        has_moved, real_position = self.__the_world.try_occupy(self, self.position, new_position)
        if has_moved:
            self.position = real_position

    def draw_representation(self, screen: Surface):
        # pixels are too small when not plain white
        # screen.set_at(self.position, self.color)
        pygame.draw.circle(
            screen,
            self.color,
            self.position,
            2
        )

    def __calculate_color(self):
        # TODO: use gene list values as seed for the rng-random color
        r = 0
        g = 0
        b = 0
        for gene in self.genes:  # type: Gene
            gene_value_counter = 0
            for gene_value in gene.get_gene_list():
                if gene_value_counter == 0:
                    r += gene_value
                elif gene_value_counter == 1:
                    g += gene_value
                elif gene_value_counter == 2:
                    b += gene_value
                    gene_value_counter = -1

                gene_value_counter += 1

        self.color = (int(r % 255), int(g % 255), int(b % 255))

    def is_alive(self):
        return self.hp > 0

    def add_damage(self, damage_amount):
        self.hp -= damage_amount

    def kill(self):
        self.hp = 0

    def tick(self):
        if self.is_alive():
            self.brain.decision()


class Gene:
    SOURCE_TYPE_SENSOR_NEURON = 0
    SOURCE_TYPE_INTERNAL_NEURON = 1
    DEST_TYPE_OUTPUT_ACTION_NEURON = 0
    DEST_TYPE_INTERNAL_NEURON = 1

    DUMMY_SOURCE_NEURON_COUNT = 6
    DUMMY_DEST_NEURON_COUNT = 6

    WEIGHT_MIN = -4.0
    WEIGHT_MAX = 4.0

    def __init__(self):
        self.source_type = Gene.SOURCE_TYPE_SENSOR_NEURON
        self.source_neuron_id = 0
        self.dest_type = Gene.DEST_TYPE_OUTPUT_ACTION_NEURON
        self.dest_neuron_id = 0
        self.weight = 0
        self.gene_cache = ()

    def generate_gene_cache(self):
        self.gene_cache = (self.source_type, self.source_neuron_id, self.dest_type, self.dest_neuron_id, self.weight)

    def get_gene_list(self):
        if not len(self.gene_cache):
            self.generate_gene_cache()
        return self.gene_cache

    def randomize(self):
        self.source_type = random.randint(Gene.SOURCE_TYPE_SENSOR_NEURON, Gene.SOURCE_TYPE_INTERNAL_NEURON)
        self.source_neuron_id = random.randint(0, Gene.DUMMY_SOURCE_NEURON_COUNT)
        self.dest_type = Gene.DEST_TYPE_OUTPUT_ACTION_NEURON
        self.dest_neuron_id = random.randint(0, Gene.DUMMY_DEST_NEURON_COUNT)
        self.weight = random.uniform(Gene.WEIGHT_MIN, Gene.WEIGHT_MAX)


class Brain:
    def __init__(self, hamster: Hamster):
        self.__body = hamster

    def sensor_border_x(self):
        # Width -> 0 .. 1920  | :Width
        # -> 0 .. 1         | - 0.5
        # -> -0.5 .. +0.5   | * 2
        # -> -1 .. +1
        return (float(self.__body.position[0]) / float(config.SCREEN_WIDTH) - 0.5) * 2
        # Alternativ (float(self.__body.position[0]) / (float(config.SCREEN_WIDTH)/2.0) - 1
        # return self.__body.position[0] / config.SCREEN_WIDTH * 100

    def sensor_border_y(self):
        return (float(self.__body.position[1]) / float(config.SCREEN_HEIGHT) - 0.5) * 2
        #return self.__body.position[1] / config.SCREEN_HEIGHT * 100

    def internal_0(self):
        pass

    def internal_1(self):
        pass

    def internal_2(self):
        pass

    def out_rotate_left(self):
        self.__body.rotate_left()

    def out_rotate_right(self):
        self.__body.rotate_right()

    def out_move_forward(self):
        self.__body.move_forward()

    def decision(self):
        if self.__body.rotation_index < 3:
            self.out_rotate_right()
            return

        if self.sensor_border_x() > -0.8:
            self.out_move_forward()
            return
