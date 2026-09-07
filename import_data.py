"""
===============================================================================
 import_data.py
-------------------------------------------------------------------------------
 Berisi kelas InstanceReader: bertugas membaca file instance berformat

 Struktur file .vrp yang dibaca:
     NAME, COMMENT, DIMENSION, EDGE_WEIGHT_TYPE, CAPACITY,
     NODE_COORD_SECTION, DEMAND_SECTION, DEPOT_SECTION, EOF
===============================================================================
"""

from __future__ import annotations

import os
import re
from typing import Dict, List

from cvrp_instance import CVRPInstance
from node import Node


class InstanceReader:
    """
    Pembaca file instance CVRP berformat TSPLIB/VRPLIB.

    Pemakaian:
        instance = InstanceReader.read("A/A-n32-k5.vrp")
    """

    # =====================================================================
    # METODE UTAMA
    # =====================================================================
    @staticmethod
    def read(filepath: str, build_matrix: bool = True) -> CVRPInstance:
        """
        Membaca file .vrp dan mengembalikan objek CVRPInstance yang sudah terisi.

        Parameter
        ---------
        filepath     : path lengkap menuju file .vrp
        build_matrix : bila True, matriks jarak langsung dibangun setelah
                       seluruh node terbentuk.
        """
        # ---- Langkah 0 : pastikan file ada ------------------------------
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"File instance tidak ditemukan:\n  {filepath}\n"
                f"Pastikan file .vrp berada di dalam folder 'A'."
            )

        instance = CVRPInstance()

        # ---- Penampung sementara hasil pembacaan ------------------------
        coords: Dict[int, tuple] = {}
        demands: Dict[int, float] = {}
        depots: List[int] = []
        dimension = 0
        section = None          # penanda section yang sedang dibaca

        # ---- Langkah 1 : baca file baris demi baris ---------------------
        with open(filepath, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue

                upper = line.upper()

                # --- Deteksi pergantian section ---------------------------
                if upper.startswith("NODE_COORD_SECTION"):
                    section = "COORD"
                    continue
                if upper.startswith("DEMAND_SECTION"):
                    section = "DEMAND"
                    continue
                if upper.startswith("DEPOT_SECTION"):
                    section = "DEPOT"
                    continue
                if upper.startswith("EOF"):
                    break

                # --- Bagian header, berformat "KEY : VALUE" ---------------
                if ":" in line and section is None:
                    InstanceReader._parse_header(line, instance)
                    if line.split(":", 1)[0].strip().upper() == "DIMENSION":
                        dimension = int(line.split(":", 1)[1].strip())
                    continue

                # --- Bagian isi section -----------------------------------
                parts = line.split()

                if section == "COORD":
                    node_id = int(parts[0])
                    coords[node_id] = (float(parts[1]), float(parts[2]))

                elif section == "DEMAND":
                    node_id = int(parts[0])
                    demands[node_id] = float(parts[1])

                elif section == "DEPOT":
                    nilai = int(parts[0])
                    if nilai == -1:
                        section = None      # tanda akhir DEPOT_SECTION
                    else:
                        depots.append(nilai)

        # ---- Langkah 2 : tentukan depot ---------------------------------
        instance.depot_id = depots[0] if depots else 1

        # ---- Langkah 3 : bentuk objek Node ------------------------------
        for node_id in sorted(coords.keys()):
            x, y = coords[node_id]
            instance.add_node(
                Node(
                    node_id=node_id,
                    x=x,
                    y=y,
                    demand=demands.get(node_id, 0.0),
                    is_depot=(node_id == instance.depot_id),
                )
            )

        # ---- Langkah 4 : validasi ---------------------------------------
        InstanceReader._validate(instance, dimension, coords, demands)

        # ---- Langkah 5 : tentukan jumlah kendaraan ----------------------
        if instance.num_vehicles == 0:
            instance.num_vehicles = InstanceReader._parse_num_vehicles(instance)

        # ---- Langkah 6 : bangun matriks jarak ---------------------------
        if build_matrix:
            instance.build_distance_matrix()

        return instance

    # =====================================================================
    # METODE PEMBANTU (helper)
    # =====================================================================
    @staticmethod
    def _parse_header(line: str, instance: CVRPInstance) -> None:
        """Mengurai satu baris header berformat 'KEY : VALUE'."""
        key, value = line.split(":", 1)
        key, value = key.strip().upper(), value.strip()

        if key == "NAME":
            instance.name = value
        elif key == "COMMENT":
            instance.comment = value
        elif key == "CAPACITY":
            instance.capacity = float(value)
        elif key == "EDGE_WEIGHT_TYPE":
            instance.edge_weight_type = value
        elif key in ("VEHICLES", "TRUCKS", "NO_OF_TRUCKS"):
            instance.num_vehicles = int(value)

    @staticmethod
    def _parse_num_vehicles(instance: CVRPInstance) -> int:
        """
        Menentukan jumlah kendaraan bila tidak tertulis eksplisit pada file.

        Urutan prioritas:
          1. pola '-kX' pada NAME, contoh: A-n32-k5  -> 5 kendaraan
          2. angka pada COMMENT, contoh: 'No of trucks: 5'
          3. batas bawah teoritis ceil(total demand / kapasitas)
        """
        cocok = re.search(r"-k(\d+)", instance.name, flags=re.IGNORECASE)
        if cocok:
            return int(cocok.group(1))

        cocok = re.search(r"(?:trucks?|vehicles?)\s*[:=]?\s*(\d+)",
                          instance.comment, flags=re.IGNORECASE)
        if cocok:
            return int(cocok.group(1))

        return instance.min_vehicles_required()

    @staticmethod
    def _validate(instance: CVRPInstance, dimension: int,
                  coords: dict, demands: dict) -> None:
        """
        Memeriksa konsistensi data hasil pembacaan.
        Kesalahan data sebaiknya terdeteksi di sini, bukan nanti saat
        algoritma sudah berjalan ratusan iterasi.
        """
        if not coords:
            raise ValueError("NODE_COORD_SECTION kosong atau gagal dibaca.")

        if dimension and dimension != len(instance.nodes):
            raise ValueError(
                f"DIMENSION={dimension} tidak sama dengan jumlah node "
                f"yang terbaca ({len(instance.nodes)})."
            )

        selisih = set(coords.keys()) - set(demands.keys())
        if selisih:
            raise ValueError(f"Node berikut tidak memiliki demand: {sorted(selisih)}")

        if instance.capacity <= 0:
            raise ValueError("CAPACITY tidak terbaca atau bernilai tidak valid.")

        if not instance.has_node(instance.depot_id):
            raise ValueError(f"Depot id={instance.depot_id} tidak ada pada daftar node.")

    # =====================================================================
    # PENCETAKAN PROSES IMPORT
    # =====================================================================
    @staticmethod
    def print_import_report(instance: CVRPInstance, filepath: str) -> None:
        """Mencetak laporan singkat keberhasilan proses import."""
        print("=" * 70)
        print(" LAPORAN IMPORT DATA")
        print("=" * 70)
        print(f" File sumber        : {filepath}")
        print(f" Status             : BERHASIL")
        print(f" Objek terbentuk    : {instance.dimension} objek Node")
        print(f"                      1 depot + {len(instance.customers)} pelanggan")
        print(f" Matriks jarak      : "
              f"{'sudah dibangun' if instance.distance_matrix else 'belum dibangun'} "
              f"({instance.dimension} x {instance.dimension})")
        print("=" * 70 + "\n")
