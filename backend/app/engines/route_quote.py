from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import graph_nodes, shortest_path


class QuoteError(ValueError):
    """Invalid quote input that must be rejected (HTTP 400)."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _err(start: str, end: str, via: str | None, code: str, message: str) -> dict:
    return {
        "start": start,
        "end": end,
        "via": via,
        "hops": None,
        "fare": None,
        "reachable": False,
        "path": None,
        "segments": None,
        "error": {"code": code, "message": message},
    }


def quote_route(
    edges: list[tuple[str, str]],
    start: str,
    end: str,
    rules: list[dict],
    via: str | None = None,
) -> dict:
    if via is not None and via in (start, end):
        raise QuoteError("via_equals_endpoint", "必经站不能与起点或终点相同")

    nodes = graph_nodes(edges)
    if via is not None and via not in nodes:
        return _err(start, end, via, "via_unknown", f"必经站 {via} 不在图中")
    if start not in nodes or end not in nodes:
        missing = [c for c in (start, end) if c not in nodes]
        return _err(start, end, via, "station_unknown", f"站点不在图中: {', '.join(missing)}")

    if via is None:
        path = shortest_path(edges, start, end)
        if path is None:
            return _err(start, end, None, "unreachable", f"{start} 到 {end} 不可达")
        hops = len(path) - 1
        return {
            "start": start,
            "end": end,
            "via": None,
            "hops": hops,
            "fare": fare_for_hops(hops, rules),
            "reachable": True,
            "path": path,
            "segments": None,
            "error": None,
        }

    leg1 = shortest_path(edges, start, via)
    if leg1 is None:
        return _err(start, end, via, "unreachable", f"{start} 到必经站 {via} 不可达")
    leg2 = shortest_path(edges, via, end)
    if leg2 is None:
        return _err(start, end, via, "unreachable", f"必经站 {via} 到 {end} 不可达")

    path = leg1 + leg2[1:]  # via station appears once
    hops = len(path) - 1
    return {
        "start": start,
        "end": end,
        "via": via,
        "hops": hops,
        "fare": fare_for_hops(hops, rules),
        "reachable": True,
        "path": path,
        "segments": [
            {"from": start, "to": via, "hops": len(leg1) - 1, "path": leg1},
            {"from": via, "to": end, "hops": len(leg2) - 1, "path": leg2},
        ],
        "error": None,
    }
