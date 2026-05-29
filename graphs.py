"""
============================================================
  Q3: Knowledge Graphs — Description & Tool Exploration
  Implements a working KG using RDFLib (W3C standard RDF).
  Demonstrates:
    - KG construction (entities, properties, triples)
    - SPARQL querying
    - OWL-lite class hierarchy
    - JSON-LD and Turtle serialisation
    - Reasoning (subclass inference)
============================================================

  WHAT IS A KNOWLEDGE GRAPH?
  ───────────────────────────
  A Knowledge Graph (KG) is a structured semantic network that
  represents real-world entities and the relationships between
  them as a graph:

      Entity ──── Relation ──── Entity
       (node)       (edge)       (node)

  Key properties:
  • Entities  : real-world objects (places, people, concepts)
  • Relations : typed, directed edges between entities
  • Triples   : (Subject, Predicate, Object) — the atomic unit
  • Schema    : ontology defines classes and properties (OWL/RDFS)
  • Inference : new facts derived from existing ones via rules

  Famous KGs: Google Knowledge Graph, Wikidata, DBpedia,
              YAGO, Freebase, Amazon Product Graph

  TOOLS FOR BUILDING KNOWLEDGE GRAPHS
  ─────────────────────────────────────
  1. RDFLib       — Python library; W3C RDF/SPARQL standard
  2. Protégé      — GUI ontology editor (OWL/RDF); free, open source
  3. Neo4j        — Property Graph DB with Cypher query language
  4. Apache Jena  — Java framework for RDF + SPARQL reasoning
  5. Stardog      — Enterprise KG platform with OWL reasoning
  6. GraphDB      — Triplestore with visual exploration
  7. Wikidata     — Open public KG with SPARQL endpoint
  8. Amazon Neptune — Cloud-managed graph database (RDF + Property)
  9. OwlReady2    — Python OWL ontology manipulation
  10. AllegroGraph — High-performance triplestore + SPARQL

  This file uses RDFLib — installable with:  pip install rdflib
============================================================
"""

try:
    from rdflib import Graph, Namespace, Literal, URIRef
    from rdflib.namespace import RDF, RDFS, OWL, XSD, FOAF
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False
    print("⚠  rdflib not installed. Run: pip install rdflib")
    print("   Continuing with pure-Python fallback demonstration.\n")


# ─────────────────────────────────────────────────────────────
#  FALLBACK: Pure Python triple store (no rdflib needed)
# ─────────────────────────────────────────────────────────────

class SimpleTupleKG:
    """
    Minimal triple store when rdflib is unavailable.
    Stores (subject, predicate, object) tuples and supports
    basic pattern matching.
    """

    def __init__(self):
        self.triples = []

    def add(self, triple):
        """Accept a (subject, predicate, object) tuple."""
        self.triples.append(triple)

    def query(self, s=None, p=None, o=None):
        """Return triples matching the given pattern (None = wildcard)."""
        results = []
        for ts, tp, to in self.triples:
            if (s is None or s == ts) and \
               (p is None or p == tp) and \
               (o is None or o == to):
                results.append((ts, tp, to))
        return results

    def all_entities(self):
        subjects = {t[0] for t in self.triples}
        objects  = {t[2] for t in self.triples if not isinstance(t[2], (int, float))}
        return subjects | objects

    def display(self, header="Knowledge Graph Triples"):
        print(f"\n  {'─'*50}")
        print(f"  {header}  ({len(self.triples)} triples)")
        print(f"  {'─'*50}")
        for s, p, o in self.triples:
            print(f"  ({s}, {p}, {o})")


# ─────────────────────────────────────────────────────────────
#  TOURISM KNOWLEDGE GRAPH (using rdflib if available)
# ─────────────────────────────────────────────────────────────

