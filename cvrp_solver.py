"""
===============================================================================
 cvrp_solver.py
-------------------------------------------------------------------------------
 Algoritma Konstruksi (Clarke-Wright Savings) + Local Search (2-Opt & Relocate)
===============================================================================
"""

from typing import List, Tuple
from cvrp_instance import CVRPInstance
from solution import Solution, Route


class CVRPSolver:
    """Solver untuk menyelesaikan CVRP."""

    def __init__(self, instance: CVRPInstance):
        self.instance = instance

    def solve(self) -> Solution:
        """Menjalankan konstruksi dan peningkatan solusi."""
        solution = self.clarke_wright_savings()
        solution = self.local_search(solution)
        return solution

    def clarke_wright_savings(self) -> Solution:
        depot_id = self.instance.depot_id
        customer_ids = self.instance.customer_ids

        # Inisialisasi: setiap customer berada dalam rute mandiri
        routes_dict = {cid: [self.instance.get_node(cid)] for cid in customer_ids}

        # Hitung savings: S_ij = d(depot, i) + d(depot, j) - d(i, j)
        savings: List[Tuple[float, int, int]] = []
        for i in range(len(customer_ids)):
            for j in range(i + 1, len(customer_ids)):
                id1 = customer_ids[i]
                id2 = customer_ids[j]
                s = (
                    self.instance.distance(depot_id, id1)
                    + self.instance.distance(depot_id, id2)
                    - self.instance.distance(id1, id2)
                )
                savings.append((s, id1, id2))

        # Urutkan penghematan dari terbesar ke terkecil
        savings.sort(key=lambda x: x[0], reverse=True)

        # Penggabungan rute
        for _, id1, id2 in savings:
            r1_key, r2_key = None, None
            for key, r in routes_dict.items():
                if id1 in [n.id for n in r]:
                    r1_key = key
                if id2 in [n.id for n in r]:
                    r2_key = key

            if r1_key is not None and r2_key is not None and r1_key != r2_key:
                r1 = routes_dict[r1_key]
                r2 = routes_dict[r2_key]

                if sum(n.demand for n in r1) + sum(n.demand for n in r2) <= self.instance.capacity:
                    if r1[-1].id == id1 and r2[0].id == id2:
                        r1.extend(r2)
                        del routes_dict[r2_key]
                    elif r2[-1].id == id2 and r1[0].id == id1:
                        r2.extend(r1)
                        routes_dict[r1_key] = r2
                        del routes_dict[r2_key]
                    elif r1[0].id == id1 and r2[0].id == id2:
                        r1.reverse()
                        r1.extend(r2)
                        del routes_dict[r2_key]
                    elif r1[-1].id == id1 and r2[-1].id == id2:
                        r2.reverse()
                        r1.extend(r2)
                        del routes_dict[r2_key]

        sol = Solution(self.instance)
        for nodes in routes_dict.values():
            sol.add_route(Route(self.instance, nodes=nodes))
        return sol

    def local_search(self, solution: Solution) -> Solution:
        best_sol = solution.copy()
        improved = True

        while improved:
            improved = False
            # 1. 2-Opt intra-rute
            for route in best_sol.routes:
                if self._two_opt(route):
                    improved = True

            # 2. Relocate antar-rute
            if self._relocate(best_sol):
                improved = True

        return best_sol

    def _two_opt(self, route: Route) -> bool:
        nodes = route.nodes
        n = len(nodes)
        if n < 4:
            return False

        depot_id = self.instance.depot_id
        improved = False

        for i in range(n - 1):
            for j in range(i + 1, n):
                prev_i = depot_id if i == 0 else nodes[i - 1].id
                next_j = depot_id if j == n - 1 else nodes[j + 1].id

                cur_cost = (
                    self.instance.distance(prev_i, nodes[i].id)
                    + self.instance.distance(nodes[j].id, next_j)
                )
                new_cost = (
                    self.instance.distance(prev_i, nodes[j].id)
                    + self.instance.distance(nodes[i].id, next_j)
                )

                if new_cost < cur_cost:
                    nodes[i : j + 1] = reversed(nodes[i : j + 1])
                    improved = True
        return improved

    def _relocate(self, sol: Solution) -> bool:
        for r1 in sol.routes:
            for r2 in sol.routes:
                if r1 is r2 or len(r1) == 0:
                    continue

                for i, node in enumerate(r1.nodes):
                    if r2.total_demand + node.demand <= self.instance.capacity:
                        old_cost = r1.distance + r2.distance

                        for insert_pos in range(len(r2.nodes) + 1):
                            t1_nodes = r1.nodes[:i] + r1.nodes[i + 1 :]
                            t2_nodes = r2.nodes[:insert_pos] + [node] + r2.nodes[insert_pos:]

                            t1 = Route(self.instance, t1_nodes)
                            t2 = Route(self.instance, t2_nodes)

                            if t1.distance + t2.distance < old_cost - 1e-4:
                                r1.nodes = t1_nodes
                                r2.nodes = t2_nodes
                                sol.routes = [r for r in sol.routes if len(r) > 0]
                                return True
        return False