from fastapi import APIRouter, Query

from app.services.data_service import load_dataset
from app.services.route_service import shortest_route


router = APIRouter(prefix="/routes", tags=["Route Planning"])


@router.get("/network")
def road_network() -> dict:
    dataset = load_dataset()
    return {
        "nodes": dataset.get("road_nodes", []),
        "edges": dataset.get("road_edges", []),
    }


@router.get("/shortest-path")
def shortest_path(
    start_node: str = Query(...),
    end_node: str = Query(...),
    algorithm: str = Query(default="dijkstra", pattern="^(dijkstra|astar)$"),
) -> dict:
    dataset = load_dataset()
    return shortest_route(
        dataset.get("road_nodes", []),
        dataset.get("road_edges", []),
        start_node,
        end_node,
        algorithm,
    )
