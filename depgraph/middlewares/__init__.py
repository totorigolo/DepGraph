from .highlight_ancestors_of import HighlightAncestorsOf
from .highlight_children import HighlightChildren
from .highlight_descendants_of import HighlightDescendantsOf
from .highlight_parents import HighlightParents
from .regex_cluster import ClusterRegex
from .remove_children import RemoveChildren
from .remove_parents import RemoveParents
from .transitive_reduction import TransitiveReduction

MIDDLEWARES = [
    ClusterRegex,
    HighlightAncestorsOf,
    HighlightChildren,
    HighlightDescendantsOf,
    HighlightParents,
    RemoveChildren,
    RemoveParents,
    TransitiveReduction,
]
