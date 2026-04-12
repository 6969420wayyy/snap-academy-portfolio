"""CS 61A presents Ants Vs. SomeBees."""

"""CS 61A presents Ants Vs. SomeBees."""

import random
from ucb import main, interact, trace
from collections import OrderedDict

################
# Core Classes #
################


class Place:
    """A Place holds insects and has an exit to another Place."""
    is_hive = False

    def __init__(self, name, exit=None):
        self.name = name
        self.exit = exit
        self.bees = []
        self.ant = None
        self.entrance = None
        if self.exit is not None:
            self.exit.entrance = self

    def add_insect(self, insect):
        insect.add_to(self)

    def remove_insect(self, insect):
        insect.remove_from(self)

    def __str__(self):
        return self.name


class Insect:
    """An Insect, the base class of Ant and Bee, has health and a Place."""

    next_id = 0
    damage = 0
    is_waterproof = False

    def __init__(self, health, place=None):
        self.health = health
        self.place = place
        self.id = Insect.next_id
        Insect.next_id += 1

    def reduce_health(self, amount):
        """Reduce health by AMOUNT, and remove the insect from its place if it
        has no health remaining.

        >>> test_insect = Insect(5)
        >>> test_insect.reduce_health(2)
        >>> test_insect.health
        3
        """
        self.health -= amount
        if self.health <= 0:
            self.zero_health_callback()
            self.place.remove_insect(self)

    def action(self, gamestate):
        """The action performed each turn."""

    def zero_health_callback(self):
        """Called when health reaches 0 or below."""

    def add_to(self, place):
        self.place = place

    def remove_from(self, place):
        self.place = None

    def __repr__(self):
        cname = type(self).__name__
        return '{0}({1}, {2})'.format(cname, self.health, self.place)


class Ant(Insect):
    """An Ant occupies a place and does work for the colony."""

    implemented = False
    food_cost = 0
    is_container = False
    is_doubled = False

    def __init__(self, health=1):
        super().__init__(health)

    def can_contain(self, other):
        return False

    def store_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def remove_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def add_to(self, place):
        if place.ant is None:
            place.ant = self
        else:
            if self.is_container and self.can_contain(place.ant):
                self.store_ant(place.ant)
                place.ant = self
            elif place.ant.is_container and place.ant.can_contain(self):
                place.ant.store_ant(self)
            else:
                assert place.ant is None, 'Too many ants in {0}'.format(place)
        Insect.add_to(self, place)

    def remove_from(self, place):
        if place.ant is self:
            place.ant = None
        elif place.ant is None:
            assert False, '{0} is not in {1}'.format(self, place)
        else:
            place.ant.remove_ant(self)
        Insect.remove_from(self, place)

    def double(self):
        """Double this ants's damage, if it has not already been doubled."""
        if not self.is_doubled:
            self.damage *= 2
            self.is_doubled = True


class HarvesterAnt(Ant):
    """HarvesterAnt produces 1 additional food per turn for the colony."""

    name = 'Harvester'
    implemented = True
    food_cost = 2

    def action(self, gamestate):
        gamestate.food += 1


class ThrowerAnt(Ant):
    """ThrowerAnt throws a leaf each turn at the nearest Bee in its range."""

    name = 'Thrower'
    implemented = True
    damage = 1
    food_cost = 3
    min_range = 0
    max_range = float('inf')

    def nearest_bee(self):
        place = self.place
        distance = 0
        while not place.is_hive:
            if distance >= self.min_range and distance <= self.max_range:
                bee = random_bee(place.bees)
                if bee:
                    return bee
            place = place.entrance
            distance += 1
        return None

    def throw_at(self, target):
        if target is not None:
            target.reduce_health(self.damage)

    def action(self, gamestate):
        self.throw_at(self.nearest_bee())


def random_bee(bees):
    """Return a random bee from a list of bees, or return None if bees is empty."""
    assert isinstance(bees, list), \
        "random_bee's argument should be a list but was a %s" % type(bees).__name__
    if bees:
        return random.choice(bees)

##############
# Extensions #
##############


class ShortThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at most 3 places away."""

    name = 'Short'
    food_cost = 2
    min_range = 0
    max_range = 3
    implemented = True


class LongThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at least 5 places away."""

    name = 'Long'
    food_cost = 2
    min_range = 5
    max_range = float('inf')
    implemented = True


