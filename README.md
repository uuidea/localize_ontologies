# localize‑Ontology

The *Annotate‑Ontology* agent enriches an existing RDF graph (`ontology`) by adding
language‑specific annotations (e.g. labels, comments, descriptions).  
The agent keeps a record of all triples that have been added so that it can
audit, debug or undo changes if necessary.




## Command‑Line Usage

The `annotate_ontology.py` script can be executed directly from the terminal.  
It takes three positional arguments:

1. **`ontology_file`** – Path to the input ontology (any RDF format that `rdflib` can parse, e.g. `.ttl`, `.rdf`, `.xml`, `.jsonld`).
2. **`output_file`** – Desired path for the enriched ontology (will be written in Turtle format).
3. **`--lang` / `-l`** – (Optional) Target language code (default is `fr`).

```bash
# Basic usage (French by default)
python src/localize_ontology/annotate_ontology.py \
  path/to/input_ontology.ttl \
  path/to/enriched_output.ttl

# Specify a different language (e.g. Spanish)
python src/localize_ontology/annotate_ontology.py \
  path/to/input_ontology.ttl \
  path/to/enriched_output.ttl \
  -l es

# Show help
python src/localize_ontology/annotate_ontology.py -h
```

### Prerequisites

1. **Python 3.9+** (recommended to use a virtual environment).
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. **LLM Configuration** –  
   The script reads a `config.json` file to determine the LLM model and base URL.  
   Copy `config.json_example` to `config.json` and edit the fields as needed.

### Example

```bash
python src/localize_ontology/annotate_ontology.py \
  data/dcterms.ttl \
  data/dcterms-nl.ttl \
  -l nl

```  
After execution, data/animals_enriched.ttl will contain the original triples plus any new skos:prefLabel or skos:definition triples that were generated in German. The console will also display a count of how many new triples were added.

Happy enriching!

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

## Typical Usage in python

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

