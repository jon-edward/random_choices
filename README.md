# random_choices

This is similar in functionality to `random.choices` built into the standard Python library.

## Why this over `random.choices`?

First off, it improves readability over even a simple implementation of `random.choices`. Let's say 
I have four choices, each with the same probability of being picked except the last, which has 
double the relative probability of being picked. This is how one would use `random.choices`:

```python
import random

population = ["first choice", "second choice", "third choice", "fourth choice"]
weights = [1.0, 1.0, 1.0, 2.0]

random.choices(population=population, weights=weights)
```