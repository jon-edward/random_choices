from dataclasses import dataclass
from typing import Any, List, Optional, Callable
from bisect import bisect
from random import random
from itertools import accumulate, repeat
from functools import cached_property
from math import floor
from copy import deepcopy


@dataclass
class WeightedChoice:
    """Defines a choice that will be picked by its return_value, with a relative weighting of 'weight'."""
    return_value: Any
    weight: float

    def __post_init__(self):
        assert self.weight > 0.0, "Weight should be greater than 0.0"


class UniformChoice(WeightedChoice):
    def __init__(self, return_value: Any):
        """Defines a WeightedChoice that has a weight of 1."""
        self.return_value: Any = return_value
        self.weight: float = 1


class Randomizer:
    def __init__(self,
                 population: Optional[List[WeightedChoice]] = None,
                 rng: Callable[..., float] = random):
        """
        Selects choices from a list based on their relative weights.

        :param population: Initializes the population.
        :param rng: A function that generates a random number in the range [0, 1).
        """
        if population is None:
            self._population: List[WeightedChoice] = []
        else:
            self._population = []
            self.population = population
        self.rng = rng

    @property
    def population(self) -> List[WeightedChoice]:
        """List of WeightedChoices that Randomizer uses for picking."""
        return self._population

    @population.setter
    def population(self, other: List[WeightedChoice]):
        self._delete_cached_properties()
        self._population = other

    @cached_property
    def weights(self) -> List[float]:
        """Index-corresponding list of weights for population."""
        return [choice.weight for choice in self.population]

    @cached_property
    def return_values(self) -> List[Any]:
        """Index-corresponding list of return_values for population."""
        return [choice.return_value for choice in self.population]

    @cached_property
    def is_uniform(self) -> bool:
        """Defines if all choices are of the same weight."""
        if not self.weights or len(self.weights) < 2:
            return True
        else:
            first_elem = self.weights[0]
            return all([e == first_elem for e in self.weights[1:]])

    @cached_property
    def cumulative_weights(self) -> List[float]:
        """Index-corresponding accumulated weights for population."""
        return list(accumulate(self.weights))

    @cached_property
    def total_weight(self) -> float:
        """The total weight for population."""
        return float(sum(self.weights))

    @property
    def is_empty(self) -> bool:
        """Specifies whether or not there are choices left."""
        return self.total_weight <= 0.0

    @cached_property
    def normalized_weights(self) -> List[float]:
        """The normalized weights for population, such that they all sum up to 1.0"""
        return list(map(lambda x: x / self.total_weight, self.weights))

    @cached_property
    def normalized_cumulative_weights(self) -> List[float]:
        """Index-corresponding accumulated normal weights for population."""
        return list(accumulate(self.normalized_weights))

    def _delete_cached_properties(self):
        """
        This forces cached properties to be recalculated when called. This should
        be done when dependent attributes are changed, like 'self.population'.
        """
        props = [p for p in self.__class__.__dict__ if not p.startswith("__")]
        for prop in props:
            if isinstance(self.__class__.__dict__[prop], cached_property):
                try:
                    del self.__dict__[prop]
                except KeyError:
                    """Property has not yet been set."""
                    pass

    def pick_with_replacement(self, k: int) -> List[Any]:
        """
        Picks choices in self.population based on their weighting. Replaces after each pick.

        :param k: Number of iterations for picking. This is the maximum length of the returned list.
        :return: The return_values of the choices picked.
        """
        if self.is_empty:
            return []

        if self.is_uniform:
            return [
                self.return_values[floor(self.rng() * len(self.population))] for _ in repeat(None, k)
            ]
        else:
            return [
                self.return_values[
                    bisect(self.normalized_cumulative_weights, self.rng(), 0, len(self.population) - 1)
                ]
                for _ in repeat(None, k)
            ]

    def pick_without_replacement(self, k: int, replenish: bool = True) -> List[Any]:
        """
        Picks choices in self.population based on their weighting. Does not replace after each pick.

        :param k: Number of iterations for picking. This is the maximum length of the returned list.
        :param replenish: Whether or not the picked choices should be replenished to the stored choices.
        :return: The return_values of the choices picked.
        """
        if self.is_empty:
            return []

        choices = deepcopy(self.population)

        def weights() -> List[float]:
            return [c.weight for c in choices]

        results = []

        for _ in repeat(None, k):
            w = weights()
            t_w = sum(w)
            if t_w <= 0.0:
                break
            pick_random = t_w * self.rng()
            choices_i = -1
            while pick_random > 0.0:
                choices_i += 1
                pick_random -= w[choices_i]
            results += [choices[choices_i].return_value]
            del choices[choices_i]

        if not replenish:
            self.population = choices

        return results
