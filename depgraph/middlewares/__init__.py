from .highlight_ancestors import HighlightAncestors
from .highlight_parents import HighlightParents
from .regex_cluster import ClusterRegex
from .transitive_reduction import TransitiveReduction

MIDDLEWARES = [
    TransitiveReduction,
    ClusterRegex,
    HighlightAncestors,
    HighlightParents,
]
