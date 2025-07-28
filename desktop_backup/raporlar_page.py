import customtkinter as ctk
import sqlite3
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class RaporlarPage(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent")
        self.user_id = user_id
        self.setup_ui()
        self.rapor_guncelle()

    def setup_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        header = ctk.CTkLabel(main_container, text="📊 Raporlar & Grafikler", font=ctk.CTkFont(size=26, weight="bold"), text_color="#fff")
        header.pack(pady=(10, 0))
        self.grafikler_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        self.grafikler_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        guncelle_btn = ctk.CTkButton(main_container, text="🔄 Raporları Güncelle", command=self.rapor_guncelle, width=180, fg_color="#00adb5", hover_color="#11998e", text_color="#fff", font=ctk.CTkFont(size=14, weight="bold"))
        guncelle_btn.pack(pady=5)

    def rapor_guncelle(self):
        for widget in self.grafikler_frame.winfo_children():
            widget.destroy()
        conn = sqlite3.connect("borctakip.db")
        cursor = conn.cursor()
        # Toplam borç/alacak
        cursor.execute("SELECT SUM(tutar) FROM islemler WHERE kullanici_id = ? AND tur = 'borc'", (self.user_id,))
        toplam_borc = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(tutar) FROM islemler WHERE kullanici_id = ? AND tur = 'alacak'", (self.user_id,))
        toplam_alacak = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(tutar) FROM islemler WHERE kullanici_id = ? AND tur = 'borc' AND odendi=0", (self.user_id,))
        odemeyen_borc = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(tutar) FROM islemler WHERE kullanici_id = ? AND tur = 'alacak' AND odendi=0", (self.user_id,))
        odemeyen_alacak = cursor.fetchone()[0] or 0
        # Pasta grafik: Toplam borç/alacak ve ödenmemiş borç/alacak
        fig, axs = plt.subplots(1, 2, figsize=(6, 3))
        fig.subplots_adjust(wspace=0.5)
        if toplam_borc > 0 or toplam_alacak > 0:
            axs[0].pie([toplam_borc, toplam_alacak], labels=["Borç", "Alacak"], autopct='%1.1f%%', colors=["#ff2e63", "#00adb5"])
            axs[0].set_title('Toplam Borç/Alacak')
        else:
            axs[0].text(0.5, 0.5, 'Veri yok', ha='center', va='center')
            axs[0].set_title('Toplam Borç/Alacak')
        if odemeyen_borc > 0 or odemeyen_alacak > 0:
            axs[1].pie([odemeyen_borc, odemeyen_alacak], labels=["Borç", "Alacak"], autopct='%1.1f%%', colors=["#393e46", "#222831"])
            axs[1].set_title('Ödenmemiş Borç/Alacak')
        else:
            axs[1].text(0.5, 0.5, 'Veri yok', ha='center', va='center')
            axs[1].set_title('Ödenmemiş Borç/Alacak')
        canvas = FigureCanvasTkAgg(fig, master=self.grafikler_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)
        # Kişiye göre borç/alacak dağılımı (Bar Grafik)
        cursor.execute("""
            SELECT k.ad, SUM(i.tutar) FROM islemler i
            LEFT JOIN kisiler k ON i.kisi_id = k.id
            WHERE i.kullanici_id = ? AND i.tur='alacak' AND i.odendi=0 GROUP BY k.ad
        """, (self.user_id,))
        alacak_data = cursor.fetchall()
        cursor.execute("""
            SELECT k.ad, SUM(i.tutar) FROM islemler i
            LEFT JOIN kisiler k ON i.kisi_id = k.id
            WHERE i.kullanici_id = ? AND i.tur='borc' AND i.odendi=0 GROUP BY k.ad
        """, (self.user_id,))
        borc_data = cursor.fetchall()
        # Kişiye Göre Alacak
        if alacak_data:
            fig2, ax2 = plt.subplots(figsize=(4, 3))
            labels, sizes = zip(*alacak_data)
            ax2.bar(labels, sizes, color="#00adb5")
            ax2.set_title('Kişiye Göre Alacak')
            ax2.set_ylabel('Tutar (TL)')
            ax2.tick_params(axis='x', rotation=45)
            canvas2 = FigureCanvasTkAgg(fig2, master=self.grafikler_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)
        else:
            label = ctk.CTkLabel(self.grafikler_frame, text="Kişiye Göre Alacak: Veri yok", font=ctk.CTkFont(size=16, weight="bold"))
            label.pack(pady=10)
        # Kişiye Göre Borç
        if borc_data:
            fig3, ax3 = plt.subplots(figsize=(4, 3))
            labels, sizes = zip(*borc_data)
            ax3.bar(labels, sizes, color="#ff2e63")
            ax3.set_title('Kişiye Göre Borç')
            ax3.set_ylabel('Tutar (TL)')
            ax3.tick_params(axis='x', rotation=45)
            canvas3 = FigureCanvasTkAgg(fig3, master=self.grafikler_frame)
            canvas3.draw()
            canvas3.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)
        else:
            label = ctk.CTkLabel(self.grafikler_frame, text="Kişiye Göre Borç: Veri yok", font=ctk.CTkFont(size=16, weight="bold"))
            label.pack(pady=10)
        # Zaman içindeki değişim (Çizgi Grafik)
        cursor.execute("SELECT tarih, tutar, tur FROM islemler WHERE kullanici_id = ? AND odendi=0 AND tarih IS NOT NULL ORDER BY tarih", (self.user_id,))
        islemler = cursor.fetchall()
        if islemler:
            tarih_list = [i[0] for i in islemler]
            borc_list = []
            alacak_list = []
            toplam_borc = 0
            toplam_alacak = 0
            for t, tutar, tur in islemler:
                if tur == 'borc':
                    toplam_borc += tutar
                elif tur == 'alacak':
                    toplam_alacak += tutar
                borc_list.append(toplam_borc)
                alacak_list.append(toplam_alacak)
            fig4, ax4 = plt.subplots(figsize=(6, 2.5))
            ax4.plot(tarih_list, borc_list, label='Borç', color='#ff2e63')
            ax4.plot(tarih_list, alacak_list, label='Alacak', color='#00adb5')
            ax4.set_title('Zaman İçinde Borç/Alacak')
            ax4.set_xlabel('Tarih')
            ax4.set_ylabel('Tutar (TL)')
            ax4.legend()
            fig4.autofmt_xdate()
            canvas4 = FigureCanvasTkAgg(fig4, master=self.grafikler_frame)
            canvas4.draw()
            canvas4.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)
        else:
            label = ctk.CTkLabel(self.grafikler_frame, text="Zaman İçinde Borç/Alacak: Veri yok", font=ctk.CTkFont(size=16, weight="bold"))
            label.pack(pady=10)
        conn.close() 