def build_tourism_kg_rdflib():
    """
    Build a Tourism Knowledge Graph using rdflib.
    Models: City → TouristPlace, TouristPlace → Category,
            Person → visited → TouristPlace, ratings, etc.
    """
    g = Graph()

    # ── Define namespaces ─────────────────────────────────────
    TOUR  = Namespace("http://example.org/tourism#")
    GEO   = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    SCHEMA= Namespace("http://schema.org/")

    g.bind("tour",   TOUR)
    g.bind("geo",    GEO)
    g.bind("schema", SCHEMA)
    g.bind("foaf",   FOAF)

    # ── OWL Class definitions ─────────────────────────────────
    for cls in ["City", "TouristPlace", "Heritage", "NaturalSite",
                "Beach", "Person", "Restaurant", "Food", "Review"]:
        g.add((TOUR[cls], RDF.type, OWL.Class))

    # Sub-class relationships (OWL hierarchy)
    g.add((TOUR.Heritage,    RDFS.subClassOf, TOUR.TouristPlace))
    g.add((TOUR.NaturalSite, RDFS.subClassOf, TOUR.TouristPlace))
    g.add((TOUR.Beach,       RDFS.subClassOf, TOUR.NaturalSite))

    # ── OWL Object Properties ─────────────────────────────────
    for prop in ["locatedIn", "hasCategory", "visited", "recommends",
                 "hasCuisine", "servedAt"]:
        g.add((TOUR[prop], RDF.type, OWL.ObjectProperty))

    # ── OWL Datatype Properties ───────────────────────────────
    for prop in ["name", "rating", "entryFee", "latitude", "longitude"]:
        g.add((TOUR[prop], RDF.type, OWL.DatatypeProperty))

    # ── City entities ─────────────────────────────────────────
    cities = {
        "Hyderabad": ("17.3850", "78.4867"),
        "Goa":       ("15.2993", "74.1240"),
        "Jaipur":    ("26.9124", "75.7873"),
    }
    for city, (lat, lon) in cities.items():
        c = TOUR[city.replace(" ", "_")]
        g.add((c, RDF.type,        TOUR.City))
        g.add((c, TOUR.name,       Literal(city, datatype=XSD.string)))
        g.add((c, GEO.lat,         Literal(lat,  datatype=XSD.decimal)))
        g.add((c, GEO.long,        Literal(lon,  datatype=XSD.decimal)))

    # ── Tourist Place entities ────────────────────────────────
    places = [
        ("Charminar",     "Heritage",    "Hyderabad", 4.6, 25),
        ("Golconda_Fort", "Heritage",    "Hyderabad", 4.5, 15),
        ("Hussain_Sagar", "NaturalSite", "Hyderabad", 4.2,  0),
        ("Baga_Beach",    "Beach",       "Goa",       4.5,  0),
        ("Amber_Fort",    "Heritage",    "Jaipur",    4.8, 200),
        ("Hawa_Mahal",    "Heritage",    "Jaipur",    4.6,  50),
    ]
    for name, cat, city, rating, fee in places:
        p = TOUR[name]
        g.add((p, RDF.type,         TOUR[cat]))
        g.add((p, TOUR.name,        Literal(name.replace("_"," "), datatype=XSD.string)))
        g.add((p, TOUR.locatedIn,   TOUR[city]))
        g.add((p, TOUR.rating,      Literal(rating, datatype=XSD.decimal)))
        g.add((p, TOUR.entryFee,    Literal(fee,    datatype=XSD.integer)))

    # ── Person entities (tourists) ────────────────────────────
    people = [
        ("Alice", ["Charminar", "Golconda_Fort"]),
        ("Bob",   ["Baga_Beach", "Hussain_Sagar"]),
        ("Priya", ["Amber_Fort", "Hawa_Mahal", "Charminar"]),
    ]
    for person, visited_places in people:
        pe = TOUR[person]
        g.add((pe, RDF.type,     FOAF.Person))
        g.add((pe, FOAF.name,    Literal(person, datatype=XSD.string)))
        for place in visited_places:
            g.add((pe, TOUR.visited, TOUR[place]))

    return g, TOUR