class FireAnt(Ant):
    """FireAnt cooks any Bee in its Place when it expires."""

    name = 'Fire'
    damage = 3
    food_cost = 5
    implemented = True

    def __init__(self, health=3):
        super().__init__(health)

    def reduce_health(self, amount):
        self.health -= amount
        if self.health <= 0:
            bees = list(self.place.bees)
            for bee in bees:
                bee.reduce_health(self.damage + amount)
            self.zero_health_callback()
            self.place.remove_insect(self)
        else:
            bees = list(self.place.bees)
            for bee in bees:
                bee.reduce_health(amount)


class WallAnt(Ant):
    """WallAnt is an Ant that does nothing each turn, but has large health."""

    name = 'Wall'
    food_cost = 4
    implemented = True

    def __init__(self, health=4):
        super().__init__(health)


class HungryAnt(Ant):
    """HungryAnt will take three turns to digest a Bee in its place."""

    name = 'Hungry'
    food_cost = 4
    chew_duration = 3
    implemented = True

    def __init__(self, health=1):
        super().__init__(health)
        self.chew_countdown = 0

    def action(self, gamestate):
        if self.chew_countdown > 0:
            self.chew_countdown -= 1
        else:
            bee = random_bee(self.place.bees)
            if bee:
                bee.reduce_health(bee.health)
                self.chew_countdown = self.chew_duration


class ContainerAnt(Ant):
    """ContainerAnt can share a space with other ants by containing them."""
    is_container = True

    def __init__(self, health):
        super().__init__(health)
        self.ant_contained = None

    def can_contain(self, other):
        return self.ant_contained is None and not other.is_container

    def store_ant(self, ant):
        self.ant_contained = ant

    def remove_ant(self, ant):
        if self.ant_contained is not ant:
            assert False, "{} does not contain {}".format(self, ant)
        self.ant_contained = None

    def remove_from(self, place):
        if place.ant is self:
            place.ant = place.ant.ant_contained
            Insect.remove_from(self, place)
        else:
            Ant.remove_from(self, place)

    def action(self, gamestate):
        if self.ant_contained is not None:
            self.ant_contained.action(gamestate)


class BodyguardAnt(ContainerAnt):
    """BodyguardAnt provides protection to other Ants."""

    name = 'Bodyguard'
    food_cost = 4
    implemented = True

    def __init__(self, health=2):
        super().__init__(health)


class TankAnt(ContainerAnt):
    """TankAnt provides both protection and damage."""

    name = 'Tank'
    food_cost = 6
    damage = 1
    implemented = True

    def __init__(self, health=2):
        super().__init__(health)

    def action(self, gamestate):
        bees = list(self.place.bees)
        for bee in bees:
            bee.reduce_health(self.damage)
        if self.ant_contained is not None:
            self.ant_contained.action(gamestate)


class Water(Place):
    """Water is a place that can only hold waterproof insects."""

    def add_insect(self, insect):
        super().add_insect(insect)
        if not insect.is_waterproof:
            insect.reduce_health(insect.health)


class ScubaThrower(ThrowerAnt):
    """ScubaThrower is a ThrowerAnt that is waterproof."""

    name = 'Scuba'
    food_cost = 6
    is_waterproof = True
    implemented = True


class QueenAnt(ThrowerAnt):
    """QueenAnt boosts the damage of all ants behind her."""

    name = 'Queen'
    food_cost = 7
    implemented = True
    _queen_exists = False

    def __init__(self, health=1):
        super().__init__(health)
        if QueenAnt._queen_exists:
            self.is_true_queen = False
        else:
            self.is_true_queen = True
            QueenAnt._queen_exists = True

    def action(self, gamestate):
        if not self.is_true_queen:
            return
        ThrowerAnt.action(self, gamestate)
        place = self.place.exit
        while place is not None:
            if place.ant is not None:
                place.ant.double()
                if place.ant.is_container and place.ant.ant_contained is not None:
                    place.ant.ant_contained.double()
            place = place.exit

    def reduce_health(self, amount):
        if not self.is_true_queen:
            Ant.reduce_health(self, amount)
        else:
            self.health -= amount
            if self.health <= 0:
                ants_lose()


################
# Extra Challenge #
################

class SlowThrower(ThrowerAnt):
    """ThrowerAnt that causes Slow on Bees."""

    name = 'Slow'
    food_cost = 6
    implemented = True

    def throw_at(self, target):
        if target is not None:
            target.slow(3)


