# Annotate‑Ontology

The *Annotate‑Ontology* agent enriches an existing RDF graph (`ontology`) by adding
language‑specific annotations (e.g. labels, comments, descriptions).  
The agent keeps a record of all triples that have been added so that it can
audit, debug or undo changes if necessary.

## config.json

Before running the code, copy the config.json_example file to a new file called config.json. Change the values to match your situtation. The example assumes you are running ollama locally and have granite3.3.

## Key Data Structure

```python
# src/annotate_ontology/annotate_ontology.py
class OntState:
    ontology: rdflib.Graph               # The RDF graph we are enriching
    target_lang: str                     # e.g. 'fr' or 'es'
    added_triples: List[Tuple[URIRef, URIRef, Literal]]
                                    # keep a log of all added triples
```

* **`ontology`** – The graph that will receive new triples.
* **`target_lang`** – The language code that the agent will target when
  generating annotations.
* **`added_triples`** – A list that the agent appends to whenever it adds a
  triple. Each entry is a `(subject, predicate, object)` tuple.

## Typical Usage

```python
from rdflib import Graph
from src.annotate_ontology.annotate_ontology import OntState

# 1. Load an existing ontology
g = Graph()
g.parse("my_ontology.ttl", format="turtle")

# 2. Initialise state
state = OntState(
    ontology=g,
    target_lang="fr",
    added_triples=[]
)

# 3. Run the agent (pseudo‑code)
#    The real implementation would iterate over the graph,
#    create language‑specific literals, add them, and log each triple.
annotate_ontology_agent(state)

# 4. Inspect what was added
for s, p, o in state.added_triples:
    print(f"Added triple: {s} {p} {o}")
```

> **Note**: The actual `annotate_ontology_agent` function is not shown in the
> snippet you provided, but it would use the `state` object to manage
> annotations.

## Flow Diagram

Below is a high‑level diagram of the agent’s workflow:

```
          +---------------------+
          |  Load RDF Graph     |
          +----------+----------+
                     |
                     v
          +---------------------+
          |  Initialise OntState|
          |  (ontology, target) |
          +----------+----------+
                     |
                     v
          +---------------------+
          |  Iterate over nodes |
          +----------+----------+
                     |
                     v
          +---------------------+
          |  Generate literal   |
          |  in target language |
          +----------+----------+
                     |
                     v
          +---------------------+
          |  Add triple to graph|
          +----------+----------+
                     |
                     v
          +---------------------+
          |  Log triple in      |
          |  added_triples list |
          +----------+----------+
                     |
                     v
          +---------------------+
          |  Continue until all |
          |  nodes processed    |
          +----------+----------+
                     |
                     v
          +---------------------+
          |  Agent finished     |
          +---------------------+
```

## Where to Learn More

* **`rdflib`** – The library used for RDF manipulation.  
  See its documentation: https://rdflib.readthedocs.io/
* **Turtle/JSON‑LD** – Formats for storing RDF graphs.  
  Common resources: W3C RDF Core and Turtle specs.
* **Ontology Enrichment** – General best practices for adding language‑specific
  annotations can be found in the OWL and SKOS documentation.

