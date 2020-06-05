import tkinter, sys
from tkinter import ttk, messagebox
from ambil_data import *


# Method menu pilihan
#===============================================================================================================
def tambah_hapus_tanaman():
    """ Tampilkan frame menu Tambah/Hapus Tanaman."""

    if frm_daftar.winfo_manager() != None:
        frm_daftar.grid_forget()
    frm_tanaman.grid(row=0, column=0)
    

def daftar_tanaman():
    """ Tampilkan frame menu Daftar Tanaman."""

    if frm_tanaman.winfo_manager() != None:
        frm_tanaman.grid_forget()
    frm_daftar.grid(row=0, column=0)


def keluar():
    """ Tutup semua program dan keluar dari aplikasi. """

    raise SystemExit()


# Method buttons pilihan tanaman
#===============================================================================================================
def populate_listbox():
    """ Update data pada listbox."""

    list_tanaman.delete(0, tkinter.END)
    for baris in db.ambil_tanaman():
        list_tanaman.insert(tkinter.END, baris)


def tambah_tanaman():
    """ Tambahkan tanaman dari input user dan tabel sensornya."""
   
    # Jika entry kosong, tampilkan pesan kesalahan    
    if ent_id.get() == '' or ent_lat.get() == '' or ent_lon.get() == '':
        messagebox.showerror('Error', 'Input tidak boleh kosong')
        return
    
    # Jika input salah, id sudah ada/ koordinat bukan bilangan desimal, 
    # tampilkan pesan kesalahan
    try:
        if int(ent_id.get()) < 1:
            raise ValueError
        tanaman = db.ambil_tanaman()
        for id_tree in tanaman:
            if int(ent_id.get()) in id_tree:
                raise TypeError 
        float(ent_lat.get())
        float(ent_lon.get())
    except:
        messagebox.showerror('Error', 'Input salah')
        return

    # Tambahkan satu baris pada tabel tanaman
    db.tambah_tanaman(ent_id.get(), 
              ent_lat.get(),        
              ent_lon.get())

    # Buat tabel sensor tanaman
    for baris in db.ambil_tanaman():
        id_tree = str(baris[0])
        db.buat_tabel_sensor(id_tree)

    # Isi listbox
    list_tanaman.delete(0, tkinter.END)
    list_tanaman.insert(tkinter.END, 
                        ent_id.get(),
                        ent_lat.get(),
                        ent_lon.get())
    populate_listbox()

    # Jalankan thread ambi_data
    # Jika thread sudah berjalan,
    # => hentikan thread, buat thread baru
    thread = threading.active_count()
    if thread == 1:
        global t1
        t1 = Thread(target=ambil_data_gateway)
    else:
        t1.kill()
        t1 = Thread(target=ambil_data_gateway)
    t1.start()


def hapus_tanaman():
    """ Hapus tanaman yang dipilih user pada listbox."""

    # Hentikan program ambil data
    try:
        # Hapus data satu baris pada kedua tabel dari DB
        db.hapus_tanaman(pilihan[0])
        clear_input()
        populate_listbox()
    except NameError:
        pass

    # Jalankan thread ambi_data
    # Jika thread sudah berjalan,
    # => hentikan thread, buat thread baru
    thread = threading.active_count()
    if thread == 1:
        global t1
        t1 = Thread(target=ambil_data_gateway)
    else:
        t1.kill()
        t1 = Thread(target=ambil_data_gateway)    
    t1.start()


def pilih_tanaman(event):
    """ Pilih tanaman dan mengembalikan data baris pilihan tanaman oleh user."""

    try:
        # Tentukan index pilihan pada listbox
        global pilihan
        index = list_tanaman.curselection()[0]
        pilihan = list_tanaman.get(index)
        # Isi entry pada frame dengan data baris
        ent_id.delete(0, tkinter.END)
        ent_id.insert(tkinter.END, pilihan[0])
        koma = pilihan[1].find(',')
        ent_lat.delete(0, tkinter.END)
        ent_lat.insert(tkinter.END, pilihan[1][:koma])
        ent_lon.delete(0, tkinter.END)
        ent_lon.insert(tkinter.END, pilihan[1][koma+1:])
    except IndexError:
        pass


def hapus_data():
    """ Hapus semua baris pada kedua tabel dari DB"""

    # Hentikan program ambil data
    db.hapus_tabel()
    clear_input()
    populate_listbox()
    
    # Hentikan thread ambi_data
    t1.kill()


def clear_input():
    """ Kosongkan entry input user."""

    ent_id.delete(0, tkinter.END)
    ent_lat.delete(0, tkinter.END)
    ent_lon.delete(0, tkinter.END)


# Method buttons pilihan data
#===============================================================================================================
def isi_tabel():
    """ Refresh baris tabel treeview pada frame daftar"""

    tabel.delete(*tabel.get_children())
    for baris in db.ambil_tanaman():
        tabel.insert("", "end", values=baris)


