from collections import defaultdict, deque


def _build_graph(edges: list[tuple[str, str]]) -> dict[str, set[str]]:
    g: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        g[a].add(b)
        g[b].add(a)
    return g


def shortest_path(edges: list[tuple[str, str]], start: str, end: str) -> list[str] | None:
    """Undirected graph BFS; returns the station list of a shortest path
    (endpoints included), or None if either endpoint is absent / unreachable."""
    if start == end:
        return [start]
    g = _build_graph(edges)
    if start not in g or end not in g:
        return None
    q = deque([start])
    parent = {start: None}
    while q:
        cur = q.popleft()
        for nxt in g[cur]:
            if nxt in parent:
                continue
            parent[nxt] = cur
            if nxt == end:
                path = [end]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])
                path.reverse()
                return path
            q.append(nxt)
    return None


def shortest_hops(edges: list[tuple[str, str]], start: str, end: str) -> int | None:
    """Undirected graph BFS hop count; None if unreachable."""
    path = shortest_path(edges, start, end)
    return None if path is None else len(path) - 1