class ScaryThrower(ThrowerAnt):
    """ThrowerAnt that intimidates Bees, making them back away instead of advancing."""

    name = 'Scary'
    food_cost = 6
    implemented = True

    def throw_at(self, target):
        if target is not None:
            target.scare(2)


class NinjaAnt(Ant):
    """NinjaAnt does not block the path and damages all bees in its place."""

    name = 'Ninja'
    damage = 1
    food_cost = 5
    blocks_path = False
    implemented = True

    def action(self, gamestate):
        for bee in list(self.place.bees):
            bee.reduce_health(self.damage)


class LaserAnt(ThrowerAnt):
    """ThrowerAnt that damages all Insects standing in its path."""

    name = 'Laser'
    food_cost = 10
    implemented = True

    def __init__(self, health=1):
        super().__init__(health)
        self.insects_shot = 0

    def insects_in_front(self):
        insects = {}
        place = self.place.entrance
        distance = 1
        while place is not None and not place.is_hive:
            if place.ant is not None:
                insects[place.ant] = distance
            for bee in place.bees:
                insects[bee] = distance
            place = place.entrance
            distance += 1
        return insects

    def calculate_damage(self, distance):
        damage = 2 - 0.25 * distance - 0.0625 * self.insects_shot
        return max(0, damage)

    def action(self, gamestate):
        insects_and_distances = self.insects_in_front()
        for insect, distance in insects_and_distances.items():
            damage = self.calculate_damage(distance)
            insect.reduce_health(damage)
            if damage:
                self.insects_shot += 1


########
# Bees #
########

class Bee(Insect):
    """A Bee moves from place to place, following exits and stinging ants."""

    name = 'Bee'
    damage = 1
    is_waterproof = True

    def __init__(self, health, place=None):
        super().__init__(health, place)
        self.slow_turns = 0
        self.scared = False
        self.has_been_scared = False

    def sting(self, ant):
        ant.reduce_health(self.damage)

    def move_to(self, place):
        self.place.remove_insect(self)
        place.add_insect(self)

    def blocked(self):
        if self.place.ant is None:
            return False
        if hasattr(self.place.ant, 'blocks_path') and not self.place.ant.blocks_path:
            return False
        return True

    def action(self, gamestate):
        destination = self.place.exit
        if self.slow_turns > 0:
            self.slow_turns -= 1
            if gamestate.time % 2 == 0:
                if self.scared and self.place.entrance is not None and not self.place.entrance.is_hive:
                    self.move_to(self.place.entrance)
                elif not self.blocked() and destination is not None:
                    self.move_to(destination)
            else:
                if self.blocked():
                    self.sting(self.place.ant)
            return
        if self.scared:
            self.scared = False
            if self.place.entrance is not None and not self.place.entrance.is_hive:
                self.move_to(self.place.entrance)
                return
        if self.blocked():
            self.sting(self.place.ant)
        elif self.health > 0 and destination is not None:
            self.move_to(destination)

    def add_to(self, place):
        place.bees.append(self)
        Insect.add_to(self, place)

    def remove_from(self, place):
        place.bees.remove(self)
        Insect.remove_from(self, place)

    def slow(self, length):
        self.slow_turns += length

    def scare(self, length):
        if not self.has_been_scared:
            self.scared = True
            self.has_been_scared = True


class Wasp(Bee):
    """Class of Bee that has higher damage."""
    name = 'Wasp'
    damage = 2


class Boss(Wasp):
    """The leader of the bees. Damage to the boss by any attack is capped."""
    name = 'Boss'
    damage_cap = 8

    def reduce_health(self, amount):
        super().reduce_health(min(amount, self.damage_cap))


class Hive(Place):
    """The Place from which the Bees launch their assault."""
    is_hive = True

    def __init__(self, assault_plan):
        self.name = 'Hive'
        self.assault_plan = assault_plan
        self.bees = []
        for bee in assault_plan.all_bees():
            self.add_insect(bee)
        self.entrance = None
        self.ant = None
        self.exit = None

    def strategy(self, gamestate):
        exits = [p for p in gamestate.places.values() if p.entrance is self]
        for bee in self.assault_plan.get(gamestate.time, []):
            bee.move_to(random.choice(exits))
            gamestate.active_bees.append(bee)

###################
# Game Components #
###################