def pilih_data_daftar(event):
    """ Pilih baris tabel data dan ambil data baris pilihan user."""
    
    global tanaman_pilih
    tanaman_pilih = tabel.focus()
    tanaman_pilih = tabel.item(tanaman_pilih)["values"]
    

def grafik_satu_tanaman():
    """ Tampilkan grafik data sensor satu tanaman pilihan user."""

        # Jika data kosong, tampilkan pesan kesalahan
    total = len(db.ambil_tanaman())
    if total == 0:
        messagebox.showerror('Error', 'Data Kosong')
        return

    try:
        # Jika user tidak memilih tanaman,
        # Tampilkan pesan kesalahan
        # Buat window baru
        pilihan = tanaman_pilih
        satu_plot = tkinter.Toplevel(window)
        # Buat widget entry range waktu user
        label = "Range Waktu:\n-- DD/MM/YY,HH/MM --\n17/08/1945,14:52"

        lbl_range = tkinter.Label(satu_plot, text=label).pack(pady=5)

        lbl_awal = tkinter.Label(satu_plot, text="Awal").pack()

        ent_awal = tkinter.Entry(satu_plot)
        ent_awal.pack()

        lbl_akhir = tkinter.Label(satu_plot, text="Akhir").pack()

        ent_akhir = tkinter.Entry(satu_plot)
        ent_akhir.pack()

        # Button tampilkan grafik data, panggil fungsi buat_plot

        btn_tampil = tkinter.Button(satu_plot, 
                                    text="Tampilkan", 
                                    command=lambda: buat_plot(satu_plot, 
                                                            True, 
                                                            pilihan, 
                                                            ent_awal, 
                                                            ent_akhir,
                                                            btn_tampil))
        btn_tampil.pack(pady=10)
        satu_plot.mainloop()

    # Tampilkan pesan kesalahan
    except NameError:
            messagebox.showerror('Error', 'Tidak ada tanaman yang dipilh')
            return
    except SystemExit:
        sys.exit()

def grafik_semua_tanaman():
    """ Tampilkan grafik data sensor overall tanaman."""
    
    # Jika data kosong, tampilkan pesan kesalahan
    total = len(db.ambil_tanaman())
    if total == 0:
        messagebox.showerror('Error', 'Data Kosong')
        return

    # Buat window baru
    semua_plot = tkinter.Toplevel(window)
    # Buat widget entry range waktu user
    label = "Range Waktu:\n-- DD/MM/YY,HH/MM --\n17/08/1945,14:52"
    
    lbl_range = tkinter.Label(semua_plot, text=label).pack(pady=5)
    
    lbl_awal = tkinter.Label(semua_plot, text="Awal").pack()
    
    ent_awal = tkinter.Entry(semua_plot)
    ent_awal.pack()
    
    lbl_akhir = tkinter.Label(semua_plot, text="Akhir").pack()
    
    ent_akhir = tkinter.Entry(semua_plot)
    ent_akhir.pack()
    
    # Button tampilkan grafik data, panggil fungsi buat_plot
    btn_tampil = tkinter.Button(semua_plot, 
                                text="Tampilkan", 
                                command=lambda: buat_plot(semua_plot,
                                                        False, 
                                                        None, 
                                                        ent_awal, 
                                                        ent_akhir,
                                                        btn_tampil))
    btn_tampil.pack(pady=10)
    semua_plot.mainloop()


# Buat window
#===============================================================================================================
window = tkinter.Tk()
window.title("Aplikasi Pemantauan Lahan")
window.geometry('345x475')


# Buat menu dari aplikasi
#===============================================================================================================
menubar = tkinter.Menu(window)
# Menu pilihan
menu_tanaman = tkinter.Menu(menubar, tearoff=0)
# Tempel menu_tanaman pada menubar
menubar.add_cascade(label="Pilihan", menu=menu_tanaman)
# Pilihan-pilihan pada menu tanaman
menu_tanaman.add_command(label="Tambah/Hapus Tanaman", command=tambah_hapus_tanaman)
menu_tanaman.add_separator()
menu_tanaman.add_command(label="Daftar Tanaman", command=daftar_tanaman)
# Menu langsung keluar
menubar.add_command(label="Keluar", command=keluar)
# Informasikan menunya yang mana
window.config(menu=menubar)


# Buat frame
#===============================================================================================================
# Frame tambh/hapus tanaman
frm_tanaman = tkinter.Frame(window, borderwidth=0)
frm_tanaman.grid(row=0, column=0)


