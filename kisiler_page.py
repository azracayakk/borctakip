import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from tkinter import ttk

class KisilerPage(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent")
        self.user_id = user_id
        self.setup_ui()
        self.load_kisiler()

    def setup_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # Başlık
        header = ctk.CTkLabel(main_container, text="Kişiler Yönetimi", font=ctk.CTkFont(size=22, weight="bold"))
        header.pack(pady=(10, 0))

        # Yatay ana frame (arama+form ve tablo yan yana)
        horizontal_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        horizontal_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Sol: Arama ve Form
        left_frame = ctk.CTkFrame(horizontal_frame, fg_color=("gray90", "gray15"), corner_radius=15)
        left_frame.pack(side="left", fill="y", padx=(0, 20), pady=0)

        # Arama kutusu
        search_label = ctk.CTkLabel(left_frame, text="Ara:", font=ctk.CTkFont(size=14, weight="bold"))
        search_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.search_entry = ctk.CTkEntry(left_frame, width=200, placeholder_text="isim, telefon veya email ile ara...")
        self.search_entry.grid(row=0, column=1, pady=5, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_kisiler)
        search_btn = ctk.CTkButton(left_frame, text="Ara", command=self.search_kisiler, width=80)
        search_btn.grid(row=0, column=2, padx=5, pady=5)

        # Form alanları
        ad_label = ctk.CTkLabel(left_frame, text="Ad Soyad:", font=ctk.CTkFont(size=14, weight="bold"))
        ad_label.grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.ad_entry = ctk.CTkEntry(left_frame, width=200)
        self.ad_entry.grid(row=1, column=1, pady=5, padx=5, columnspan=2)
        telefon_label = ctk.CTkLabel(left_frame, text="Telefon:", font=ctk.CTkFont(size=14, weight="bold"))
        telefon_label.grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.telefon_entry = ctk.CTkEntry(left_frame, width=200)
        self.telefon_entry.grid(row=2, column=1, pady=5, padx=5, columnspan=2)
        email_label = ctk.CTkLabel(left_frame, text="Email:", font=ctk.CTkFont(size=14, weight="bold"))
        email_label.grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.email_entry = ctk.CTkEntry(left_frame, width=200)
        self.email_entry.grid(row=3, column=1, pady=5, padx=5, columnspan=2)
        adres_label = ctk.CTkLabel(left_frame, text="Adres:", font=ctk.CTkFont(size=14, weight="bold"))
        adres_label.grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.adres_entry = ctk.CTkEntry(left_frame, width=200)
        self.adres_entry.grid(row=4, column=1, pady=5, padx=5, columnspan=2)
        notlar_label = ctk.CTkLabel(left_frame, text="Notlar:", font=ctk.CTkFont(size=14, weight="bold"))
        notlar_label.grid(row=5, column=0, sticky="w", pady=5, padx=5)
        self.notlar_entry = ctk.CTkEntry(left_frame, width=200)
        self.notlar_entry.grid(row=5, column=1, pady=5, padx=5, columnspan=2)
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=3, pady=15)
        ekle_btn = ctk.CTkButton(btn_frame, text="Kişi Ekle", command=self.add_kisi, width=100)
        ekle_btn.pack(side="left", padx=10)
        temizle_btn = ctk.CTkButton(btn_frame, text="Temizle", command=self.clear_form, width=100, fg_color="gray")
        temizle_btn.pack(side="left", padx=10)

        # Sağ: Kişi tablosu
        self.tree_frame = ctk.CTkFrame(horizontal_frame, fg_color="transparent")
        self.tree_frame.pack(side="left", fill="both", expand=True)

    def add_kisi(self):
        ad = self.ad_entry.get().strip()
        telefon = self.telefon_entry.get().strip()
        email = self.email_entry.get().strip()
        adres = self.adres_entry.get().strip()
        notlar = self.notlar_entry.get().strip()
        if not ad:
            messagebox.showerror("Hata", "Ad alanı boş olamaz!")
            return
        try:
            conn = sqlite3.connect("borctakip.db")
            c = conn.cursor()
            c.execute("INSERT INTO kisiler (kullanici_id, ad, telefon, email, adres, notlar) VALUES (?, ?, ?, ?, ?, ?)",
                      (self.user_id, ad, telefon, email, adres, notlar))
            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Kişi başarıyla eklendi!")
            self.clear_form()
            self.load_kisiler()
        except Exception as e:
            messagebox.showerror("Hata", f"Kişi eklenirken hata oluştu: {str(e)}")

    def clear_form(self):
        self.ad_entry.delete(0, "end")
        self.telefon_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.adres_entry.delete(0, "end")
        self.notlar_entry.delete(0, "end")

    def load_kisiler(self):
        try:
            search_term = self.search_entry.get().strip().lower() if hasattr(self, 'search_entry') else ''
            conn = sqlite3.connect("borctakip.db")
            c = conn.cursor()
            if search_term:
                c.execute("SELECT * FROM kisiler WHERE kullanici_id = ? AND (LOWER(ad) LIKE ? OR LOWER(telefon) LIKE ? OR LOWER(email) LIKE ?) ORDER BY ad", (self.user_id, f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            else:
                c.execute("SELECT * FROM kisiler WHERE kullanici_id = ? ORDER BY ad", (self.user_id,))
            kisiler = c.fetchall()
            conn.close()
            for widget in self.tree_frame.winfo_children():
                widget.destroy()
            if not kisiler:
                no_data_label = ctk.CTkLabel(self.tree_frame, text="Henüz kişi eklenmemiş", font=ctk.CTkFont(size=16, weight="bold"))
                no_data_label.pack(expand=True)
                return
            columns = ("ID", "Ad", "Telefon", "Email", "Adres", "Notlar")
            self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=18)
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Treeview",
                            background="#f5f5f5",
                            foreground="#222",
                            fieldbackground="#f5f5f5",
                            rowheight=28,
                            font=("Segoe UI", 10))
            style.configure("Treeview.Heading",
                            background="#e0e0e0",
                            foreground="#111",
                            font=("Segoe UI", 11, "bold"))
            column_widths = {
                "ID": 60,
                "Ad": 150,
                "Telefon": 120,
                "Email": 200,
                "Adres": 250,
                "Notlar": 200
            }
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=column_widths.get(col, 150), minwidth=80)
            for kisi in kisiler:
                values = [str(val) if val is not None else "" for val in kisi]
                self.tree.insert("", "end", values=values)
            scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=scrollbar.set)
            self.tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        except Exception as e:
            messagebox.showerror("Hata", f"Kişiler yüklenirken hata oluştu: {str(e)}")

    def search_kisiler(self, event=None):
        self.load_kisiler() 