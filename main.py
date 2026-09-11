"""
===============================================================================
 main.py
-------------------------------------------------------------------------------
 MODUL : STRUKTUR DATA UNTUK METODE METAHEURISTIK
 Studi kasus : Capacitated Vehicle Routing Problem (CVRP)
 Format data : TSPLIB / VRPLIB (Augerat et al., set A)

 Struktur folder proyek:
     project/
     ├── A/
     │   └── A-n32-k5.vrp     <- file instance
     ├── node.py              <- kelas Node
     ├── cvrp_instance.py     <- kelas CVRPInstance
     ├── import_data.py       <- kelas InstanceReader
     ├── solution.py          <- kelas Route dan Solution
     ├── cvrp_solver.py       <- kelas CVRPSolver
     └── main.py              <- file ini
===============================================================================
"""

import os

from cvrp_instance import CVRPInstance
from import_data import InstanceReader
from solution import Solution, Route
from cvrp_solver import CVRPSolver


class Main:
    """
    Kelas utama yang mengatur alur program.

    Semua konfigurasi diletakkan sebagai atribut kelas (class attribute)
    agar mudah diubah dari satu tempat.
    """

    # ---- Konfigurasi lokasi data ----------------------------------------
    INSTANCE_FOLDER = "A"
    INSTANCE_FILE = "A-n32-k5.vrp"

    # =====================================================================
    @staticmethod
    def get_instance_path() -> str:
        """Membangun path file instance relatif terhadap lokasi main.py."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, Main.INSTANCE_FOLDER, Main.INSTANCE_FILE)

    # =====================================================================
    @staticmethod
    def run() -> None:
        """Alur utama program."""

        # -----------------------------------------------------------------
        # LANGKAH 1 : IMPORT DATA
        # -----------------------------------------------------------------
        print("\n[LANGKAH 1] Import data instance")
        path = Main.get_instance_path()
        instance = InstanceReader.read(path)
        InstanceReader.print_import_report(instance, path)

        # -----------------------------------------------------------------
        # LANGKAH 2 : VERIFIKASI DATA TERSIMPAN DENGAN BENAR
        # -----------------------------------------------------------------
        print("[LANGKAH 2] Verifikasi seluruh informasi hasil import\n")
        instance.print_summary()
        instance.print_nodes()
        instance.print_distance_matrix(limit=8)

        # -----------------------------------------------------------------
        # LANGKAH 3 : UJI AKSES OBJEK DAN METODE DI DALAM KELAS
        # -----------------------------------------------------------------
        print("[LANGKAH 3] Uji akses objek dan metode\n")
        Main.demo_kelas_node(instance)
        Main.demo_kelas_instance(instance)

        # -----------------------------------------------------------------
        # LANGKAH 4 : UJI KELAS SOLUTION DAN ROUTE
        # -----------------------------------------------------------------
        print("[LANGKAH 4] Uji pembuatan objek kelas Route dan Solution\n")
        Main.demo_kelas_solution(instance)

        # -----------------------------------------------------------------
        # LANGKAH 5 : OPTIMASI SOLUSI CVRP HINGGA NILAI OPTIMUM
        # -----------------------------------------------------------------
        print("[LANGKAH 5] Optimasi Penyelesaian Kasus CVRP (Clarke-Wright + Local Search)\n")
        solver = CVRPSolver(instance)
        best_solution = solver.solve()
        best_solution.print_summary()

        print("Program selesai dijalankan dengan sukses.\n")

    # =====================================================================
    # DEMONSTRASI PENGGUNAAN KELAS
    # =====================================================================
    @staticmethod
    def demo_kelas_node(instance: CVRPInstance) -> None:
        """Menunjukkan cara mengakses atribut dan metode pada kelas Node."""
        depot = instance.depot
        node_5 = instance.get_node(5)
        node_25 = instance.get_node(25)

        print("-" * 70)
        print(" DEMO KELAS Node")
        print("-" * 70)
        print(f" Objek depot                 : {depot!r}")
        print(f" Objek node 5                : {node_5!r}")
        print()
        print(f" node_5.id                   : {node_5.id}")
        print(f" node_5.coordinates()        : {node_5.coordinates()}")
        print(f" node_5.demand               : {node_5.demand:.0f}")
        print(f" node_5.is_customer()        : {node_5.is_customer()}")
        print(f" node_5.is_depot             : {node_5.is_depot}")
        print(f" node_5.fits_in(15)          : {node_5.fits_in(15)}   "
              f"(demand {node_5.demand:.0f} > sisa kapasitas 15)")
        print(f" node_5.fits_in(100)         : {node_5.fits_in(100)}")
        print()
        print(f" Jarak node 5 -> node 25 (Euclidean, dibulatkan) : "
              f"{node_5.euclidean_distance(node_25):.0f}")
        print(f" Jarak node 5 -> node 25 (Euclidean, presisi)    : "
              f"{node_5.euclidean_distance(node_25, rounded=False):.4f}")
        print(f" Jarak node 5 -> node 25 (Manhattan)             : "
              f"{node_5.manhattan_distance(node_25):.0f}")
        print()
        print(f" node_5.to_dict()            : {node_5.to_dict()}")
        print("-" * 70 + "\n")

    @staticmethod
    def demo_kelas_instance(instance: CVRPInstance) -> None:
        """Menunjukkan cara mengakses atribut dan metode pada kelas CVRPInstance."""
        print("-" * 70)
        print(" DEMO KELAS CVRPInstance")
        print("-" * 70)
        print(f" repr(instance)              : {instance!r}")
        print(f" len(instance)               : {len(instance)}")
        print()
        print(f" instance.capacity           : {instance.capacity:.0f}   [variabel]")
        print(f" instance.num_vehicles       : {instance.num_vehicles}     [variabel]")
        print(f" instance.depot_id           : {instance.depot_id}")
        print(f" instance.customer_ids[:10]  : {instance.customer_ids[:10]} ...")
        print()
        print(f" instance.distance(1, 5)     : {instance.distance(1, 5):.0f}   "
              f"(diambil dari matriks, O(1))")
        print(f" instance.nearest_neighbors(5, k=5) : "
              f"{instance.nearest_neighbors(5, k=5)}")
        print()
        print(f" instance.total_demand()     : {instance.total_demand():.0f}")
        print(f" instance.average_demand()   : {instance.average_demand():.2f}")
        print(f" instance.max_demand()       : {instance.max_demand():.0f}")
        print(f" instance.min_vehicles_required() : {instance.min_vehicles_required()}")
        print(f" instance.is_feasible_instance()  : {instance.is_feasible_instance()}")
        print()

        total = sum(node.demand for node in instance if node.is_customer())
        print(f" Iterasi 'for node in instance' -> total demand : {total:.0f}")
        print("-" * 70 + "\n")

    @staticmethod
    def demo_kelas_solution(instance: CVRPInstance) -> None:
        """Menunjukkan cara membuat dan mengevaluasi objek Route dan Solution."""
        print("-" * 70)
        print(" DEMO KELAS Route & Solution (Contoh Sederhana)")
        print("-" * 70)
        # Buat rute dummy contoh
        node_2 = instance.get_node(2)
        node_3 = instance.get_node(3)
        node_4 = instance.get_node(4)

        sample_route = Route(instance, nodes=[node_2, node_3, node_4])
        print(f" Objek Route contoh          : {sample_route}")
        print(f" Total Demand Rute           : {sample_route.total_demand:.0f}")
        print(f" Kelayakan Kapasitas Rute    : {sample_route.is_feasible}")
        print(f" Total Jarak Rute (Cost)     : {sample_route.distance:.0f}")
        print()

        dummy_solution = Solution(instance)
        dummy_solution.add_route(sample_route)
        print(f" Objek Solution contoh       : {dummy_solution!r}")
        print(f" Status Validitas Solusi     : {dummy_solution.is_feasible} (False karena belum melayani semua node)")
        print("-" * 70 + "\n")


# =============================================================================
# TITIK EKSEKUSI PROGRAM
# =============================================================================
if __name__ == "__main__":
    Main.run()