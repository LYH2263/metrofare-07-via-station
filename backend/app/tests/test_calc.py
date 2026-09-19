import pytest

from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import shortest_hops, shortest_path
from app.engines.route_quote import QuoteError, quote_route

EDGES = [("A1", "A2"), ("A2", "A3"), ("A2", "B1"), ("B1", "B2")]
# C-line is a disconnected component: reachable internally, never to the A/B net.
SPLIT_EDGES = EDGES + [("C1", "C2")]
RULES = [{"max_hops": 2, "price": 3.0}, {"max_hops": 4, "price": 4.0}, {"max_hops": None, "price": 6.0}]


def test_hops_a1_a3():
    assert shortest_hops(EDGES, "A1", "A3") == 2


def test_hops_a1_b2():
    assert shortest_hops(EDGES, "A1", "B2") == 3


def test_fare_by_hops():
    assert fare_for_hops(2, RULES) == 3.0
    assert fare_for_hops(3, RULES) == 4.0
    assert fare_for_hops(10, RULES) == 6.0


def test_quote():
    q = quote_route(EDGES, "A1", "B2", RULES)
    assert q["hops"] == 3 and q["fare"] == 4.0
    assert q["via"] is None and q["reachable"] is True
    assert q["path"] == ["A1", "A2", "B1", "B2"]
    assert len(q["legs"]) == 1 and q["legs"][0]["hops"] == 3


def test_no_via_unknown_endpoint_is_unreachable_not_error():
    # Pre-change behavior: an unknown endpoint is simply unreachable (no exception).
    q = quote_route(EDGES, "A1", "ZZ", RULES)
    assert q["reachable"] is False and q["hops"] is None and q["fare"] is None


def test_via_basic_two_legs_spliced():
    q = quote_route(EDGES, "A1", "B2", RULES, via="A3")
    assert q["reachable"] is True
    assert q["legs"][0]["hops"] == 2 and q["legs"][1]["hops"] == 3
    assert q["hops"] == 5
    assert q["path"] == ["A1", "A2", "A3", "A2", "B1", "B2"]
    # The via station appears exactly once; non-via stations may repeat on a detour.
    assert q["path"].count("A3") == 1
    assert q["hops"] == sum(l["hops"] for l in q["legs"]) == len(q["path"]) - 1


def test_via_fare_uses_total_hops_not_sum_of_leg_fares():
    # 2 hops would cost 3.0, 3 hops 4.0: summing leg fares gives 7.0.
    # The forced detour totals 5 hops -> open tier 6.0.
    q = quote_route(EDGES, "A1", "B2", RULES, via="A3")
    assert q["fare"] == 6.0


def test_via_on_shortest_path_matches_direct():
    direct = quote_route(EDGES, "A1", "B2", RULES)
    via = quote_route(EDGES, "A1", "B2", RULES, via="A2")
    assert via["hops"] == direct["hops"] == 3
    assert via["fare"] == direct["fare"] == 4.0
    assert via["path"] == ["A1", "A2", "B1", "B2"]


def test_via_equals_start_or_end_rejected():
    with pytest.raises(QuoteError) as e1:
        quote_route(EDGES, "A1", "B2", RULES, via="A1")
    assert e1.value.code == "same_station"
    with pytest.raises(QuoteError) as e2:
        quote_route(EDGES, "A1", "B2", RULES, via="B2")
    assert e2.value.code == "same_station"


def test_unknown_via_distinct_from_unknown_endpoint():
    with pytest.raises(QuoteError) as e:
        quote_route(EDGES, "A1", "B2", RULES, via="X9")
    assert e.value.code == "via_not_found"
    # Unknown start/end with a valid via stays an in-band unreachable result.
    q = quote_route(EDGES, "A1", "ZZ", RULES, via="A2")
    assert q["reachable"] is False


def test_either_leg_unreachable_makes_whole_order_unreachable():
    # C1->C2 is fine, C2->A1 is impossible: the whole quote is unreachable,
    # never a fare for just the reachable leg.
    q = quote_route(SPLIT_EDGES, "C1", "A1", RULES, via="C2")
    assert q["reachable"] is False
    assert q["hops"] is None and q["fare"] is None
    assert q["legs"][0]["hops"] == 1
    assert q["legs"][1]["hops"] is None and q["legs"][1]["path"] == []
