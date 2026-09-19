import pytest

from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import shortest_hops, shortest_path
from app.engines.route_quote import QuoteError, quote_route

EDGES = [("A1", "A2"), ("A2", "A3"), ("A2", "B1"), ("B1", "B2")]
RULES = [{"max_hops": 2, "price": 3.0}, {"max_hops": 4, "price": 4.0}, {"max_hops": None, "price": 6.0}]


def test_hops_a1_a3():
    assert shortest_hops(EDGES, "A1", "A3") == 2


def test_hops_a1_b2():
    assert shortest_hops(EDGES, "A1", "B2") == 3


def test_path_a1_b2():
    assert shortest_path(EDGES, "A1", "B2") == ["A1", "A2", "B1", "B2"]


def test_fare_by_hops():
    assert fare_for_hops(2, RULES) == 3.0
    assert fare_for_hops(3, RULES) == 4.0
    assert fare_for_hops(10, RULES) == 6.0


def test_quote():
    q = quote_route(EDGES, "A1", "B2", RULES)
    assert q["hops"] == 3 and q["fare"] == 4.0
    assert q["via"] is None and q["path"] == ["A1", "A2", "B1", "B2"]


def test_quote_via_hops_is_sum_and_path_joined_once():
    q = quote_route(EDGES, "A1", "B2", RULES, via="A2")
    assert q["reachable"] is True
    assert [s["hops"] for s in q["segments"]] == [1, 2]
    assert q["hops"] == 3  # sum of the two legs
    assert q["path"] == ["A1", "A2", "B1", "B2"]
    assert q["path"].count("A2") == 1  # via appears only once


def test_quote_via_fare_on_total_hops_not_segment_sum():
    q = quote_route(EDGES, "A1", "B2", RULES, via="A2")
    # total 3 hops -> 4.0; adding leg fares (3.0 + 3.0 = 6.0) would be wrong
    assert q["fare"] == 4.0


def test_quote_via_equals_endpoint_rejected():
    with pytest.raises(QuoteError):
        quote_route(EDGES, "A1", "B2", RULES, via="A1")
    with pytest.raises(QuoteError):
        quote_route(EDGES, "A1", "B2", RULES, via="B2")


def test_quote_via_unknown_distinct_from_unknown_end():
    q_via = quote_route(EDGES, "A1", "B2", RULES, via="Z9")
    q_end = quote_route(EDGES, "A1", "Z9", RULES)
    assert q_via["reachable"] is False and q_via["error"]["code"] == "via_unknown"
    assert q_end["reachable"] is False and q_end["error"]["code"] == "station_unknown"
    assert q_via["error"]["code"] != q_end["error"]["code"]


def test_quote_via_leg_unreachable_whole_quote_unreachable():
    edges = EDGES + [("C1", "C2")]  # C1/C2 island, disconnected from A/B
    q = quote_route(edges, "A1", "B2", RULES, via="C1")
    assert q["reachable"] is False
    assert q["error"]["code"] == "unreachable"
    assert q["hops"] is None and q["fare"] is None  # no partial leg fare
    assert q["path"] is None and q["segments"] is None
