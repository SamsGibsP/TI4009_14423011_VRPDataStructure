"""
===============================================================================
 node.py
-------------------------------------------------------------------------------
 Berisi kelas Node: unit data terkecil pada permasalahan CVRP.

 Prinsip OOP yang diajarkan di file ini:
   - ENKAPSULASI : satu titik pada peta punya beberapa data (id, x, y, demand)
                   yang selalu bergerak bersama, sehingga lebih baik dibungkus
                   menjadi satu objek daripada disimpan di beberapa list terpisah.
   - PERILAKU    : objek tidak hanya menyimpan data, tetapi juga punya metode
                   (menghitung jarak, mengecek muat/tidak, dan seterusnya).
===============================================================================
"""

from __future__ import annotations

import math


class Node:
    """
    Merepresentasikan SATU titik pada jaringan CVRP.

    Sebuah node dapat berupa:
      - depot    : titik awal dan akhir semua rute, demand = 0
      - customer : titik yang harus dilayani tepat satu kali, demand > 0

    Atribut
    -------
    id       : int   -> nomor node sesuai file .vrp (1..n)
    x, y     : float -> koordinat kartesian node
    demand   : float -> jumlah permintaan barang pada node tersebut
    is_depot : bool  -> True bila node ini adalah depot

    Catatan implementasi
    --------------------
    `__slots__` membuat Python tidak membuat __dict__ untuk tiap objek, sehingga
    objek Node menjadi jauh lebih hemat memori. Ini relevan untuk metaheuristik:
    pada instance besar, objek Node akan diakses jutaan kali selama iterasi.
    """

    __slots__ = ("id", "x", "y", "demand", "is_depot")

    # =====================================================================
    # CONSTRUCTOR
    # =====================================================================
    def __init__(self, node_id: int, x: float, y: float,
                 demand: float = 0.0, is_depot: bool = False) -> None:
        self.id = int(node_id)
        self.x = float(x)
        self.y = float(y)
        self.demand = float(demand)
        self.is_depot = bool(is_depot)

    # =====================================================================
    # METODE GEOMETRI (PERHITUNGAN JARAK)
    # =====================================================================
    def euclidean_distance(self, other: "Node", rounded: bool = True) -> float:
        """
        Menghitung jarak Euclidean dari node ini ke node lain.
        Sesuai EDGE_WEIGHT_TYPE = EUC_2D pada file instance.

        Parameter
        ---------
        rounded : bool
            True  -> dibulatkan ke integer terdekat, sesuai konvensi TSPLIB.
                     Nilai optimal benchmark (misal 784 untuk A-n32-k5)
                     dihitung memakai pembulatan ini.
            False -> jarak presisi penuh (untuk keperluan analisis).
        """
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx * dx + dy * dy)
        return float(round(distance)) if rounded else distance

    def manhattan_distance(self, other: "Node") -> float:
        """
        Jarak Manhattan (grid). Alternatif bila kasus nyata menggunakan
        jaringan jalan kota yang berpola kotak-kotak.
        """
        return abs(self.x - other.x) + abs(self.y - other.y)

    def coordinates(self) -> tuple:
        """Mengembalikan koordinat node sebagai tuple (x, y)."""
        return (self.x, self.y)

    # =====================================================================
    # METODE PEMERIKSAAN (QUERY)
    # =====================================================================
    def is_customer(self) -> bool:
        """True bila node ini pelanggan, bukan depot."""
        return not self.is_depot

    def fits_in(self, remaining_capacity: float) -> bool:
        """
        Memeriksa apakah demand node ini masih muat pada sisa kapasitas
        kendaraan. Metode ini akan sering dipakai pada heuristik konstruktif.
        """
        return self.demand <= remaining_capacity

    # =====================================================================
    # METODE UTILITAS
    # =====================================================================
    def to_dict(self) -> dict:
        """Mengekspor isi node ke dictionary, berguna untuk logging/debugging."""
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "demand": self.demand,
            "is_depot": self.is_depot,
        }

    def copy(self) -> "Node":
        """Membuat salinan independen dari node ini."""
        return Node(self.id, self.x, self.y, self.demand, self.is_depot)

    # =====================================================================
    # DUNDER METHODS (metode khusus Python)
    # =====================================================================
    def __repr__(self) -> str:
        """Tampilan objek saat dicetak dengan print() atau repr()."""
        tipe = "DEPOT" if self.is_depot else "CUST "
        return (f"Node({self.id:>3d} | {tipe} | x={self.x:7.2f} | "
                f"y={self.y:7.2f} | demand={self.demand:6.2f})")

    def __eq__(self, other) -> bool:
        """Dua node dianggap sama bila id-nya sama."""
        return isinstance(other, Node) and self.id == other.id

    def __hash__(self) -> int:
        """Agar objek Node dapat dipakai sebagai anggota set atau key dict."""
        return hash(self.id)
