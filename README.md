Energy Hacks for SPAN

Key features:
This simulation creates time dependent cost functions using both physical and psychological parameters such as Newton's law of cooling and Brager's Thermolic Comfort Model to create realistic profiles for an individual household.

In a similar manner, any appliance can be modelled with this framework and immediately implemented into this simulation environment.

These functions are used in an optimization framework (in this case exhaustive search, but in future use, SIMPLEX algorithm, Min-Max search, or alpha-beta pruning will be better suited for large scale optimization of minimizing the cost function) which provides the optimal load management at a given time (1 minute intervals over the course of one day was used, this is flexible).

As exemplified in the code, more complex interactions between user load inputs and SPANs load shifting technology can be immediately incorporated. We use an intelligent general model for personal use, however it is simple to incorporate a living machine learning algorithm to estimate peak times for a person.

One key benefit is that our algorithm aims to maximize convenience even in the event of a usage difference from the expected.
