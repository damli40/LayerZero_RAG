import re
from typing import Dict, List, Set, Tuple


def _normalize(text: str) -> str:
    return text.strip().lower()


def get_glossary() -> Dict[str, List[str]]:
    """
    Domain glossary mapping canonical terms to lists of synonyms/aliases.
    Extend this list with project-specific vocabulary as needed.
    """
    return {
        # Core brand/product
        "layerzero": ["layer zero", "lz", "layerzero labs"],
        # Applications
        "omnichain application": ["oapp", "o-app", "omni app"],
        "omnichain fungible token": ["oft", "o-f-t"],
        "omnichain non-fungible token": ["onft", "o-nft", "o n f t"],
        "BitGo": ["bitgo"],
        # Protocol / architecture terms
        "ultra light node": ["uln", "uln v2", "uln v3"],
        "decentralized verification network": ["dvn"],
        "endpoint": ["lz endpoint", "layerzero endpoint"],
        "executor": ["lz executor"],
        "oracle": ["lz oracle"],
        "relayer": ["lz relayer"],
        # Common abbreviations
        "cross-chain": ["xchain", "x-chain"],
        "bridge": ["bridging", "bridge tx", "bridge transaction"],
    }


def build_reverse_index(glossary: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Build a synonym->canonical reverse index for quick lookup.
    """
    reverse: Dict[str, str] = {}
    for canonical, synonyms in glossary.items():
        can = _normalize(canonical)
        for term in set([can] + [
            _normalize(s) for s in synonyms
        ]):
            reverse[term] = can
    return reverse


def _phrase_present(phrase: str, text: str) -> bool:
    pattern = r"\b" + re.escape(_normalize(phrase)) + r"\b"
    return re.search(pattern, _normalize(text)) is not None


def find_glossary_expansions(query: str) -> Tuple[Dict[str, Set[str]], Set[str]]:
    """
    Find which glossary terms occur in the query and compute expansions.

    Returns:
        - mapping canonical_term -> set of expansion terms to add
        - set of matched terms (for telemetry)
    """
    glossary = get_glossary()
    reverse = build_reverse_index(glossary)

    matched_terms: Set[str] = set()
    expansions: Dict[str, Set[str]] = {}

    # If query contains a synonym, add the canonical; if it contains canonical, add its synonyms
    for canonical, synonyms in glossary.items():
        can_norm = _normalize(canonical)
        # canonical present
        if _phrase_present(can_norm, query):
            matched_terms.add(canonical)
            to_add = {s for s in synonyms}
            if to_add:
                expansions.setdefault(canonical, set()).update(to_add)
        # any synonym present
        for syn in synonyms:
            if _phrase_present(syn, query):
                matched_terms.add(syn)
                expansions.setdefault(canonical, set()).add(canonical)

    return expansions, matched_terms


def augment_query_for_retrieval(query: str, max_terms: int = 12) -> str:
    """
    Append glossary-based expansions to the query to improve dense retrieval recall.
    """
    expansions, _ = find_glossary_expansions(query)
    if not expansions:
        return query

    terms_to_add: List[str] = []
    for canonical, extras in expansions.items():
        terms_to_add.append(canonical)
        terms_to_add.extend(sorted(list(extras)))

    # Deduplicate while preserving order
    seen: Set[str] = set()
    deduped: List[str] = []
    for t in terms_to_add:
        t_norm = _normalize(t)
        if t_norm not in seen:
            seen.add(t_norm)
            deduped.append(t)

    if not deduped:
        return query

    # Limit to avoid over-inflating the prompt
    deduped = deduped[:max_terms]

    # Add an explicit synonyms hint; this primarily affects retrieval embeddings
    appended = query.strip() + "\nSynonyms/aliases: " + ", ".join(deduped)
    return appended


