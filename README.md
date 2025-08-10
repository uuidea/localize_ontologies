# Annotate‑Ontology

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

**LLM Configuration** –  
The script reads a `config.json` file to determine the LLM model and base URL.  
Copy `config.json_example` to `config.json` and edit the fields as needed.

### Example

```bash
python src/localize_ontology/annotate_ontology.py \
  data/dcterms.ttl \
  data/dcterms-nl.ttl \
  -l de

```  
After execution, data/animals_enriched.ttl will contain the original triples plus any new skos:prefLabel or skos:definition triples that were generated in German. The console will also display a count of how many new triples were added.

Happy enriching!

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
