import sqlite3, tkinter, json, datetime, time
import sys, threading, trace
from tkinter import messagebox
from urllib.request import urlopen
from matplotlib import pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Kelas Database
#===============================================================================================================
class Database:
    """ Merepresentasikan sebuah database. """

    def __init__(self, db):
        """ Default constructor. """

        # Buat atribut tabel tanaman
        self.koneksi = sqlite3.connect(db)
        self.koneksi_threading = sqlite3.connect(db, check_same_thread = False)        
        self.cursor = self.koneksi.cursor()
        self.cursor_threading = self.koneksi_threading.cursor()
        sql =  """CREATE TABLE IF NOT EXISTS tanaman(
                    id_tree INTEGER,
                    koordinat TEXT,
                    waktu TEXT);"""
        self.cursor.execute(sql)
        self.koneksi.commit()       


    def tambah_tanaman(self, id, lat, lon):
        """ Tambah data input user pada tabel tanaman. """

        # Ambil tanggal waktu RTC
        tanggal = datetime.datetime.today().strftime('%a, %d %b %Y %H:%M')
        tanggal = str(tanggal)

        sql = """INSERT INTO tanaman VALUES (?, ?, ?)"""
        self.cursor.execute(sql, (id, f"{lat},{lon}", tanggal))
        self.koneksi.commit()


    def hapus_tanaman(self, id):
        """ Hapus satu baris pada tabel tanaman dan tabel sensornya
            dengan id_tree pilihan user.
        """
        
        # Hapus satu baris dari tabel tanaman
        sql = """DELETE FROM tanaman WHERE id_tree=?"""
        self.cursor.execute(sql, (id,))
        self.koneksi.commit()
        # Hapus tabel sensor tanamannya
        sql = """DROP TABLE IF EXISTS '%s';""" % id 
        self.cursor.execute(sql)
     

    def ambil_tanaman(self):
        """ Ambil data semua tanaman di tabel tanaman. """
        
        sql = """SELECT * FROM tanaman"""
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        return data

    
    def hapus_tabel(self):
        """ Hapus semua baris pada kedua tabel dari DB. """
        
        # Hapus semua tabel sensor tanaman
        for baris in self.ambil_tanaman():
            id_tree = str(baris[0])
            sql = """DROP TABLE IF EXISTS '%s';""" % id_tree 
            self.cursor.execute(sql)
        # Hapus tabel tanaman
        sql = """DROP TABLE IF EXISTS tanaman;""" 
        self.cursor.execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS tanaman(
                    id_tree INTEGER,
                    koordinat TEXT,
                    waktu TEXT);"""
        self.cursor.execute(sql)
    

    def buat_tabel_sensor(self, id_tree):
        """ Buat tabel sensor tiap tanaman. """

        sql =  """CREATE TABLE IF NOT EXISTS '%s'(
                    waktu TEXT,
                    sensor_type_0 REAL,
                    sensor_type_1 REAL,
                    sensor_type_2 REAL,
                    sensor_type_3 REAL,
                    sensor_type_4 REAL,
                    sensor_type_5 REAL,
                    sensor_type_6 REAL,
                    sensor_type_7 REAL,
                    sensor_type_8 REAL,
                    sensor_type_9 REAL)""" % id_tree
        self.cursor.execute(sql)
        self.koneksi.commit()        


    def threading_ambil_tanaman(self):
        """ Ambil data semua tanaman di tabel tanaman. """
        
        sql = """SELECT * FROM tanaman"""
        self.cursor_threading.execute(sql)
        data = self.cursor_threading.fetchall()
        return data


    def tambah_data_sensor(self, data):
        """ Tambah data input user pada tabel sensor. """

        id_tree = str(data["id_tree"])

        sql = """INSERT INTO '%s' 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""" % id_tree
        self.cursor_threading.execute(sql,(data["waktu"], 
                                        data["nilai"][0],
                                        data["nilai"][1],
                                        data["nilai"][2],
                                        data["nilai"][3],
                                        data["nilai"][4],
                                        data["nilai"][5],
                                        data["nilai"][6],
                                        data["nilai"][7],
                                        data["nilai"][8],
                                        data["nilai"][9]))
        self.koneksi_threading.commit()


    def ambil_data_sensor(self, tanaman):
        """ Ambil data semua tanaman di tabel sensor. """
        
        id_tree = str(tanaman[0])
        sql = """SELECT * FROM '%s'""" % id_tree
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        return data


    def ambil_baris_sensor(self, tanaman, waktu):
        """ Ambil data semua tanaman di tabel sensor. """
        while True:
            id_tree = str(tanaman[0])
            sql = """SELECT * FROM '%s' WHERE waktu = '%s'""" % (id_tree, waktu)
            self.cursor.execute(sql)
            data = self.cursor.fetchone()
            if data != None:
                return data
                break
            waktu = int(waktu) - 1
            waktu = str(waktu)


    def cari_tabel_min(self):
        """ Buat tabel rata-rata data sensor semua tanaman. """

        # Hitung rata-rata data tiap sensor semua tanaman
        total_baris = {}
        for baris in self.ambil_tanaman():
            id_tree = str(baris[0])
            sql = """SELECT * FROM '%s'""" % id_tree
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            banyak_data = len(data)
            total_baris[id_tree] = banyak_data
        min_baris = min([total_baris[key] for key in total_baris])
        tabel = [key for (key, nilai) in total_baris.items() if nilai == min_baris]
        return tabel

    def __del__(self):
        """ Tutup koneksi database. """
        
        self.koneksi.close()
        self.koneksi_threading.close()


class Thread(threading.Thread): 
    """ Merepresentasikan sebuah thread. """

    """ Default constructor. """
    def __init__(self, *args, **keywords): 
        threading.Thread.__init__(self, *args, **keywords) 
        # Atribut thread
        self.killed = False
        self.daemon = True
  
    def start(self): 
        """ Jalankan thread. """

        self.__run_backup = self.run 
        self.run = self.__run       
        threading.Thread.start(self) 
  
    def __run(self):
        sys.settrace(self.globaltrace) 
        self.__run_backup() 
        self.run = self.__run_backup 
  
    def globaltrace(self, frame, event, arg):
        if event == 'call': 
          return self.localtrace 
        else: 
          return None
      
    def localtrace(self, frame, event, arg):

        if self.killed: 
          if event == 'line':
            raise SystemExit()
        return self.localtrace 
      
    def kill(self):
        """ Berikan sinyal stop pada thread. """ 

        self.killed = True


# Program ambil data
#==================================================================================================================
def konversi_waktu(tanggal, format):
    """ Konversi format tanggal. """

    # Konversi format tanggal data dari gateway 
    if format == True:
        waktu = tanggal.strip().replace(" ","")
        waktu = datetime.datetime.strptime(waktu, '%a,%d%b%Y%H:%M')
        waktu = waktu.strftime('%Y%m%d%H%M')
        return waktu

    # Konversi format tanggal input user
    else:
        waktu = tanggal.strip().replace(" ","")
        waktu = datetime.datetime.strptime(waktu, '%d/%m/%Y,%H:%M')
        waktu = waktu.strftime('%Y%m%d%H%M')
        return waktu


def konversi_si(sensor_type, nilai):
    """ Konversi satuan data dari gateway. """
    
    # Suhu udara
    if sensor_type == 0:
        suhu_udara = nilai
        if not 15 < suhu_udara < 40:
            if suhu_udara > 40:
                suhu_udara = suhu_udara - 40 + 20
            else:
                suhu_udara = suhu_udara + 15
        return suhu_udara

    # Kelembaban udara
    elif sensor_type == 1:
        udara_lembab = nilai / 60 * 100
        return udara_lembab
    
    # Curah hujan
    elif sensor_type == 2:
        curah_hujan = nilai * 5
        return curah_hujan

    # UV level
    elif sensor_type == 3:
        uv_index = nilai
        if 0 < uv_index <= 5:
            uv_index = 1
        elif 5 < uv_index <= 10:
            uv_index = 2
        elif 10 < uv_index <= 15:
            uv_index = 3
        elif 15 < uv_index <= 20:
            uv_index = 4
        elif 20 < uv_index <= 25:
            uv_index = 5
        elif 25 < uv_index <= 30:
            uv_index = 6
        elif 30 < uv_index <= 35:
            uv_index = 7
        elif 35 < uv_index <= 40:
            uv_index = 8
        elif 40 < uv_index <= 45:
            uv_index = 9
        elif 50 < uv_index <= 55:
            uv_index = 10
        else:
            uv_index = 11
        return uv_index

    # Suhu tanah
    elif sensor_type == 4:
        suhu_tanah = nilai
        if not 10 < suhu_tanah < 30:
            if suhu_tanah > 40:
                suhu_tanah = suhu_tanah - 30 + 20
            else:
                suhu_tanah = suhu_tanah + 10
        return suhu_tanah

    # Kelembaban tanah
    elif sensor_type == 5:
        tanah_lembab = nilai / 60 * 80
        return tanah_lembab

    # pH tanah
    elif sensor_type == 6:
        skala_ph = nilai
        if 0 < skala_ph <= 4:
            skala_ph = 1
        elif 4 < skala_ph <= 8:
            skala_ph = 2
        elif 8 < skala_ph <= 12:
            skala_ph = 3
        elif 12 < skala_ph <= 16:
            skala_ph = 4
        elif 16 < skala_ph <= 20:
            skala_ph = 5
        elif 20 < skala_ph <= 24:
            skala_ph = 6
        elif 24 < skala_ph <= 28:
            skala_ph = 7
        elif 28 < skala_ph <= 32:
            skala_ph = 8
        elif 32 < skala_ph <= 36:
            skala_ph = 9
        elif 36 < skala_ph <= 40:
            skala_ph = 10
        elif 40 < skala_ph <= 44:
            skala_ph = 11
        elif 44 < skala_ph <= 48:
            skala_ph = 12
        elif 48 < skala_ph <= 52:
            skala_ph = 13
        else:
            skala_ph = 14
        return skala_ph

    # Kadar N, P, dan K dalam tanah
    elif sensor_type == 7:
        kadar_n = nilai + 90
        return kadar_n
    elif sensor_type == 8:
        kadar_p = nilai + 50
        return kadar_p
    else:
        kadar_k = nilai + 30
        return kadar_k
        

def ambil_data_gateway():
    """
    - Ambil data 10 sensor pada tiap tanaman di DB.
    - Tanaman telah ditambahkan pada tabel tanaman.
    - Ambil data => Gateway IoT dengan API khusus.
    - Ambil tiap satu menit
    """

    while True: 
        data = db.threading_ambil_tanaman()
        print('\n',data)
        # Ambil data hingga aplikasi berhenti
        for baris in data:
            # Ambil data id_tree per baris
            id_tree = baris[0]
            print('\nid_tree: ', id_tree)

            # Buat dictionary tampung data sensor 
            data_sensor = {"id_tree":id_tree, "waktu":"", "nilai":{}}
            
            for sensor_type in range(10):
                # URL API per sensor 
                alamat = f"https://belajar-python-unsyiah.an.r.appspot.com/sensor/read?npm=1904105010025&id_tree={id_tree}&sensor_type={sensor_type}"
                # Buka koneksi ke URL
                url = urlopen(alamat)
        
                # Ambil/baca dokumen
                dokumen = url.read().decode("utf-8")
                # Memuat dokumen json pada data
                data_API = json.loads(dokumen)
                print(data_API)

                # Ambil data waktu, isi pada dictionary
                waktu = data_API["when"][:-7] 
                waktu = konversi_waktu(waktu, True)
                data_sensor["waktu"] = waktu

                # Ambil data nilai, isi pada dictionary
                data_sensor["nilai"][sensor_type] = data_API["value"]

            # Panggil method untuk tambahkan data pada tabel sensor
            print(data_sensor)
            db.tambah_data_sensor(data_sensor)
        time.sleep(60)


def buat_plot(window, satu, pilihan, awal, akhir, button):
    """ Buat plot dari DB."""

    # Ambil input range dari user
    # Range awal dan akhir
    try:
        awal = awal.get()
        awal = konversi_waktu(awal, False)
        awal = int(awal)
        akhir = akhir.get()
        akhir = konversi_waktu(akhir, False)
        akhir = int(akhir)

        # Buat figure grafik
        fig = pyplot.Figure(figsize=(10,6), dpi=80)
        grafik = fig.add_subplot(111)

        # Jika user pilih grafik_satu_tanaman
        # Buat grafik data 10 sensor satu tanaman
        if satu == True:
            # Ambil data sensor satu tanaman
            # Tanaman pilihan user pada tabel daftar tanaman
            data = db.ambil_data_sensor(pilihan)
            
            # Ambil range waktu data sensor
            sumbu_x = []
            for baris in data:  
                waktu = int(baris[0])
                # Jika waktu berada pada range waktu input user, 
                # tambahkan pada sumbu x
                if waktu >= awal and waktu <= akhir:
                    sumbu_x.append(waktu)
            print("x: ", len(sumbu_x), sumbu_x)

            # Jika tidak ada waktu yang sesuai range,
            # raise kesalahan
            if len(sumbu_x) == 0 or len(sumbu_x) == 1:
                raise ValueError

            # Matikan button
            button["state"] = "disabled"

            # Buat grafik garis
            # Ada 10 plot => 10 sensor pada satu tanaman
            warna = ['k','r','b','g','y','m','c','tab:orange','tab:brown','lime']
            for sensor in range(10):
                sumbu_y = []
                for waktu in sumbu_x:
                    baris = db.ambil_baris_sensor(pilihan, str(waktu))
                    nilai = baris[sensor+1]
                    nilai = round(nilai, 2)
                    nilai = konversi_si(sensor, nilai)
                    sumbu_y.append(nilai)
                xi = [n+1 for n in range(len(sumbu_x))]
                grafik.plot(xi, sumbu_y, color=warna[sensor])

            # Buat judul grafik, berdasrakan nama tanaman input user
            grafik.set_title(f'Data Sensor Tanaman {pilihan[0]}', pad=15)

        # Jika user pilih grafik_semua_tanaman
        # Buat grafik data rata-rata 10 sensor semua tanaman
        else:
            # Ambil id_tree semua tanaman
            # Hitung jumlah tanaman
            tabel_min = db.cari_tabel_min()
            data = db.ambil_data_sensor(tabel_min)
            
            # Ambil range waktu data sensor
            sumbu_x = []
            for baris in data:  
                waktu = int(baris[0])
                # Jika waktu berada pada range waktu input user, 
                # tambahkan pada sumbu x
                if waktu >= awal and waktu <= akhir:
                    sumbu_x.append(waktu)

            # Jika tidak ada waktu yang sesuai range,
            # raise kesalahan
            if len(sumbu_x) < 2:
                raise ValueError

            # Matikan button
            button["state"] = "disabled"

            # Buat grafik garis
            # Ada 10 plot => 10 sensor pada semua tanaman
            # Rata-rata bacaan semua tanaman pada tiap sensor
            warna = ['k','r','b','g','y','m','c','tab:orange','tab:brown','lime']
            for sensor in range(10):
                sumbu_y = []
                for waktu in sumbu_x:
                    total = 0
                    banyak = 0
                    for tanaman in db.ambil_tanaman():
                        baris = db.ambil_baris_sensor(tanaman, str(waktu))
                        nilai = baris[sensor+1]
                        nilai = round(nilai, 2)
                        total += nilai
                        banyak += 1
                    rata2 = total / banyak
                    rata2 = round(rata2,2)
                    rata2 = konversi_si(sensor, rata2)
                    sumbu_y.append(rata2)
                xi = [n+1 for n in range(len(sumbu_x))]
                grafik.plot(xi, sumbu_y, color=warna[sensor])

            # Buat judul grafik, berdasrakan nama tanaman input user
            grafik.set_title(f'Data Rata-Rata Sensor Semua Tanaman', pad=15)
    
    # Tampilkan pesan kesalahan 
    except ValueError:
        pesan = "Range waktu tidak ditemukan/input kosong"
        messagebox.showerror('Error', pesan)
        return

    # Kecilkan ketinggian grafik 10%
    bbox = grafik.get_position()
    grafik.set_position([0.08, 
                        0.1, 
                        bbox.width * 0.9, 
                        bbox.height + bbox.height * 0.05])

    # Tempatkan legend grafik
    # Di kanan grafik, ada 10 warna legend 
    grafik.legend(['Suhu Udara (°C)', 
                'Kelembabaan\nUdara (%)',
                'Curah Hujan (mm)',
                'UV Level (Indeks UV)',
                'Suhu Tanah (°C)',
                'Kelembaban\nTanah (%)',
                'pH Tanah (Skala pH)',
                'Kadar N (g kg-1)',
                'Kadar P (g kg-1)',
                'Kadar K (g kg-1)'],
                loc="center left",
                bbox_to_anchor=(1, 0.5),
                fancybox=True,
                shadow=True,
                labelspacing=1.5
                )

    # Tempel label sumbu
    grafik.set_xlabel("Waktu Bacaan (menit)")
    grafik.set_ylabel("Nilai Baca")

    # Tempel figure pada window    
    canvas = FigureCanvasTkAgg(fig, window)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Button keluar
    # Hapus grafik, tutup window
    btn_keluar = tkinter.Button(window, text="Tutup", command= lambda: window.destroy())
    btn_keluar.pack(pady=5)
    window.mainloop()


# Buat DB
#==================================================================================================================
# nama : 'kebun.db'
# Dua tabel => tanaman dan sensor
db = Database('kebun.db')

# Buat thread program ambil_data
#==================================================================================================================
# Hanya ada 2 thread yang berjalan pada aplikasi
#   => Thread GUI dan ambil_data
t1 = Thread(target=ambil_data_gateway)