def sparql_queries(g, TOUR):
    """Run several SPARQL queries on the tourism KG."""

    print("\n  ── SPARQL QUERY 1: All Heritage sites with ratings ──")
    q1 = """
        PREFIX tour: <http://example.org/tourism#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?name ?rating ?city
        WHERE {
            ?place a tour:Heritage ;
                   tour:name   ?name   ;
                   tour:rating ?rating ;
                   tour:locatedIn ?c .
            ?c tour:name ?city .
        }
        ORDER BY DESC(?rating)
    """
    for row in g.query(q1):
        print(f"     {str(row.name):<20} rating={row.rating}  city={row.city}")

    print("\n  ── SPARQL QUERY 2: Places visited by Priya ──")
    q2 = """
        PREFIX tour: <http://example.org/tourism#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?place_name
        WHERE {
            ?person foaf:name "Priya" ;
                    tour:visited ?place .
            ?place tour:name ?place_name .
        }
    """
    for row in g.query(q2):
        print(f"     {row.place_name}")

    print("\n  ── SPARQL QUERY 3: Free entry tourist places ──")
    q3 = """
        PREFIX tour: <http://example.org/tourism#>
        SELECT ?name ?city
        WHERE {
            ?place tour:name    ?name ;
                   tour:entryFee 0    ;
                   tour:locatedIn ?c  .
            ?c tour:name ?city .
        }
    """
    for row in g.query(q3):
        print(f"     {str(row.name):<20} in {row.city}")

    print("\n  ── SPARQL QUERY 4: Top-rated places (rating ≥ 4.5) ──")
    q4 = """
        PREFIX tour: <http://example.org/tourism#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?name ?rating
        WHERE {
            ?place tour:name   ?name   ;
                   tour:rating ?rating .
            FILTER(?rating >= 4.5)
        }
        ORDER BY DESC(?rating)
    """
    for row in g.query(q4):
        print(f"     {str(row.name):<20} ⭐ {row.rating}")


def serialise_kg(g):
    """Show KG in Turtle and JSON-LD formats."""
    print("\n  ── TURTLE SERIALISATION (first 30 lines) ──")
    turtle = g.serialize(format="turtle")
    lines  = turtle.split("\n")
    for line in lines[:30]:
        print("  " + line)
    print("  ... (truncated)")

    print("\n  ── JSON-LD SERIALISATION (first 20 lines) ──")
    try:
        jsonld = g.serialize(format="json-ld", indent=2)
        for line in jsonld.split("\n")[:20]:
            print("  " + line)
        print("  ... (truncated)")
    except Exception:
        print("  (json-ld plugin not installed — pip install rdflib-jsonld)")


# ─────────────────────────────────────────────────────────────
#  FALLBACK DEMO (pure Python)
# ─────────────────────────────────────────────────────────────

def build_tourism_kg_fallback():
    kg = SimpleTupleKG()

    # Class hierarchy
    kg.add(("Heritage",    "subClassOf", "TouristPlace"))
    kg.add(("NaturalSite", "subClassOf", "TouristPlace"))
    kg.add(("Beach",       "subClassOf", "NaturalSite"))

    # Entities
    kg.add(("Charminar",   "type",       "Heritage"))
    kg.add(("Charminar",   "locatedIn",  "Hyderabad"))
    kg.add(("Charminar",   "rating",     4.6))
    kg.add(("Charminar",   "entryFee",   25))

    kg.add(("Golconda_Fort", "type",      "Heritage"))
    kg.add(("Golconda_Fort", "locatedIn", "Hyderabad"))
    kg.add(("Golconda_Fort", "rating",    4.5))
    kg.add(("Golconda_Fort", "entryFee",  15))

    kg.add(("Baga_Beach",  "type",       "Beach"))
    kg.add(("Baga_Beach",  "locatedIn",  "Goa"))
    kg.add(("Baga_Beach",  "rating",     4.5))
    kg.add(("Baga_Beach",  "entryFee",   0))

    kg.add(("Amber_Fort",  "type",       "Heritage"))
    kg.add(("Amber_Fort",  "locatedIn",  "Jaipur"))
    kg.add(("Amber_Fort",  "rating",     4.8))
    kg.add(("Amber_Fort",  "entryFee",   200))

    # People
    kg.add(("Alice", "type",    "Person"))
    kg.add(("Alice", "visited", "Charminar"))
    kg.add(("Alice", "visited", "Golconda_Fort"))

    kg.add(("Priya", "type",    "Person"))
    kg.add(("Priya", "visited", "Amber_Fort"))
    kg.add(("Priya", "visited", "Charminar"))

    return kg


