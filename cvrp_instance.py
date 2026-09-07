"""
===============================================================================
 cvrp_instance.py
-------------------------------------------------------------------------------
 Berisi kelas CVRPInstance: wadah seluruh data satu instance CVRP.

 Prinsip desain pada file ini:
   - KOMPOSISI     : CVRPInstance "memiliki" banyak objek Node
                     (relasi has-a, bukan pewarisan).
   - VARIABEL vs OBJEK :
                     kapasitas dan jumlah kendaraan cukup disimpan sebagai
                     variabel biasa karena hanya berupa satu angka tanpa
                     perilaku khusus. Node dijadikan objek karena punya banyak
                     atribut sekaligus perilaku.
   - PRECOMPUTATION : matriks jarak dihitung sekali di awal, bukan berulang
                     setiap kali dibutuhkan.
===============================================================================
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from node import Node


class CVRPInstance:
    """
    Menyimpan SELURUH data satu instance CVRP.

    Atribut utama
    -------------
    name, comment, edge_weight_type : metadata dari file .vrp
    capacity      : float -> kapasitas tiap kendaraan (Q)   [VARIABEL]
    num_vehicles  : int   -> jumlah kendaraan (m)           [VARIABEL]
    nodes         : list  -> kumpulan objek Node            [OBJEK]
    depot_id      : int   -> id node yang berperan sebagai depot
    """

    # =====================================================================
    # CONSTRUCTOR
    # =====================================================================
    def __init__(self, name: str = "", comment: str = "",
                 capacity: float = 0.0, num_vehicles: int = 0) -> None:
        # ---- Metadata instance ------------------------------------------
        self.name: str = name
        self.comment: str = comment
        self.edge_weight_type: str = "EUC_2D"

        # ---- Disimpan sebagai VARIABEL, bukan objek ---------------------
        self.capacity: float = capacity
        self.num_vehicles: int = num_vehicles

        # ---- Kumpulan OBJEK Node ----------------------------------------
        self.nodes: List[Node] = []          # seluruh node termasuk depot
        self._index: Dict[int, Node] = {}    # peta id -> Node, akses O(1)
        self.depot_id: int = 1

        # ---- Struktur data pendukung ------------------------------------
        self.distance_matrix: Optional[List[List[float]]] = None
        self._pos: Dict[int, int] = {}       # peta id -> indeks baris matriks

    # =====================================================================
    # BAGIAN 1 : PENGELOLAAN NODE
    # =====================================================================
    def add_node(self, node: Node) -> None:
        """
        Menambahkan objek Node ke dalam instance.

        Dua struktur data diisi sekaligus:
          - list  self.nodes  -> menjaga urutan, mudah di-iterasi
          - dict  self._index -> pencarian berdasarkan id dalam waktu O(1)
        Tanpa dictionary, mencari node harus menelusuri list (O(n)), yang
        akan sangat mahal bila dipanggil jutaan kali.
        """
        self.nodes.append(node)
        self._index[node.id] = node

    def get_node(self, node_id: int) -> Node:
        """Mengambil objek Node berdasarkan id-nya."""
        if node_id not in self._index:
            raise KeyError(f"Node dengan id {node_id} tidak ada pada instance.")
        return self._index[node_id]

    def has_node(self, node_id: int) -> bool:
        """Memeriksa keberadaan node."""
        return node_id in self._index

    # ---------------------------------------------------------------------
    # PROPERTY : diakses seperti atribut, tetapi dihitung saat dipanggil
    # ---------------------------------------------------------------------
    @property
    def depot(self) -> Node:
        """Objek Node yang berperan sebagai depot."""
        return self._index[self.depot_id]

    @property
    def customers(self) -> List[Node]:
        """Daftar objek Node pelanggan (tanpa depot)."""
        return [n for n in self.nodes if n.is_customer()]

    @property
    def customer_ids(self) -> List[int]:
        """
        Daftar id pelanggan saja.
        Nantinya menjadi dasar representasi solusi pada metaheuristik.
        """
        return [n.id for n in self.nodes if n.is_customer()]

    @property
    def dimension(self) -> int:
        """Jumlah seluruh node (depot + pelanggan)."""
        return len(self.nodes)

    # =====================================================================
    # BAGIAN 2 : MATRIKS JARAK
    # =====================================================================
    def build_distance_matrix(self, rounded: bool = True) -> None:
        """
        Menghitung matriks jarak antar seluruh node satu kali di awal.

        Mengapa perlu?
        Metaheuristik mengevaluasi jutaan kandidat solusi. Bila jarak dihitung
        ulang dengan math.sqrt setiap kali, program akan sangat lambat. Dengan
        matriks, pengambilan jarak menjadi operasi indexing O(1).

        Biaya memori: O(n^2). Untuk instance sangat besar (n > 10.000) sebaiknya
        gunakan perhitungan on-the-fly atau hanya menyimpan daftar tetangga
        terdekat setiap node.
        """
        n = self.dimension
        self._pos = {node.id: i for i, node in enumerate(self.nodes)}

        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                d = self.nodes[i].euclidean_distance(self.nodes[j], rounded=rounded)
                matrix[i][j] = d
                matrix[j][i] = d          # matriks simetris

        self.distance_matrix = matrix

    def distance(self, node_a, node_b) -> float:
        """
        Mengembalikan jarak antara dua node.
        Argumen boleh berupa id (int) maupun objek Node, agar pemakaian fleksibel.
        """
        id_a = node_a.id if isinstance(node_a, Node) else node_a
        id_b = node_b.id if isinstance(node_b, Node) else node_b

        if self.distance_matrix is None:
            return self.get_node(id_a).euclidean_distance(self.get_node(id_b))
        return self.distance_matrix[self._pos[id_a]][self._pos[id_b]]

    def nearest_neighbors(self, node_id: int, k: int = 5) -> List[int]:
        """
        Mengembalikan k node terdekat dari suatu node (tidak termasuk dirinya).
        Berguna untuk membatasi ruang pencarian (granular neighborhood)
        pada local search.
        """
        others = [n.id for n in self.nodes if n.id != node_id]
        others.sort(key=lambda other_id: self.distance(node_id, other_id))
        return others[:k]

    # =====================================================================
    # BAGIAN 3 : STATISTIK DAN VALIDASI
    # =====================================================================
    def total_demand(self) -> float:
        """Total permintaan seluruh pelanggan."""
        return sum(n.demand for n in self.customers)

    def average_demand(self) -> float:
        """Rata-rata permintaan per pelanggan."""
        pelanggan = self.customers
        return self.total_demand() / len(pelanggan) if pelanggan else 0.0

    def max_demand(self) -> float:
        """Permintaan terbesar di antara seluruh pelanggan."""
        return max((n.demand for n in self.customers), default=0.0)

    def total_fleet_capacity(self) -> float:
        """Total kapasitas armada = jumlah kendaraan x kapasitas per kendaraan."""
        return self.num_vehicles * self.capacity

    def min_vehicles_required(self) -> int:
        """
        Batas bawah jumlah kendaraan = ceil(total demand / kapasitas).
        Digunakan untuk memeriksa kecukupan armada.
        """
        if self.capacity <= 0:
            return 0
        return math.ceil(self.total_demand() / self.capacity)

    def is_feasible_instance(self) -> bool:
        """
        Memeriksa apakah instance mungkin diselesaikan:
          1. total demand tidak melebihi total kapasitas armada
          2. tidak ada pelanggan dengan demand melebihi kapasitas satu kendaraan
        """
        if self.total_demand() > self.total_fleet_capacity():
            return False
        return all(n.demand <= self.capacity for n in self.customers)

    # =====================================================================
    # BAGIAN 4 : PENCETAKAN UNTUK VERIFIKASI DATA
    # =====================================================================
    def print_summary(self) -> None:
        """Mencetak ringkasan instance."""
        print("=" * 70)
        print(" RINGKASAN INSTANCE CVRP")
        print("=" * 70)
        print(f" Nama instance            : {self.name}")
        print(f" Komentar                 : {self.comment}")
        print(f" Tipe perhitungan jarak   : {self.edge_weight_type}")
        print(f" Jumlah node (dimension)  : {self.dimension}")
        print(f" Jumlah pelanggan         : {len(self.customers)}")
        print(f" Depot (id)               : {self.depot_id} "
              f"-> koordinat {self.depot.coordinates()}")
        print(f" Kapasitas kendaraan (Q)  : {self.capacity:.0f}")
        print(f" Jumlah kendaraan (m)     : {self.num_vehicles}")
        print(f" Total demand             : {self.total_demand():.0f}")
        print(f" Rata-rata demand         : {self.average_demand():.2f}")
        print(f" Demand terbesar          : {self.max_demand():.0f}")
        print(f" Total kapasitas armada   : {self.total_fleet_capacity():.0f}")
        print(f" Minimum kendaraan        : {self.min_vehicles_required()} "
              f"(batas bawah teoritis)")
        print(f" Instance layak?          : "
              f"{'YA' if self.is_feasible_instance() else 'TIDAK'}")
        print("=" * 70)

    def print_nodes(self, limit: Optional[int] = None) -> None:
        """
        Mencetak isi seluruh objek Node.
        Dipakai untuk memastikan data hasil import tersimpan dengan benar.
        """
        print("\n" + "=" * 70)
        print(" DAFTAR OBJEK NODE")
        print("=" * 70)
        print(f"{'ID':>4} | {'Tipe':^8} | {'X':>8} | {'Y':>8} | {'Demand':>8}")
        print("-" * 70)

        data = self.nodes if limit is None else self.nodes[:limit]
        for node in data:
            tipe = "DEPOT" if node.is_depot else "Customer"
            print(f"{node.id:>4} | {tipe:^8} | {node.x:>8.2f} | "
                  f"{node.y:>8.2f} | {node.demand:>8.2f}")

        if limit is not None and len(self.nodes) > limit:
            print(f"... ({len(self.nodes) - limit} node lainnya tidak ditampilkan)")

        print("-" * 70)
        print(f"Ditampilkan {len(data)} node dari total {self.dimension} node.\n")

    def print_distance_matrix(self, limit: int = 8) -> None:
        """Mencetak cuplikan matriks jarak (bagian kiri atas)."""
        if self.distance_matrix is None:
            print("Matriks jarak belum dibangun. Panggil build_distance_matrix().")
            return

        n = min(limit, self.dimension)
        print("=" * 70)
        print(f" CUPLIKAN MATRIKS JARAK ({n} x {n} node pertama)")
        print("=" * 70)
        print("      " + "".join(f"{self.nodes[j].id:>7}" for j in range(n)))
        for i in range(n):
            baris = "".join(f"{self.distance_matrix[i][j]:>7.0f}" for j in range(n))
            print(f"{self.nodes[i].id:>5} " + baris)
        print("=" * 70 + "\n")

    # =====================================================================
    # DUNDER METHODS
    # =====================================================================
    def __len__(self) -> int:
        """Agar len(instance) mengembalikan jumlah node."""
        return self.dimension

    def __iter__(self):
        """Agar instance dapat langsung di-iterasi: for node in instance."""
        return iter(self.nodes)

    def __repr__(self) -> str:
        return (f"CVRPInstance(name='{self.name}', n={self.dimension}, "
                f"Q={self.capacity:.0f}, m={self.num_vehicles})")
