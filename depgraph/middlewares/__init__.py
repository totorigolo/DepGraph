from .regex_cluster import ClusterRegex
from .transitive_reduction import TransitiveReduction

MIDDLEWARES = [
    TransitiveReduction,
    ClusterRegex,
]
