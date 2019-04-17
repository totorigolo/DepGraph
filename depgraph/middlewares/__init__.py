from .highlight_ancestors_of import HighlightAncestorsOf
from .highlight_children import HighlightChildren
from .highlight_descendants_of import HighlightDescendantsOf
from .highlight_parents import HighlightParents
from .keep_only_ancestors_of import KeepOnlyAncestorsOf
from .keep_only_descendants_of import KeepOnlyDescendantsOf
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
    KeepOnlyAncestorsOf,
    KeepOnlyDescendantsOf,
    RemoveChildren,
    RemoveParents,
    TransitiveReduction,
]
