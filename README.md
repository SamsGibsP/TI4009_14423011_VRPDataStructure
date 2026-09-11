# TI4009_14423011_Minggu3

# Capacitated Vehicle Routing Problem (CVRP) - Data Structure & Solver

Implementasi struktur data berbasis **Object-Oriented Programming (OOP)** dan algoritma optimasi untuk menyelesaikan permasalahan *Capacitated Vehicle Routing Problem* (CVRP) dengan format benchmark standar **TSPLIB / VRPLIB** (Augerat et al., Set A).

---

## 📌 Fitur Utama

- **Struktur Data Efisien & Hemat Memori**:
  - Menggunakan `__slots__` pada kelas `Node` dan `Route` untuk efisiensi alokasi memori.
  - Representasi ganda (`List` untuk iterasi berurutan dan `Dict` untuk pencarian $O(1)$).
  - *Precomputed distance matrix* simetris $O(1)$ berbasis pembulatan Euclidean standar TSPLIB (reproduksi nilai optimal benchmark 784).
- **Pemodelan Berorientasi Objek (OOP)**:
  - Pembagian tanggung jawab modular (*Single Responsibility Principle*).
  - Representasi entitas: `Node`, `CVRPInstance`, `Route`, `Solution`, dan `CVRPSolver`.
- **Algoritma Optimasi**:
  - **Konstruksi Awal**: *Clarke-Wright Savings Algorithm*.
  - **Peningkatan Solusi (*Local Search*)**: Operator *2-Opt* (intra-rute) dan *Relocate* (inter-rute).
- **Validasi Kelayakan (*Feasibility Check*)**:
  - Kapasitas muatan kendaraan ($\sum \text{demand} \le \text{capacity}$).
  - Batasan jumlah armada kendaraan.
  - Integritas kunjungan pelanggan (setiap *customer* dikunjungi tepat satu kali).

---

## 📂 Struktur Direktori

```text
project/
├── A/
│   └── A-n32-k5.vrp       # File instance dataset benchmark (Set A)
├── node.py                # Kelas Node (lokasi, demand, geometri)
├── cvrp_instance.py       # Kelas CVRPInstance (pengelola instance & matriks jarak)
├── import_data.py         # Kelas InstanceReader (parser file .vrp)
├── solution.py            # Kelas Route & Solution (representasi & evaluasi solusi)
├── cvrp_solver.py         # Kelas CVRPSolver (Clarke-Wright Savings + Local Search)
├── main.py                # Titik masuk eksekusi program
├── .gitignore             # Pengabaian cache Python (__pycache__) & OS artifacts
└── README.md              # Dokumentasi proyek
