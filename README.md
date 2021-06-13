# random_choices

This is similar in functionality to `random.choices` built into the standard Python library, 
with improvements to speed and readability.

## Why this over `random.choices`?

First off, it improves readability over even a simple implementation of `random.choices`. Let's say 
I have four choices, each with the same probability of being picked except the last, which has 
double the relative probability of being picked. This is how one would use `random.choices` to 
accomplish this:

```python
import random

population = ["first choice", "second choice", "third choice", "fourth choice"]
weights = [1.0, 1.0, 1.0, 2.0]

result = random.choices(population=population, weights=weights, k=1)
```

The main problem with this solution is that the weights are not visually represented alongside the 
values to be picked. This decreases readability, and forces the reader to speculate that the indices
of the population members and weights are significant. 

A secondary problem is that if you need to pick again and neither the population nor weights have 
changed, you'll find internally that a lot of unnecessary calculation is done. Namely, the 
accumulation of the weights.

`random_choices` solves both of these problems, allowing the population to be initialized 
visually alongside their weights and caching the calculation-intensive steps so that if 
you have to make another selection when the population or weights have not changed there will 
not be a significant increase in runtime.

## How do I use it?

This is a simple solution to the above problem:

```python
from random_choices import Randomizer, WeightedChoice

population = [
    WeightedChoice("first choice",  1.0),
    WeightedChoice("second choice", 1.0),
    WeightedChoice("third choice",  1.0),
    WeightedChoice("fourth choice", 2.0)
]
randomizer = Randomizer(population)

randomizer.choices(1, replace=True)
```
