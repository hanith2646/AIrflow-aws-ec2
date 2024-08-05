from _typeshed import Incomplete

from networkx.utils.backends import _dispatch

@_dispatch
def eccentricity(G, v: Incomplete | None = None, sp: Incomplete | None = None, weight: Incomplete | None = None): ...
@_dispatch
def diameter(G, e: Incomplete | None = None, usebounds: bool = False, weight: Incomplete | None = None): ...
@_dispatch
def periphery(G, e: Incomplete | None = None, usebounds: bool = False, weight: Incomplete | None = None): ...
@_dispatch
def radius(G, e: Incomplete | None = None, usebounds: bool = False, weight: Incomplete | None = None): ...
@_dispatch
def center(G, e: Incomplete | None = None, usebounds: bool = False, weight: Incomplete | None = None): ...
@_dispatch
def barycenter(G, weight: Incomplete | None = None, attr: Incomplete | None = None, sp: Incomplete | None = None): ...
@_dispatch
def resistance_distance(G, nodeA, nodeB, weight: Incomplete | None = None, invert_weight: bool = True): ...