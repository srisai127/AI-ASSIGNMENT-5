# AI-ASSIGNMENT-5

A structured compilation of foundational Artificial Intelligence and Knowledge Engineering frameworks implemented in Python, ranging from game tree optimization to structured knowledge graphs and probabilistic causal networks.

---

## Repository Directory & Project Index

### 1. Game Tree Search Algorithms (`q1_search_algorithms.py`)

* **Domain:** Adversarial state-space exploration implemented within an interactive 3x3 Tic-Tac-Toe grid environment.


* **Core Mechanisms:** Combinatorial game-playing calculations and terminal state assessments.


* **Implemented Agents:**
* **Classic Minimax:** Exhaustive tree exploration tracking exact game utility states with a time complexity of $O(b^m)$.


* **Alpha-Beta Pruning:** Optimized minimax execution that removes irrelevant search branches using dynamic alpha and beta bounds.


* **Heuristic Alpha-Beta:** Depth-limited search variance applying a custom line-occupancy score calculation when specified depth limits are reached.


* **Monte-Carlo Tree Search (MCTS):** Simulation-driven decision engine executing Selection, Expansion, Simulation, and Back-propagation phases across iterative win-and-visit configurations.





### 2. AI-Based Travel Planner (`q2_travel_planner.py`)

* **Domain:** Custom itinerary planning based on multi-city constraint tracking.


* **Core Mechanisms:** Native Python dictionary structures acting as programmatic knowledge bases to simulate semantic ontology endpoints.


* **Knowledge Store Elements:**
* `TOURIST_PLACES_KB`: Maps destination points across Goa, Hyderabad, Manali, Jaipur, and Kerala, storing category markers, safety or interest ratings, and entry fee listings.


* `FOOD_KB`: Database mapping regional culinary offerings, cuisine categorizations, dietary profiles (vegetarian and non-vegetarian flags), and average cost valuations.


* `WINE_KB`: Specialized beverage curation system pairing explicit drink types (such as Sauvignon Blanc, Kullu Apple Wine, or Lassi) against specified cuisine structures.


* `HOTEL_KB` & `TRANSPORT_KB`: Tiered constraint indexes dividing local transit models and hotel options into explicit budget, mid-range, and luxury segments.





### 3. Knowledge Graphs & Semantic Networks (`q3_knowledge_graphs.py`)

* **Domain:** Formalized tourism and heritage relational semantic networks.


* **Core Mechanisms:** Standard W3C graph construction, triple schema alignment, and programmatic data serialization.


* **Key Framework Components:**
* **RDFLib Engine:** Core manager handling namespace definitions, prefix binding, and explicit triple assertions via `URIRef` and `Literal` formatting.


* **Ontology Structure:** Explicit class hierarchies (e.g., `Beach` $\sqsubseteq$ `NaturalSite` $\sqsubseteq$ `TouristPlace`) establishing class properties and directional subclass inheritance relationships.


* **SPARQL Query Endpoint:** Pattern-matching execution filters extracting data arrays based on target criteria like site ratings or visitor logs.


* **SimpleTupleKG Fallback:** A lightweight, dependency-free structural tuple array storage fallback utilizing generic wildcard pattern matching when external libraries are missing.





### 4. Bayesian Networks & Probabilistic Inference (`q4_bayesian_networks.py`)

* **Domain:** Directed acyclic risk modeling using the classic "Asia/Cancer" medical diagnostic literature case study.


* **Core Mechanisms:** Joint probability distribution mapping and factor table manipulation.


* **Algorithmic Operations:**
* **CPT Mapping:** Structured data classes mapping parent variable state combinations to underlying conditional probability tables.


* **Variable Elimination Engine:** Exact inference calculation engine executing variable elimination workflows ordered via an internal topological sorting algorithm.


* **Factor Manipulation Functions:** Algorithmic routines execution for calculating factor products, restricting tables by active evidence states, and marginalizing out hidden variables.


* **Query Methods:** Handles standard posterior distribution tracking alongside Maximum A Posteriori (`map_query`) joint configuration sequence estimates.





---

## Getting Started & Execution

### Prerequisites

To run the full suite, ensure your local environment runs Python 3.x with the standard semantic web dependencies configured:

```bash
pip install rdflib

```

(Note: `q4_bayesian_networks.py` operates entirely on native mathematical and iteration structures, but mentions industry alternatives like `pgmpy` or `PyMC` for real-world integration).

### Verification and Test Suites

Each pipeline includes automated validation workflows. Execute files individually to trigger internal assertions and diagnostics:

```bash
python q1_search_algorithms.py
python q2_travel_planner.py
python q3_knowledge_graphs.py
python q4_bayesian_networks.py

```
