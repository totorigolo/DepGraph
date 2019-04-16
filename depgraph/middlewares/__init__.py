from .highlight_ancestors import HighlightAncestors
from .highlight_children import HighlightChildren
from .highlight_descendants import HighlightDescendants
from .highlight_parents import HighlightParents
from .regex_cluster import ClusterRegex
from .remove_children import RemoveChildren
from .remove_parents import RemoveParents
from .transitive_reduction import TransitiveReduction

MIDDLEWARES = [
    ClusterRegex,
    HighlightAncestors,
    HighlightChildren,
    HighlightDescendants,
    HighlightParents,
    RemoveChildren,
    RemoveParents,
    TransitiveReduction,
]
