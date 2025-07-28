import customtkinter as ctk
from kisiler_page import KisilerPage
from borclar_page import BorclarPage
from alacaklar_page import AlacaklarPage
from raporlar_page import RaporlarPage
from ayarlar_page import AyarlarPage
from login_page import LoginPage
import sqlite3
import os
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk

class BorcTakipApp:
    def __init__(self):
        # Modern tema ayarları
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Borç Takip Sistemi")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)

        # --- TAMAMEN GRİ/METALLIC ARKA PLAN ---
        self.root.configure(bg="#232526")
        
        # Kullanıcı bilgisi
        self.current_user = None
        
        # Veritabanını başlat
        self.init_database()
        
        # Ana frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#232526")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Modern ikonlu başlık ve özet kutuları
        self.header_label = ctk.CTkLabel(self.main_frame, text="💸 Borç Takip Sistemi", font=ctk.CTkFont(size=28, weight="bold"), text_color="#fff")
        self.header_label.pack(pady=(20, 10))
        self.summary_frame = ctk.CTkFrame(self.main_frame, fg_color=("#393e46", "#222831"), corner_radius=18)
        self.summary_frame.pack(pady=10, padx=10, fill="x")
        # 4 özet kutusu (kart)
        for title, value in [
            ("Toplam Borç", "₺0"),
            ("Toplam Alacak", "₺0"),
            ("Ödenen", "₺0"),
            ("Kalan", "₺0")
        ]:
            card = ctk.CTkFrame(self.summary_frame, fg_color=("#393e46", "#222831"), corner_radius=16, width=200, height=80)
            card.pack(side="left", padx=18, pady=10, fill=None, expand=False)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=15, weight="bold"), text_color="#e0e0e0").pack(pady=(12, 0))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"), text_color="#fff").pack(pady=(2, 10))
        
        # Giriş sayfasını göster
        self.show_login()
    
    def init_database(self):
        """Veritabanını başlat"""
        conn = sqlite3.connect("borctakip.db")
        c = conn.cursor()

        # Mevcut tabloları sil
        c.execute("DROP TABLE IF EXISTS islemler")
        c.execute("DROP TABLE IF EXISTS kisiler")
        c.execute("DROP TABLE IF EXISTS kullanicilar")

        # Kullanıcılar tablosu
        c.execute('''
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT UNIQUE NOT NULL,
                sifre_hash TEXT NOT NULL,
                email TEXT,
                ad_soyad TEXT,
                olusturma_tarihi TEXT,
                son_giris_tarihi TEXT,
                rol TEXT DEFAULT 'user'
            )
        ''')
        # Admin hesabı ekle/güncelle
        import hashlib
        admin_password_hash = hashlib.sha256("123456".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, olusturma_tarihi, rol) VALUES (?, ?, ?, datetime('now'), 'admin')", ("admin", admin_password_hash, "Azra Hülya"))
        c.execute("UPDATE kullanicilar SET rol='admin' WHERE kullanici_adi='admin'")

        # Kişiler tablosu
        c.execute('''
        CREATE TABLE IF NOT EXISTS kisiler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_id INTEGER,
            ad TEXT NOT NULL,
            telefon TEXT,
                email TEXT,
                adres TEXT,
                notlar TEXT,
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id)
        )
    ''')

        # İşlemler tablosu (tur ve tarih sütunu dahil!)
        c.execute('''
        CREATE TABLE IF NOT EXISTS islemler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_id INTEGER,
            kisi_id INTEGER,
            tutar REAL NOT NULL,
            aciklama TEXT,
            vade_tarihi TEXT,
                kategori TEXT,
                parabirimi TEXT,
            odendi INTEGER DEFAULT 0,
                tur TEXT,
                tarih TEXT,
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id),
            FOREIGN KEY (kisi_id) REFERENCES kisiler(id)
        )
    ''')
        conn.commit()
        conn.close()

    def show_login(self):
        """Giriş sayfasını göster"""
        # Mevcut içeriği temizle
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Giriş sayfasını göster
        login_page = LoginPage(self.main_frame, self.on_login_success)
        login_page.pack(fill="both", expand=True)
    
    def on_login_success(self, user):
        """Giriş başarılı olduğunda çağrılır"""
        self.current_user = user
        self.show_main_app()
    
    def show_main_app(self):
        """Ana uygulamayı göster"""
        # Mevcut içeriği temizle
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Sidebar
        self.create_sidebar()
        
        # Ana içerik alanı
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=("gray90", "gray13"))
        self.content_frame.pack(side="left", fill="both", expand=True, padx=(15, 0))
        
        # Sayfa yöneticisi
        self.current_page = None
        self.pages = {}
        
        # İlk sayfayı göster
        self.show_page("kisiler")
    
    def create_sidebar(self):
        """Modern sidebar oluştur"""
        sidebar = ctk.CTkFrame(self.main_frame, width=280, corner_radius=15)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)
        
        # Başlık
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=25)
        
        title = ctk.CTkLabel(
            title_frame, 
            text="Borç Takip", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Yönetim Sistemi",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        )
        subtitle.pack(pady=(5, 0))
        
        # Kullanıcı bilgisi
        user_frame = ctk.CTkFrame(sidebar, fg_color=("gray85", "gray20"), corner_radius=10)
        user_frame.pack(fill="x", padx=20, pady=10)
        
        user_label = ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.current_user[4] or self.current_user[1]}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        user_label.pack(pady=10)
        
        # Menü butonları
        menu_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        menu_frame.pack(fill="x", padx=15, pady=20)
        
        buttons = [
            ("👥 Kişiler", "kisiler", "gray70"),
            ("💸 Borçlar", "borclar", "red"),
            ("💰 Alacaklar", "alacaklar", "green"),
            ("📊 Raporlar", "raporlar", "blue"),
            ("⚙️ Ayarlar", "ayarlar", "gray70")
        ]
        
        for text, page_name, color in buttons:
            btn = ctk.CTkButton(
                menu_frame, 
                text=text,
                command=lambda p=page_name: self.show_page(p),
                width=250,
                height=50,
                corner_radius=10,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=("gray80", "gray25"),
                hover_color=("gray70", "gray35"),
                text_color=("gray10", "gray90")
            )
            btn.pack(pady=8)
        
        # Çıkış butonu
        logout_btn = ctk.CTkButton(
            sidebar,
            text="🚪 Çıkış Yap",
            command=self.logout,
            width=250,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red")
        )
        logout_btn.pack(pady=20)
        
        # Alt bilgi
        info_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        info_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        version_label = ctk.CTkLabel(
            info_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50")
        )
        version_label.pack()
    
    def show_page(self, page_name):
        """Sayfa göster"""
        if self.current_page:
            self.current_page.pack_forget()
        
        if page_name not in self.pages:
            if page_name == "kisiler":
                self.pages[page_name] = KisilerPage(self.content_frame, self.current_user[0])
            elif page_name == "borclar":
                self.pages[page_name] = BorclarPage(self.content_frame, self.current_user[0])
            elif page_name == "alacaklar":
                self.pages[page_name] = AlacaklarPage(self.content_frame, self.current_user[0])
            elif page_name == "raporlar":
                self.pages[page_name] = RaporlarPage(self.content_frame, self.current_user[0])
            elif page_name == "ayarlar":
                self.pages[page_name] = AyarlarPage(self.content_frame, self.current_user)

        self.current_page = self.pages[page_name]
        # --- EK: Borçlar veya Alacaklar sayfasına geçerken kişi listesini güncelle ---
        if page_name == "borclar" and hasattr(self.current_page, "load_kisiler"):
            self.current_page.load_kisiler()
        if page_name == "alacaklar" and hasattr(self.current_page, "load_kisiler"):
            self.current_page.load_kisiler()
        self.current_page.pack(fill="both", expand=True, padx=20, pady=20)
    
    def logout(self):
        """Çıkış yap"""
        result = messagebox.askyesno("Çıkış", "Çıkış yapmak istediğinizden emin misiniz?")
        if result:
            self.current_user = None
            self.show_login()
    
    def run(self):
        """Uygulamayı çalıştır"""
        self.root.mainloop()

    def create_gradient(self, width, height, color1, color2):
        from PIL import Image, ImageTk
        base = Image.new('RGB', (width, height), color1)
        top = Image.new('RGB', (width, height), color2)
        mask = Image.new('L', (width, height))
        for y in range(height):
            for x in range(width):
                mask.putpixel((x, y), int(255 * (y / height)))
        base.paste(top, (0, 0), mask)
        return ImageTk.PhotoImage(base)

if __name__ == "__main__":
    app = BorcTakipApp()
    app.run() 