#!/usr/bin/env python3
"""
Langraph Agent: Add missing skos:prefLabel / skos:definition in a target language.
Author: ChatGPT
Date: 2025-08-09
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Tuple

import rdflib
from langgraph.graph import StateGraph, add_messages
# from langgraph.prebuilt import create_chat_agent
from langchain_ollama import ChatOllama
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, SKOS
import json

# ----------------------------------------------------------------------
# 1.  State definition
# ----------------------------------------------------------------------
@dataclass
class OntState:
    ontology: rdflib.Graph  # the RDF graph we are enriching
    target_lang: str        # e.g. 'fr' or 'es'
    added_triples: List[Tuple[URIRef, URIRef, Literal]]  # keep a log


# ----------------------------------------------------------------------
# 2.  LLM wrapper
# ----------------------------------------------------------------------
# Change the model name to whatever you have pulled
# LLM_MODEL = "granite3.3:latest"
CONFIG_PATH = os.getenv("ANNOTATE_CONFIG_PATH", "config.json")

try:
    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)
    # Mandatory keys – the script will exit if they’re missing
    LLM_MODEL = cfg["model"]
    BASE_URL  = cfg["base_url"]
except FileNotFoundError:
    print(f"[Config] Config file {CONFIG_PATH} not found – using defaults.")
    LLM_MODEL = "granite3.3:latest"
    BASE_URL  = "http://localhost:11434"
except json.JSONDecodeError as e:
    print(f"[Config] Error parsing {CONFIG_PATH}: {e} – using defaults.")
    LLM_MODEL = "granite3.3:latest"
    BASE_URL  = "http://localhost:11434"

llm = ChatOllama(model=LLM_MODEL, base_url=BASE_URL)

# ----------------------------------------------------------------------
# 3.  Node that processes a single class/property
# ----------------------------------------------------------------------
def process_triple(state: OntState) -> OntState:
    g = state.ontology
    target = state.target_lang

    # iterate over all triples where the subject is a class or property
    for subj in g.subjects(RDF.type, RDFS.Class):
        _process_resource(g, subj, target, state)
    for subj in g.subjects(RDF.type, RDF.Property):
        _process_resource(g, subj, target, state)

    return state


def _process_resource(g: rdflib.Graph, subj: URIRef, target_lang: str, state: OntState) -> None:
    """
    Check and add missing skos:prefLabel / skos:definition
    """
    # helper to get annotation in any language
    def get_any_annotation(pred: URIRef) -> Literal | None:
        for _, _, obj in g.triples((subj, pred, None)):
            if isinstance(obj, Literal):
                return obj
        return None

    # 1. prefLabel
    _ensure_annotation(
        g, subj, SKOS.prefLabel, target_lang, state,
        prompt_template=(
            "Translate the following label into {lang}.\n\n"
            "Label: {label}\n"
            "Target language: {lang}\n"
            "Respond with the translated label only."
        ),
        get_any=get_any_annotation
    )

    # 2. definition
    _ensure_annotation(
        g, subj, SKOS.definition, target_lang, state,
        prompt_template=(
            "Generate a definition in {lang} for the following concept.\n\n"
            "Existing definition: {definition}\n"
            "Target language: {lang}\n"
            "Respond with the definition only."
        ),
        get_any=get_any_annotation
    )


def _ensure_annotation(
    g: rdflib.Graph,
    subj: URIRef,
    predicate: URIRef,
    target_lang: str,
    state: OntState,
    prompt_template: str,
    get_any
) -> None:
    """
    If annotation in target_lang missing, create it using LLM.
    """
    # Search for existing annotation in target_lang
    exists = False
    for _, _, obj in g.triples((subj, predicate, None)):
        if isinstance(obj, Literal) and obj.language == target_lang:
            exists = True
            break

    if exists:
        return  # nothing to do

    # Grab any existing annotation in another language
    existing = get_any(predicate)

    # ----------- Fallbacks -------------
    if existing is None:
        if predicate == SKOS.prefLabel:
            # Prefer an existing rdfs:label in another language
            existing = get_any(RDFS.label)
            if existing is None:
                # Fallback to URI local name if no label exists
                label = str(subj).split('#')[-1] or str(subj).split('/')[-1]
                existing = Literal(label, lang=target_lang)
        elif predicate == SKOS.definition:
            # Prefer an existing rdfs:comment in another language
            existing = get_any(RDFS.comment)
    if existing is None:
                # If no comment, try to reuse a prefLabel
                existing = get_any(SKOS.prefLabel)
                if existing is None:
                    # Final fallback to URI local name
                    label = str(subj).split('#')[-1] or str(subj).split('/')[-1]
                    existing = Literal(label, lang=target_lang)
    # ------------------------------------

    if existing is None:
        # Still nothing to work from – skip this resource
        return

    # Build prompt
    prompt = prompt_template.format(
        label=existing.value if predicate == SKOS.prefLabel else "",
        definition=existing.value if predicate == SKOS.definition else "",
        lang=target_lang
    )

    # Call LLM
    try:
        response = llm.invoke(prompt)
        new_text = response.content.strip()
    except Exception as e:
        print(f"[LLM error] {e}")
        return

    # Add new annotation
    new_literal = Literal(new_text, lang=target_lang)
    g.add((subj, predicate, new_literal))
    state.added_triples.append((subj, predicate, new_literal))
    print(f"Added {predicate} for {subj} in language '{target_lang}'.")

# ----------------------------------------------------------------------
# 4.  Langgraph wiring
# ----------------------------------------------------------------------
def build_graph() -> StateGraph[OntState]:
    graph = StateGraph(OntState)

    # The only node in the graph processes everything
    graph.add_node("process", process_triple)

    # The graph entry point
    graph.set_entry_point("process")

    return graph


# ----------------------------------------------------------------------
# 5.  Main driver
# ----------------------------------------------------------------------
def main(ontology_path: str, output_path: str, target_lang: str = "fr") -> None:
    g = rdflib.Graph()
    # rdflib will infer the format from the file extension
    g.parse(ontology_path, format=None)

    # Create the agent state
    state = OntState(ontology=g, target_lang=target_lang, added_triples=[])

    # Build and run the graph
    graph = build_graph()
    chain = graph.compile()
    chain.invoke(state)  # run the whole pipeline

    # Dump enriched ontology to Turtle
    g.serialize(destination=output_path, format="turtle")
    print(f"Enriched ontology written to {output_path}.")
    print(f"Total new triples added: {len(state.added_triples)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Add missing skos:prefLabel / skos:definition in a target language."
    )
    parser.add_argument(
        "ontology_file", help="Path to the input ontology file (any RDF format)."
    )
    parser.add_argument(
        "output_file", help="Path where the enriched ontology will be written (TTL)."
    )
    parser.add_argument(
        "-l",
        "--lang",
        default="fr",
        help="Target language code (e.g. 'fr', 'es', 'de'). Default is 'fr'.",
    )

    args = parser.parse_args()
    main(args.ontology_file, args.output_file, args.lang)