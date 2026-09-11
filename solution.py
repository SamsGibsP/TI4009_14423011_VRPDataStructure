"""
===============================================================================
 solution.py
-------------------------------------------------------------------------------
 Kelas Route dan Solution untuk Capacitated Vehicle Routing Problem (CVRP)
===============================================================================
"""

from typing import List, Optional
from node import Node
from cvrp_instance import CVRPInstance


class Route:
    """
    Kelas untuk merepresentasikan satu rute perjalanan kendaraan.
    Rute menyimpan daftar objek Node yang dikunjungi (tanpa depot di awal/akhir).
    """
    __slots__ = ("instance", "nodes")

    def __init__(self, instance: CVRPInstance, nodes: Optional[List[Node]] = None):
        self.instance = instance
        self.nodes: List[Node] = nodes if nodes is not None else []

    @property
    def total_demand(self) -> float:
        """Menghitung total muatan (demand) yang dibawa rute ini."""
        return sum(node.demand for node in self.nodes)

    @property
    def is_feasible(self) -> bool:
        """Mengecek apakah muatan rute tidak melebihi kapasitas kendaraan."""
        return self.total_demand <= self.instance.capacity

    @property
    def distance(self) -> float:
        """
        Menghitung total jarak rute secara O(1) per segmen:
        Depot -> Node_1 -> Node_2 -> ... -> Node_k -> Depot
        """
        if not self.nodes:
            return 0.0

        depot_id = self.instance.depot_id
        total_dist = 0.0

        # Jarak Depot -> Node pertama
        total_dist += self.instance.distance(depot_id, self.nodes[0].id)

        # Jarak antar node customer
        for i in range(len(self.nodes) - 1):
            total_dist += self.instance.distance(self.nodes[i].id, self.nodes[i + 1].id)

        # Jarak Node terakhir -> Depot
        total_dist += self.instance.distance(self.nodes[-1].id, depot_id)

        return total_dist

    def copy(self) -> 'Route':
        """Membuat salinan cepat (shallow copy pada nodes) dari rute."""
        new_route = Route(self.instance)
        new_route.nodes = list(self.nodes)
        return new_route

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        route_str = " -> ".join(str(n.id) for n in self.nodes)
        return (f"Route(Depot -> {route_str} -> Depot | "
                f"Demand: {self.total_demand:.0f}/{self.instance.capacity:.0f} | "
                f"Cost: {self.distance:.0f})")


class Solution:
    """
    Kelas untuk merepresentasikan sebuah solusi lengkap CVRP (koleksi rute).
    """
    __slots__ = ("instance", "routes")

    def __init__(self, instance: CVRPInstance, routes: Optional[List[Route]] = None):
        self.instance = instance
        self.routes: List[Route] = routes if routes is not None else []

    def add_route(self, route: Route) -> None:
        """Menambahkan rute ke dalam solusi."""
        self.routes.append(route)

    @property
    def total_cost(self) -> float:
        """Total jarak seluruh rute kendaraan (Fungsi Tujuan)."""
        return sum(route.distance for route in self.routes)

    @property
    def num_vehicles_used(self) -> int:
        """Jumlah kendaraan aktif (rute yang tidak kosong)."""
        return sum(1 for route in self.routes if len(route) > 0)

    @property
    def is_feasible(self) -> bool:
        """
        Memvalidasi kelayakan solusi:
        1. Muatan tiap rute <= kapasitas kendaraan.
        2. Jumlah armada <= batas num_vehicles (jika ada).
        3. Seluruh customer terlayani tepat satu kali.
        """
        # 1. Cek kapasitas tiap rute
        if not all(route.is_feasible for route in self.routes):
            return False

        # 2. Cek jumlah armada
        if self.instance.num_vehicles and self.num_vehicles_used > self.instance.num_vehicles:
            return False

        # 3. Cek apakah setiap customer dikunjungi tepat 1 kali
        visited_ids = [node.id for route in self.routes for node in route.nodes]
        if len(visited_ids) != len(set(visited_ids)):
            return False

        expected_ids = set(self.instance.customer_ids)
        if set(visited_ids) != expected_ids:
            return False

        return True

    def copy(self) -> 'Solution':
        """Deep copy dari solusi untuk kebutuhan neighborhood search/metaheuristik."""
        new_sol = Solution(self.instance)
        new_sol.routes = [r.copy() for r in self.routes]
        return new_sol

    def print_summary(self) -> None:
        """Mencetak ringkasan solusi."""
        print("-" * 70)
        print(f" HASIL EVALUASI SOLUSI: {self.instance.name if hasattr(self.instance, 'name') else 'CVRP'}")
        print("-" * 70)
        print(f" Total Biaya Jarak (Cost)    : {self.total_cost:.0f}")
        print(f" Jumlah Kendaraan Digunakan  : {self.num_vehicles_used} / {self.instance.num_vehicles or '-'}")
        print(f" Status Solusi (Feasible)    : {'FEASIBLE (VALID)' if self.is_feasible else 'INFEASIBLE'}")
        print()
        print(" Detail Rute:")
        for idx, route in enumerate(self.routes, 1):
            if len(route) > 0:
                print(f"   [{idx}] {route}")
        print("-" * 70 + "\n")

    def __repr__(self) -> str:
        return (f"Solution(Cost={self.total_cost:.0f}, "
                f"Vehicles={self.num_vehicles_used}, "
                f"Feasible={self.is_feasible})")