import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from tkinter import ttk

class AlacaklarPage(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent")
        self.user_id = user_id
        self.setup_ui()
        self.load_alacaklar()

    def setup_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # Başlık
        header = ctk.CTkLabel(main_container, text="💰 Yeni Alacak Ekle", font=ctk.CTkFont(size=26, weight="bold"), text_color="#fff")
        header.pack(pady=(10, 0))

        # --- FİLTRELER ---
        filter_frame = ctk.CTkFrame(main_container, fg_color=("gray90", "gray15"), corner_radius=15)
        filter_frame.pack(pady=(10, 0), padx=20, fill="x")
        # Tarih sıralama
        ctk.CTkLabel(filter_frame, text="Sırala:").grid(row=0, column=0, padx=5, pady=5)
        self.sort_var = ctk.StringVar(value="Artan")
        self.sort_combo = ctk.CTkComboBox(filter_frame, values=["Artan", "Azalan"], variable=self.sort_var, width=100, command=lambda _: self.load_alacaklar())
        self.sort_combo.grid(row=0, column=1, padx=5, pady=5)
        # Tutar aralığı
        ctk.CTkLabel(filter_frame, text="Tutar min:").grid(row=0, column=2, padx=5, pady=5)
        self.tutar_min_entry = ctk.CTkEntry(filter_frame, width=80)
        self.tutar_min_entry.grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkLabel(filter_frame, text="max:").grid(row=0, column=4, padx=5, pady=5)
        self.tutar_max_entry = ctk.CTkEntry(filter_frame, width=80)
        self.tutar_max_entry.grid(row=0, column=5, padx=5, pady=5)
        # Yalnızca ödenmemişler
        self.only_unpaid_var = ctk.BooleanVar(value=True)
        self.only_unpaid_checkbox = ctk.CTkCheckBox(filter_frame, text="Yalnızca ödenmemişler", variable=self.only_unpaid_var, command=self.load_alacaklar)
        self.only_unpaid_checkbox.grid(row=0, column=6, padx=10, pady=5)
        # Filtrele butonu
        filter_btn = ctk.CTkButton(filter_frame, text="Filtrele", command=self.load_alacaklar, width=100)
        filter_btn.grid(row=0, column=7, padx=10, pady=5)

        form = ctk.CTkFrame(main_container, fg_color=("gray90", "gray15"), corner_radius=15)
        form.pack(pady=20, padx=20, fill="x")

        # Kişi seçimi
        kisi_label = ctk.CTkLabel(form, text="Kişi:", font=ctk.CTkFont(size=14, weight="bold"))
        kisi_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.kisi_combobox = ctk.CTkComboBox(form, width=250)
        self.kisi_combobox.grid(row=0, column=1, pady=5, padx=5)
        self.kisi_combobox.set("")
        self.load_kisiler()

        # Tutar
        tutar_label = ctk.CTkLabel(form, text="Tutar (₺):", font=ctk.CTkFont(size=14, weight="bold"))
        tutar_label.grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.tutar_entry = ctk.CTkEntry(form, width=250)
        self.tutar_entry.grid(row=1, column=1, pady=5, padx=5)

        # Açıklama
        aciklama_label = ctk.CTkLabel(form, text="Açıklama:", font=ctk.CTkFont(size=14, weight="bold"))
        aciklama_label.grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.aciklama_entry = ctk.CTkEntry(form, width=250)
        self.aciklama_entry.grid(row=2, column=1, pady=5, padx=5)

        # Vade tarihi
        vade_label = ctk.CTkLabel(form, text="Vade Tarihi:", font=ctk.CTkFont(size=14, weight="bold"))
        vade_label.grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.vade_entry = ctk.CTkEntry(form, width=250, placeholder_text="GG/AA/YYYY")
        self.vade_entry.grid(row=3, column=1, pady=5, padx=5)

        # Kategori
        kategori_label = ctk.CTkLabel(form, text="Kategori:", font=ctk.CTkFont(size=14, weight="bold"))
        kategori_label.grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.kategori_entry = ctk.CTkEntry(form, width=250)
        self.kategori_entry.grid(row=4, column=1, pady=5, padx=5)

        # Para birimi
        parabirimi_label = ctk.CTkLabel(form, text="Para Birimi:", font=ctk.CTkFont(size=14, weight="bold"))
        parabirimi_label.grid(row=5, column=0, sticky="w", pady=5, padx=5)
        self.parabirimi_combobox = ctk.CTkComboBox(form, values=["TL", "USD", "EUR"], width=250)
        self.parabirimi_combobox.set("TL")
        self.parabirimi_combobox.grid(row=5, column=1, pady=5, padx=5)

        # Butonlar
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=15)
        ekle_btn = ctk.CTkButton(btn_frame, text="➕ Kaydet", command=self.add_alacak, width=120, fg_color="#00adb5", hover_color="#11998e", text_color="#fff", font=ctk.CTkFont(size=14, weight="bold"))
        ekle_btn.pack(side="left", padx=10)
        temizle_btn = ctk.CTkButton(btn_frame, text="🧹 Temizle", command=self.clear_form, width=120, fg_color="#393e46", hover_color="#222831", text_color="#fff", font=ctk.CTkFont(size=14, weight="bold"))
        temizle_btn.pack(side="left", padx=10)

        # Liste
        self.tree_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        self.tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def load_kisiler(self):
        try:
            conn = sqlite3.connect("borctakip.db")
            c = conn.cursor()
            c.execute("SELECT id, ad FROM kisiler WHERE kullanici_id = ? ORDER BY ad", (self.user_id,))
            kisiler = c.fetchall()
            conn.close()
            kisi_values = [f"{k[0]} - {k[1]}" for k in kisiler]
            self.kisi_combobox.configure(values=kisi_values)
            if kisi_values:
                self.kisi_combobox.set(kisi_values[0])
            else:
                self.kisi_combobox.set("")
        except Exception as e:
            messagebox.showerror("Hata", f"Kişiler yüklenirken hata oluştu: {str(e)}")

    def add_alacak(self):
        kisi_text = self.kisi_combobox.get()
        if not kisi_text:
            messagebox.showerror("Hata", "Alacak eklemek için önce kişi eklemelisiniz!")
            return
        tutar = self.tutar_entry.get().strip()
        aciklama = self.aciklama_entry.get().strip()
        vade_tarihi = self.vade_entry.get().strip()
        kategori = self.kategori_entry.get().strip()
        parabirimi = self.parabirimi_combobox.get()

        if not kisi_text or not tutar:
            messagebox.showerror("Hata", "Kişi ve tutar zorunludur.")
            return
        try:
            kisi_id = int(kisi_text.split(" - ")[0])
            tutar = float(tutar)
        except Exception:
            messagebox.showerror("Hata", "Kişi seçimi veya tutar formatı hatalı. Lütfen geçerli bir kişi seçin ve tutarı doğru girin.")
            return
        try:
            from datetime import datetime
            conn = sqlite3.connect("borctakip.db")
            c = conn.cursor()
            current_date = datetime.now().strftime("%Y-%m-%d")
            c.execute("INSERT INTO islemler (kullanici_id, kisi_id, tutar, aciklama, vade_tarihi, kategori, parabirimi, odendi, tur, tarih) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'alacak', ?)",
                      (self.user_id, kisi_id, tutar, aciklama, vade_tarihi, kategori, parabirimi, current_date))
            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Alacak başarıyla eklendi!")
            self.clear_form()
            self.load_kisiler()
            self.load_alacaklar()
        except Exception as e:
            messagebox.showerror("Hata", f"Alacak eklenirken hata oluştu: {str(e)}")

    def clear_form(self):
        self.tutar_entry.delete(0, "end")
        self.aciklama_entry.delete(0, "end")
        self.vade_entry.delete(0, "end")
        self.kategori_entry.delete(0, "end")
        self.parabirimi_combobox.set("TL")

    def load_alacaklar(self):
        try:
            conn = sqlite3.connect("borctakip.db")
            c = conn.cursor()
            # Filtreler
            order = "ASC" if self.sort_var.get() == "Artan" else "DESC"
            tutar_min = self.tutar_min_entry.get().strip()
            tutar_max = self.tutar_max_entry.get().strip()
            only_unpaid = self.only_unpaid_var.get()
            query = """
                SELECT i.id, k.ad, i.tutar, i.aciklama, i.vade_tarihi, i.kategori, i.parabirimi, i.odendi
                FROM islemler i
                LEFT JOIN kisiler k ON i.kisi_id = k.id
                WHERE i.kullanici_id = ? AND i.tur='alacak'
            """
            params = [self.user_id]
            if tutar_min:
                query += " AND i.tutar >= ?"
                params.append(float(tutar_min))
            if tutar_max:
                query += " AND i.tutar <= ?"
                params.append(float(tutar_max))
            if only_unpaid:
                query += " AND i.odendi = 0"
            query += f" ORDER BY i.vade_tarihi {order}"
            c.execute(query, params)
            alacaklar = c.fetchall()
            conn.close()
            for widget in self.tree_frame.winfo_children():
                widget.destroy()
            columns = ("ID", "Kişi", "Tutar", "Açıklama", "Vade Tarihi", "Kategori", "Para Birimi", "Durum", "İşlem")
            self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Treeview",
                            background="#f5f5f5",
                            foreground="#222",
                            fieldbackground="#f5f5f5",
                            rowheight=30,
                            font=("Segoe UI", 10))
            style.configure("Treeview.Heading",
                            background="#e0e0e0",
                            foreground="#111",
                            font=("Segoe UI", 11, "bold"))
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, minwidth=80)
            from datetime import datetime
            for alacak in alacaklar:
                durum = "✅ Ödendi" if alacak[7] else ("⏳ Bekliyor" if alacak[4] >= datetime.now().strftime("%Y-%m-%d") else "🔴 Gecikti")
                self.tree.insert("", "end", values=(alacak[0], alacak[1], alacak[2], alacak[3], alacak[4], alacak[5], alacak[6], durum, "Ödendi olarak işaretle" if not alacak[7] else ""))
            self.tree.bind("<Double-1>", self.on_tree_double_click)
            scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=scrollbar.set)
            self.tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        except Exception as e:
            messagebox.showerror("Hata", f"Alacaklar yüklenirken hata oluştu: {str(e)}")

    # Tabloya çift tıklama ile ödendi olarak işaretle

    def on_tree_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        values = self.tree.item(item, "values")
        alacak_id = values[0]
        islem = values[-1]
        if islem == "Ödendi olarak işaretle":
            conn = sqlite3.connect("borctakip.db")
            c = conn.cursor()
            c.execute("UPDATE islemler SET odendi=1 WHERE id=?", (alacak_id,))
            conn.commit()
            conn.close()
            self.load_alacaklar() 