from .cluster_regex import ClusterRegex
from .highlight_dependencies_of import HighlightDependenciesOf
from .highlight_dependents_of import HighlightDependentsOf
from .highlight_leafs import HighlightLeafs
from .highlight_roots import HighlightRoots
from .keep_only_ancestors_of import KeepOnlyAncestorsOf
from .keep_only_descendants_of import KeepOnlyDescendantsOf
from .remove_ancestors_of import RemoveAncestorsOf
from .remove_children import RemoveChildren
from .remove_descendants_of import RemoveDescendantsOf
from .remove_parents import RemoveParents
from .transitive_reduction import TransitiveReduction

MIDDLEWARES = [
    ClusterRegex,
    HighlightDependenciesOf,
    HighlightDependentsOf,
    HighlightLeafs,
    HighlightRoots,
    KeepOnlyAncestorsOf,
    KeepOnlyDescendantsOf,
    RemoveAncestorsOf,
    RemoveChildren,
    RemoveDescendantsOf,
    RemoveParents,
    TransitiveReduction,
]
