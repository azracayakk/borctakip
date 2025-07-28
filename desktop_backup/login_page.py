import customtkinter as ctk
import sqlite3
import hashlib
from tkinter import messagebox

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="transparent")
        self.on_login_success = on_login_success
        self.setup_ui()
        self.init_database()
    
    def setup_ui(self):
        """Modern login UI oluştur"""
        # Ana container
        main_container = ctk.CTkFrame(self, fg_color="#232526")
        main_container.pack(fill="both", expand=True)
        
        # Login kartı
        login_card = ctk.CTkFrame(main_container, fg_color=("#393e46", "#222831"), corner_radius=20)
        login_card.pack(expand=True, padx=50, pady=50)
        
        # Logo ve başlık
        header_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=30)
        
        title = ctk.CTkLabel(
            header_frame, 
            text="🔐 Borç Takip Sistemi", 
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#fff"
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Hesabınıza giriş yapın",
            font=ctk.CTkFont(size=16),
            text_color="#e0e0e0"
        )
        subtitle.pack(pady=(10, 0))
        
        # Form alanları
        form_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=40, pady=20)
        
        # Kullanıcı adı
        username_label = ctk.CTkLabel(
            form_frame, 
            text="👤 Kullanıcı Adı:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e0e0e0"
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame, 
            width=300,
            placeholder_text="Kullanıcı adınızı girin",
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            fg_color="#222831",
            text_color="#fff"
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Şifre
        password_label = ctk.CTkLabel(
            form_frame, 
            text="🔒 Şifre:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e0e0e0"
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame, 
            width=300,
            placeholder_text="Şifrenizi girin",
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            show="*",
            fg_color="#222831",
            text_color="#fff"
        )
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        # Giriş butonu
        login_btn = ctk.CTkButton(
            form_frame, 
            text="🔑 Giriş Yap", 
            command=self.login,
            width=300,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#393e46",
            hover_color="#222831",
            text_color="#fff"
        )
        login_btn.pack(pady=(0, 15))
    
    def init_database(self):
        """Kullanıcılar tablosunu oluştur"""
        try:
            conn = sqlite3.connect("borctakip.db")
            c = conn.cursor()
            
            # Kullanıcılar tablosu
            c.execute('''
                CREATE TABLE IF NOT EXISTS kullanicilar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kullanici_adi TEXT UNIQUE NOT NULL,
                    sifre_hash TEXT NOT NULL,
                    email TEXT,
                    ad_soyad TEXT,
                    olusturma_tarihi TEXT,
                    son_giris_tarihi TEXT
                )
            ''')
            
            # Demo kullanıcı ekle (eğer yoksa)
            demo_password_hash = hashlib.sha256("123456".encode()).hexdigest()
            c.execute("INSERT OR IGNORE INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, olusturma_tarihi) VALUES (?, ?, ?, datetime('now'))",
                     ("admin", demo_password_hash, "Demo Kullanıcı"))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Veritabanı başlatılırken hata oluştu: {str(e)}")
    
    def login(self):
        """Kullanıcı girişi"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Hata", "Kullanıcı adı ve şifre boş olamaz!")
            return
        
        try:
            conn = sqlite3.connect("borctakip.db")
            c = conn.cursor()
            
            # Şifreyi hash'le
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Kullanıcıyı kontrol et
            c.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = ? AND sifre_hash = ?", (username, password_hash))
            user = c.fetchone()
            
            if user:
                # Son giriş tarihini güncelle
                c.execute("UPDATE kullanicilar SET son_giris_tarihi = datetime('now') WHERE id = ?", (user[0],))
                conn.commit()
                
                messagebox.showinfo("Başarılı", f"✅ Hoş geldiniz, {user[4] or username}! (Rol: {user[-1]})")
                self.on_login_success(user)
            else:
                messagebox.showerror("Hata", "❌ Kullanıcı adı veya şifre hatalı!")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Giriş sırasında hata oluştu: {str(e)}")
    
    def show_register(self):
        """Kayıt sayfasını göster"""
        self.pack_forget()
        register_page = RegisterPage(self.master, self.on_login_success)
        register_page.pack(fill="both", expand=True)

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="transparent")
        self.on_login_success = on_login_success
        self.setup_ui()
    
    def setup_ui(self):
        """Modern kayıt UI oluştur"""
        # Ana container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # Kayıt kartı
        register_card = ctk.CTkFrame(main_container, fg_color=("gray90", "gray15"), corner_radius=20)
        register_card.pack(expand=True, padx=50, pady=50)
        
        # Logo ve başlık
        header_frame = ctk.CTkFrame(register_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=30)
        
        title = ctk.CTkLabel(
            header_frame, 
            text="📝 Yeni Hesap Oluştur", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Hesap bilgilerinizi girin",
            font=ctk.CTkFont(size=16),
            text_color=("gray40", "gray60")
        )
        subtitle.pack(pady=(10, 0))
        
        # Form alanları
        form_frame = ctk.CTkFrame(register_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=40, pady=20)
        
        # Ad Soyad
        name_label = ctk.CTkLabel(
            form_frame, 
            text="👤 Ad Soyad:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            form_frame, 
            width=300,
            placeholder_text="Ad ve soyadınızı girin",
            font=ctk.CTkFont(size=14),
            corner_radius=8
        )
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        # Kullanıcı adı
        username_label = ctk.CTkLabel(
            form_frame, 
            text="🔑 Kullanıcı Adı:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame, 
            width=300,
            placeholder_text="Kullanıcı adınızı girin",
            font=ctk.CTkFont(size=14),
            corner_radius=8
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Email
        email_label = ctk.CTkLabel(
            form_frame, 
            text="📧 Email:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            form_frame, 
            width=300,
            placeholder_text="Email adresinizi girin",
            font=ctk.CTkFont(size=14),
            corner_radius=8
        )
        self.email_entry.pack(fill="x", pady=(0, 15))
        
        # Şifre
        password_label = ctk.CTkLabel(
            form_frame, 
            text="🔒 Şifre:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame, 
            width=300,
            placeholder_text="Şifrenizi girin",
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            show="*"
        )
        self.password_entry.pack(fill="x", pady=(0, 15))
        
        # Şifre tekrar
        password_confirm_label = ctk.CTkLabel(
            form_frame, 
            text="🔒 Şifre Tekrar:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        password_confirm_label.pack(anchor="w", pady=(0, 5))
        
        self.password_confirm_entry = ctk.CTkEntry(
            form_frame, 
            width=300,
            placeholder_text="Şifrenizi tekrar girin",
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            show="*"
        )
        self.password_confirm_entry.pack(fill="x", pady=(0, 20))
        
        # Kayıt butonu
        register_btn = ctk.CTkButton(
            form_frame, 
            text="📝 Hesap Oluştur", 
            command=self.register,
            width=300,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green")
        )
        register_btn.pack(pady=(0, 15))
        
        # Giriş sayfasına dön linki
        login_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        login_frame.pack(fill="x")
        
        login_label = ctk.CTkLabel(
            login_frame,
            text="Zaten hesabınız var mı?",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        login_label.pack(side="left")
        
        login_link = ctk.CTkButton(
            login_frame,
            text="Giriş Yap",
            command=self.show_login,
            width=80,
            height=25,
            corner_radius=5,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=("gray80", "gray20"),
            text_color=("blue", "lightblue")
        )
        login_link.pack(side="right")
    
    def register(self):
        """Yeni kullanıcı kaydı"""
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        password_confirm = self.password_confirm_entry.get().strip()
        
        if not all([name, username, password, password_confirm]):
            messagebox.showerror("Hata", "Tüm alanları doldurun!")
            return
        
        if password != password_confirm:
            messagebox.showerror("Hata", "Şifreler eşleşmiyor!")
            return
        
        if len(password) < 6:
            messagebox.showerror("Hata", "Şifre en az 6 karakter olmalıdır!")
            return
        
        try:
            conn = sqlite3.connect("borctakip.db")
            c = conn.cursor()
            
            # Kullanıcı adı kontrolü
            c.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = ?", (username,))
            if c.fetchone():
                messagebox.showerror("Hata", "Bu kullanıcı adı zaten kullanılıyor!")
                conn.close()
                return
            
            # Şifreyi hash'le
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Yeni kullanıcı ekle
            c.execute("INSERT INTO kullanicilar (kullanici_adi, sifre_hash, email, ad_soyad, olusturma_tarihi) VALUES (?, ?, ?, ?, datetime('now'))",
                     (username, password_hash, email, name))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarılı", "✅ Hesabınız başarıyla oluşturuldu!")
            self.show_login()
            
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Kayıt sırasında hata oluştu: {str(e)}")
    
    def show_login(self):
        """Giriş sayfasını göster"""
        self.pack_forget()
        login_page = LoginPage(self.master, self.on_login_success)
        login_page.pack(fill="both", expand=True) 