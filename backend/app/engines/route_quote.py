from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import shortest_path


class QuoteError(ValueError):
    """Validation failure for a quote request.

    code: "same_station"  — via equals start/end, must be rejected
          "via_not_found" — the required intermediate station is not in the graph
                            (distinct from an unknown start/end)
    """

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _unreachable(start: str, end: str, via: str | None) -> dict:
    return {"start": start, "end": end, "via": via, "hops": None,
            "fare": None, "reachable": False, "path": [], "legs": []}


def quote_route(
    edges: list[tuple[str, str]],
    start: str,
    end: str,
    rules: list[dict],
    via: str | None = None,
) -> dict:
    if via is not None and (via == start or via == end):
        raise QuoteError("same_station", "必经站不得与起点或终点相同")

    nodes = {c for pair in edges for c in pair}

    if via is None:
        # Behavior identical to the pre-change direct shortest-path quote:
        # an unknown or unreachable endpoint is simply unreachable.
        path = shortest_path(edges, start, end) if start in nodes and end in nodes else None
        if path is None:
            return _unreachable(start, end, None)
        hops = len(path) - 1
        return {"start": start, "end": end, "via": None, "hops": hops,
                "fare": fare_for_hops(hops, rules), "reachable": True,
                "path": path, "legs": [{"hops": hops, "path": path}]}

    # With a via: an unknown endpoint stays in-band unreachable, while an
    # unknown VIA is a distinct, explicit failure.
    if start not in nodes or end not in nodes:
        return _unreachable(start, end, via)
    if via not in nodes:
        raise QuoteError("via_not_found", f"必经站不在网络中: {via}")

    first = shortest_path(edges, start, via)
    second = shortest_path(edges, via, end)
    legs = [
        {"hops": None if p is None else len(p) - 1, "path": p or []}
        for p in (first, second)
    ]
    # Either leg unreachable -> the whole order is unreachable; never quote one leg alone.
    if first is None or second is None:
        result = _unreachable(start, end, via)
        result["legs"] = legs
        return result

    # Splice the two paths; the via station appears exactly once.
    path = first + second[1:]
    hops = sum(leg["hops"] for leg in legs)
    # Fare is priced by the TOTAL hop count on the existing table, never the sum of two leg fares.
    return {"start": start, "end": end, "via": via, "hops": hops,
            "fare": fare_for_hops(hops, rules), "reachable": True,
            "path": path, "legs": legs}
