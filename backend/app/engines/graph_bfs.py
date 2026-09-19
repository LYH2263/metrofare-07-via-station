from collections import defaultdict, deque


def graph_nodes(edges: list[tuple[str, str]]) -> set[str]:
    nodes: set[str] = set()
    for a, b in edges:
        nodes.add(a)
        nodes.add(b)
    return nodes


def shortest_path(edges: list[tuple[str, str]], start: str, end: str) -> list[str] | None:
    """Undirected BFS shortest path as station list (inclusive); None if unreachable."""
    if start == end:
        return [start]
    g: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        g[a].add(b)
        g[b].add(a)
    if start not in g or end not in g:
        return None
    prev: dict[str, str | None] = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        for nxt in sorted(g[cur]):
            if nxt in prev:
                continue
            prev[nxt] = cur
            if nxt == end:
                path = [end]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])
                path.reverse()
                return path
            q.append(nxt)
    return None


def shortest_hops(edges: list[tuple[str, str]], start: str, end: str) -> int | None:
    """Undirected graph BFS hop count; None if unreachable."""
    if start == end:
        return 0
    g: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        g[a].add(b)
        g[b].add(a)
    if start not in g or end not in g:
        return None
    q = deque([(start, 0)])
    seen = {start}
    while q:
        cur, d = q.popleft()
        for nxt in g[cur]:
            if nxt in seen:
                continue
            if nxt == end:
                return d + 1
            seen.add(nxt)
            q.append((nxt, d + 1))
    return None
