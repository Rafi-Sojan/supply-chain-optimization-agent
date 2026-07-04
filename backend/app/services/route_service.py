from collections import defaultdict
from heapq import heappop, heappush
from math import asin, cos, radians, sin, sqrt


def _graph(edges: list[dict]) -> dict[str, list[tuple[str, float, float]]]:
    graph: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    for edge in edges:
        start = edge["from_node"]
        end = edge["to_node"]
        distance = float(edge["distance_km"])
        cost = distance * float(edge.get("cost_per_km", 1))
        graph[start].append((end, distance, cost))
        graph[end].append((start, distance, cost))
    return graph


def _minimum_cost_per_km(edges: list[dict]) -> float:
    values = [float(edge.get("cost_per_km", 1)) for edge in edges if float(edge.get("cost_per_km", 1)) > 0]
    return min(values) if values else 0.0


def _reconstruct(previous: dict[str, str], end: str) -> list[str]:
    path = [end]
    while path[-1] in previous:
        path.append(previous[path[-1]])
    return list(reversed(path))


def shortest_route(
    nodes: list[dict],
    edges: list[dict],
    start_node: str,
    end_node: str,
    algorithm: str = "dijkstra",
) -> dict:
    if start_node == end_node:
        return {"algorithm": algorithm, "path": [start_node], "distance_km": 0, "route_cost": 0}

    graph = _graph(edges)
    coordinates = {row["node_id"]: (float(row["latitude"]), float(row["longitude"])) for row in nodes}
    min_cost_per_km = _minimum_cost_per_km(edges)
    frontier = [(0.0, 0.0, start_node)]
    best_cost = {start_node: 0.0}
    best_distance = {start_node: 0.0}
    previous: dict[str, str] = {}

    while frontier:
        _, cost_so_far, node = heappop(frontier)
        if node == end_node:
            return {
                "algorithm": algorithm,
                "path": _reconstruct(previous, end_node),
                "distance_km": round(best_distance[end_node], 2),
                "route_cost": round(best_cost[end_node], 2),
            }
        if cost_so_far > best_cost.get(node, float("inf")):
            continue

        for neighbor, distance, edge_cost in graph.get(node, []):
            candidate_cost = best_cost[node] + edge_cost
            if candidate_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = candidate_cost
                best_distance[neighbor] = best_distance[node] + distance
                previous[neighbor] = node
                heuristic = 0.0
                if algorithm == "astar" and neighbor in coordinates and end_node in coordinates:
                    # Keep the heuristic conservative for arbitrary business data.
                    # A non-admissible heuristic can return a faster but more expensive route.
                    straight_line = _haversine_km(coordinates[neighbor], coordinates[end_node])
                    heuristic = min(0.0, straight_line * min_cost_per_km)
                heappush(frontier, (candidate_cost + heuristic, candidate_cost, neighbor))

    return {
        "algorithm": algorithm,
        "path": [],
        "distance_km": 0,
        "route_cost": 0,
        "error": f"No route found from {start_node} to {end_node}",
    }


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(radians, a)
    lat2, lon2 = map(radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    value = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371 * 2 * asin(sqrt(value))


def build_route_based_shipping_costs(dataset: dict, algorithm: str = "dijkstra") -> list[dict]:
    nodes = dataset.get("road_nodes", [])
    edges = dataset.get("road_edges", [])
    if not nodes or not edges:
        return dataset["shipping_costs"]

    warehouse_nodes = {row["warehouse_id"]: row["warehouse_id"] for row in dataset["warehouses"]}
    customer_nodes = {row["customer_id"]: row["customer_id"] for row in dataset["customers"]}
    routed_costs = []
    for lane in dataset["shipping_costs"]:
        start = warehouse_nodes.get(lane["warehouse_id"])
        end = customer_nodes.get(lane["customer_id"])
        route = shortest_route(nodes, edges, start, end, algorithm) if start and end else {"path": []}
        if route.get("path"):
            routed_costs.append(
                {
                    **lane,
                    "shipping_cost": route["route_cost"],
                    "distance_km": route["distance_km"],
                    "route_path": route["path"],
                    "route_algorithm": algorithm,
                }
            )
        else:
            routed_costs.append(lane)
    return routed_costs