class GameState:
    """An ant collective that manages global game state and simulates time."""

    def __init__(self, beehive, ant_types, create_places, dimensions, food=2):
        self.time = 0
        self.food = food
        self.beehive = beehive
        self.ant_types = OrderedDict((a.name, a) for a in ant_types)
        self.dimensions = dimensions
        self.active_bees = []
        self.configure(beehive, create_places)

    def configure(self, beehive, create_places):
        self.base = AntHomeBase('Ant Home Base')
        self.places = OrderedDict()
        self.bee_entrances = []

        def register_place(place, is_bee_entrance):
            self.places[place.name] = place
            if is_bee_entrance:
                place.entrance = beehive
                self.bee_entrances.append(place)
        register_place(self.beehive, False)
        create_places(self.base, register_place,
                      self.dimensions[0], self.dimensions[1])

    def ants_take_actions(self):
        for ant in self.ants:
            if ant.health > 0:
                ant.action(self)

    def bees_take_actions(self, num_bees):
        for bee in self.active_bees[:]:
            if bee.health > 0:
                bee.action(self)
            if bee.health <= 0:
                num_bees -= 1
                self.active_bees.remove(bee)
        if num_bees == 0:
            raise AntsWinException()
        return num_bees

    def simulate(self):
        """Simulate an attack on the ant colony."""
        num_bees = len(self.bees)
        try:
            while True:
                self.beehive.strategy(self)
                yield None
                self.ants_take_actions()
                self.time += 1
                yield None
                num_bees = self.bees_take_actions(num_bees)
        except AntsWinException:
            print('All bees are vanquished. You win!')
            yield True
        except AntsLoseException:
            print('The bees reached homebase or the queen ant queen has perished. Please try again :(')
            yield False

    def deploy_ant(self, place_name, ant_type_name):
        ant_type = self.ant_types[ant_type_name]
        if ant_type.food_cost > self.food:
            print('Not enough food remains to place ' + ant_type.__name__)
        else:
            ant = ant_type()
            self.places[place_name].add_insect(ant)
            self.food -= ant.food_cost
            return ant

    def remove_ant(self, place_name):
        place = self.places[place_name]
        if place.ant is not None:
            place.remove_insect(place.ant)

    @property
    def ants(self):
        return [p.ant for p in self.places.values() if p.ant is not None]

    @property
    def bees(self):
        return [b for p in self.places.values() for b in p.bees]

    @property
    def insects(self):
        return self.ants + self.bees

    def __str__(self):
        status = ' (Food: {0}, Time: {1})'.format(self.food, self.time)
        return str([str(i) for i in self.ants + self.bees]) + status


class AntHomeBase(Place):
    """AntHomeBase at the end of the tunnel, where the queen normally resides."""

    def add_insect(self, insect):
        assert isinstance(insect, Bee), 'Cannot add {0} to AntHomeBase'
        raise AntsLoseException()


def ants_win():
    raise AntsWinException()


def ants_lose():
    raise AntsLoseException()


def ant_types():
    all_ant_types = []
    new_types = [Ant]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_ant_types.extend(new_types)
    return [t for t in all_ant_types if t.implemented]


def bee_types():
    all_bee_types = []
    new_types = [Bee]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_bee_types.extend(new_types)
    return all_bee_types


class GameOverException(Exception):
    pass


class AntsWinException(GameOverException):
    pass


class AntsLoseException(GameOverException):
    pass


###########
# Layouts #
###########


def wet_layout(queen, register_place, tunnels=3, length=9, moat_frequency=3):
    for tunnel in range(tunnels):
        exit = queen
        for step in range(length):
            if moat_frequency != 0 and (step + 1) % moat_frequency == 0:
                exit = Water('water_{0}_{1}'.format(tunnel, step), exit)
            else:
                exit = Place('tunnel_{0}_{1}'.format(tunnel, step), exit)
            register_place(exit, step == length - 1)


def dry_layout(queen, register_place, tunnels=3, length=9):
    wet_layout(queen, register_place, tunnels, length, 0)


#################
# Assault Plans #
#################

class AssaultPlan(dict):
    """The Bees' plan of attack for the colony.  Attacks come in timed waves.

    >>> AssaultPlan().add_wave(4, 2)
    {4: [Bee(3, None), Bee(3, None)]}
    """

    def add_wave(self, bee_type, bee_health, time, count):
        bees = [bee_type(bee_health) for _ in range(count)]
        self.setdefault(time, []).extend(bees)
        return self

    def all_bees(self):
        return [bee for wave in self.values() for bee in wave]