def query_fallback_kg(kg):
    print("\n  ── QUERY: All Heritage sites ──")
    heritage_entities = [s for s, p, o in kg.query(p="type", o="Heritage")]
    for e in heritage_entities:
        rating  = kg.query(s=e, p="rating")
        city    = kg.query(s=e, p="locatedIn")
        r = rating[0][2]  if rating  else "?"
        c = city[0][2]    if city    else "?"
        print(f"     {e:<20} ⭐{r}  in {c}")

    print("\n  ── QUERY: Places visited by Priya ──")
    visited = kg.query(s="Priya", p="visited")
    for _, _, place in visited:
        print(f"     {place}")

    print("\n  ── QUERY: Free-entry places ──")
    free_places = [s for s, p, o in kg.query(p="entryFee", o=0)]
    for place in free_places:
        city = kg.query(s=place, p="locatedIn")
        c = city[0][2] if city else "?"
        print(f"     {place} in {c}")

    print("\n  ── SUBCLASS INFERENCE: What is a Beach? ──")
    # Walk subClassOf chain: Beach → NaturalSite → TouristPlace
    def get_superclasses(entity_type):
        chain = [entity_type]
        current = entity_type
        while True:
            parents = kg.query(s=current, p="subClassOf")
            if not parents:
                break
            parent = parents[0][2]
            chain.append(parent)
            current = parent
        return chain

    beach_chain = get_superclasses("Beach")
    print(f"     Beach  →  {' → '.join(beach_chain)}")
    baga_type = kg.query(s="Baga_Beach", p="type")[0][2]
    chain = get_superclasses(baga_type)
    print(f"     Baga_Beach is a {baga_type}, which is a: {' → '.join(chain)}")


# ─────────────────────────────────────────────────────────────
#  TEST CASES
# ─────────────────────────────────────────────────────────────

def run_kg_demo():
    print("\n" + "█"*62)
    print("  Q3: KNOWLEDGE GRAPH — DEMO & TOOL EXPLORATION")
    print("█"*62)

    if RDFLIB_AVAILABLE:
        print("\n   rdflib found — using W3C-standard RDF/SPARQL")
        g, TOUR = build_tourism_kg_rdflib()
        print(f"\n  KG built with {len(g)} triples")
        sparql_queries(g, TOUR)
        serialise_kg(g)

        # Test triple count
        assert len(g) > 30, "KG should have more than 30 triples"
        print("\n   Triple count assertion passed")

        # Test SPARQL query returns results
        q = """
            PREFIX tour: <http://example.org/tourism#>
            SELECT (COUNT(?p) AS ?count)
            WHERE { ?p a tour:Heritage }
        """
        results = list(g.query(q))
        count = int(results[0][0])
        assert count >= 4, f"Expected ≥ 4 heritage sites, got {count}"
        print(f"   Heritage count assertion passed (found {count})")

    else:
        print("\n  ⚠  Using pure-Python fallback KG (no rdflib)")
        kg = build_tourism_kg_fallback()
        kg.display("Tourism Knowledge Graph")
        query_fallback_kg(kg)

        # Test queries
        heritage = [s for s, p, o in kg.query(p="type", o="Heritage")]
        assert len(heritage) >= 3, "Expected ≥ 3 heritage sites"
        print(f"\n   Heritage count: {len(heritage)}")

        visited = kg.query(s="Priya", p="visited")
        assert len(visited) == 2
        print(f"   Priya visited {len(visited)} places")

        free = [s for s, p, o in kg.query(p="entryFee", o=0)]
        assert len(free) >= 1
        print(f"   Free-entry places found: {len(free)}")

    print("\n" + "═"*62)
    print("  KG TOOLS SUMMARY")
    print("═"*62)
    tools = [
        ("RDFLib",        "Python",  "W3C RDF triples + SPARQL queries"),
        ("Protégé",       "GUI",     "OWL ontology editor with reasoning"),
        ("Neo4j",         "DB",      "Property Graph, Cypher query language"),
        ("Apache Jena",   "Java",    "RDF framework + rule-based inference"),
        ("Stardog",       "Cloud",   "Enterprise KG + OWL2 reasoning"),
        ("GraphDB",       "GUI/DB",  "Triplestore with visual explorer"),
        ("Wikidata",      "Public",  "Open KG with SPARQL endpoint"),
        ("OwlReady2",     "Python",  "OWL ontology manipulation in Python"),
        ("AllegroGraph",  "DB",      "High-performance triplestore"),
        ("Amazon Neptune","Cloud",   "Managed graph DB (RDF + Property)"),
    ]
    print(f"  {'Tool':<18} {'Type':<10} Description")
    print(f"  {'─'*18} {'─'*10} {'─'*28}")
    for tool, ttype, desc in tools:
        print(f"  {tool:<18} {ttype:<10} {desc}")

    print("\n   ALL KG TESTS PASSED")


if __name__ == "__main__":
    run_kg_demo()
