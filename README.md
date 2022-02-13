# facility_location
Facility Location discrete optimization solvers, based on ortools lib.


Optimizes the total cost of opening, maintaining facilities and shipping to customers:
Each customer is assigned to exactly one facility.
The cost of shipping is the euclidian distance between the facility location and customer location.
If a facility is active (serve customers), its opening and maintaining cost is 'setup_cost'
Each facility can only handle a certain amount of customer demands (capacity).

-----------------------------------------------------------------------------------------------------------

The solver takes two primary inputs:
 - facilities: list of struct Facility
 - customers: list of struct Customer

Where the structs are defined as follows:

Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

(the types are:
 - 'index' -> int
 - 'setup_cost' -> float
 - 'capacity' -> float
 - 'demand' -> float
 - 'location' -> Point

(the struct Point is defined as: Point = namedtuple("Point", ['x', 'y']), where 'x', 'y' are floats)

-----------------------------------------------------------------------------------------------------------

The output 'solution' is a list of size equal to the number of customers.
Each item maps the index customer to the index of facility.
Example:  solution[3] == 1 means the customer N°3 is assigned to the facility N°1. (we can by the way deduce that the facility N°1 is active)