# Tempatkan berbagai widget
#===============================================================================================================
# Label Judul
lbl_judul = tkinter.Label(frm_tanaman, text="Tambah/Hapus Tanaman", font=("bold", 10))
lbl_judul.grid(row=0, column=0, columnspan=2, padx=100, pady=5, sticky=tkinter.W)
# Label-Entry nama
lbl_nama = tkinter.Label(frm_tanaman, text="ID Tanaman", font=("bold", 10))
lbl_nama.grid(row=1, column=0, sticky=tkinter.W, padx=30, pady=10)
ent_id = tkinter.Entry(frm_tanaman)
ent_id.grid(row=1, column=1, pady=10, sticky=tkinter.W)
# Label-Entry posisi
lbl_posisi = tkinter.Label(frm_tanaman, text="Lintang-Bujur", font=("bold", 10))
lbl_posisi.grid(row=2, column=0, padx=30, pady=10, sticky=tkinter.W)
ent_lat = tkinter.Entry(frm_tanaman, width=10)
ent_lat.grid(row=2, column=1, columnspan=2, pady=10, sticky=tkinter.W)
ent_lon = tkinter.Entry(frm_tanaman, width=10)
ent_lon.grid(row=2, column=1, padx=60, pady=10, sticky=tkinter.W)
# Buttons
# Button tambah tanaman
btn_tambah = tkinter.Button(frm_tanaman, text="Tambah Tanaman", width=15, command=tambah_tanaman)
btn_tambah.grid(row=3, column=0, padx=30, pady=10, sticky=tkinter.W)
# Button hapus tanaman
btn_hapus = tkinter.Button(frm_tanaman, text="Hapus Tanaman", width=15, command=hapus_tanaman)
btn_hapus.grid(row=3, column=1, padx=10, sticky=tkinter.W)
# Button hapus_data tanaman
btn_hapus_data = tkinter.Button(frm_tanaman, text="Hapus Semua Data", width=15, command=hapus_data)
btn_hapus_data.grid(row=4, column=0, padx=30, pady=10, sticky=tkinter.W)
# Button kosongkan input
btn_input = tkinter.Button(frm_tanaman, text="Kosongkan Entry", width=15, command=clear_input)
btn_input.grid(row=4, column=1, padx=10, sticky=tkinter.W)
# list tanaman (listbox)
list_tanaman = tkinter.Listbox(frm_tanaman, relief=tkinter.RIDGE, height=13, width=45, border=5)
list_tanaman.grid(row=5, column=0, columnspan=3, rowspan=6, pady=1, padx=30, sticky=tkinter.W)
# Pilih bind
list_tanaman.bind('<<ListboxSelect>>', pilih_tanaman)
# Scrollbar
scr_bar = tkinter.Scrollbar(frm_tanaman)
scr_bar.grid(row=5, column=1, padx=30, sticky=tkinter.E)
list_tanaman.configure(yscrollcommand=scr_bar.set)
scr_bar.configure(command=list_tanaman.yview)


# Frame daftar
#===============================================================================================================
frm_daftar = tkinter.Frame(window, relief=tkinter.RIDGE)
# Label Judul
lbl_judul = tkinter.Label(frm_daftar, text="Daftar Tanaman", font=("bold", 10))
lbl_judul.grid(row=0, column=0, columnspan=3, pady=5)
# Widget tabel 
kolom = ("id", "koor", "waktu")
tabel = ttk.Treeview(frm_daftar, selectmode="browse", show="headings", height=18, column=kolom)
tabel.grid(row=1, column=0, sticky=tkinter.W)
tabel.bind("<ButtonRelease-1>", pilih_data_daftar)
# Kolom tabel
tabel.column("id", width=66, anchor='center')
tabel.column("koor", width=125, anchor='center')
tabel.column("waktu", width=151, anchor='center')
tabel.heading("id", text="id_tree")
tabel.heading("koor", text="Lintang-Bujur")
tabel.heading("waktu", text="Waktu Tambah")

# Scrollbar
scrbar_tabel = ttk.Scrollbar(frm_daftar, orient="vertical", command=tabel.yview)
tabel.configure(yscrollcommand=scrbar_tabel.set)
scrbar_tabel.grid(row=1, column=0, sticky=tkinter.E)
# Widget buttons
# Button refresh daftar
btn_refresh = tkinter.Button(frm_daftar, text="Refresh Tabel", height=3, width=15, command=isi_tabel)
btn_refresh.grid(row=2, column=0, columnspan=2, sticky=tkinter.W)
# Button data satu tanaman
btn_satu_tanaman = tkinter.Button(frm_daftar, text="Tampilkan data", height=3, width=15, command=grafik_satu_tanaman)
btn_satu_tanaman.grid(row=2, column=0, padx=115, sticky=tkinter.W)
# Button data semua tanaman
btn_semua_tanaman = tkinter.Button(frm_daftar, text="Tampilkan semua", height=3, width=15, command=grafik_semua_tanaman)
btn_semua_tanaman.grid(row=2, column=0, sticky=tkinter.E)


# Tunggu masukan user
#===============================================================================================================
# Populate data
populate_listbox()
isi_tabel()
window.mainloop()