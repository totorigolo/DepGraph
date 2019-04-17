from .cluster_regex import ClusterRegex
from .highlight_dependencies_of import HighlightDependenciesOf
from .highlight_dependents_of import HighlightDependentsOf
from .highlight_leafs import HighlightLeafs
from .highlight_roots import HighlightRoots
from .keep_only_dependencies_of import KeepOnlyDependenciesOf
from .keep_only_dependents_of import KeepOnlyDependentsOf
from .remove_dependencies_of import RemoveDependenciesOf
from .remove_dependents_of import RemoveDependentsOf
from .remove_leafs import RemoveLeafs
from .remove_roots import RemoveRoots
from .transitive_reduction import TransitiveReduction

MIDDLEWARES = [
    ClusterRegex,
    HighlightDependenciesOf,
    HighlightDependentsOf,
    HighlightLeafs,
    HighlightRoots,
    KeepOnlyDependenciesOf,
    KeepOnlyDependentsOf,
    RemoveDependenciesOf,
    RemoveDependentsOf,
    RemoveLeafs,
    RemoveRoots,
    TransitiveReduction,
]
