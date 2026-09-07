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
     └── main.py              <- file ini
===============================================================================
"""

import os

from cvrp_instance import CVRPInstance
from import_data import InstanceReader


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
        """
        Membangun path file instance relatif terhadap lokasi main.py.

        Cara ini dipakai agar program tetap berjalan meskipun working directory
        VS Code berbeda dengan folder proyek. Memakai path relatif biasa seperti
        "A/A-n32-k5.vrp" sering menyebabkan FileNotFoundError.
        """
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

        print("Seluruh data instance sudah tersimpan dengan benar "
              "dalam bentuk objek.\n")

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

        # Contoh iterasi langsung atas objek instance
        total = sum(node.demand for node in instance if node.is_customer())
        print(f" Iterasi 'for node in instance' -> total demand : {total:.0f}")
        print("-" * 70 + "\n")


# =============================================================================
# TITIK EKSEKUSI PROGRAM
# =============================================================================
if __name__ == "__main__":
    Main.run()
