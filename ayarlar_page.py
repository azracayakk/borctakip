import customtkinter as ctk
import sqlite3
import os
import shutil
from tkinter import messagebox
from tkinter import filedialog

class AyarlarPage(ctk.CTkFrame):
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.user_id = current_user[0]
        self.setup_ui()
        self.load_stats()
    
    def setup_ui(self):
        """Modern UI bileşenlerini oluştur"""
        # Ana container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # Başlık bölümü
        header_frame = ctk.CTkFrame(main_container, fg_color=("gray85", "gray17"), corner_radius=15)
        header_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        title = ctk.CTkLabel(
            header_frame, 
            text="⚙️ Ayarlar ve Yönetim", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title.pack(pady=20)
        
        # Sadece admin için kullanıcı ekleme butonu
        try:
            user_role = self.current_user[-1] if self.current_user and len(self.current_user) > 7 else None
        except Exception:
            user_role = None
        if user_role == 'admin':
            add_user_btn = ctk.CTkButton(header_frame, text="👤 Yeni Kullanıcı Ekle", command=self.show_add_user_form, fg_color="#393e46", hover_color="#222831", text_color="#fff", font=ctk.CTkFont(size=14, weight="bold"))
            add_user_btn.pack(pady=(0, 10))
        
        # İçerik bölümü - iki sütunlu layout
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Sol sütun - Veritabanı Yönetimi
        db_container = ctk.CTkFrame(content_frame, fg_color=("gray90", "gray15"), corner_radius=15)
        db_container.pack(side="left", fill="y", padx=(0, 10))
        
        # Veritabanı başlığı
        db_title = ctk.CTkLabel(
            db_container, 
            text="🗄️ Veritabanı Yönetimi", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "gray90")
        )
        db_title.pack(pady=20)
        
        # Veritabanı bilgileri
        info_frame = ctk.CTkFrame(db_container, fg_color="transparent")
        info_frame.pack(fill="x", padx=25, pady=10)
        
        self.create_info_field(info_frame, "📊 Veritabanı Boyutu:", "db_size_label")
        self.create_info_field(info_frame, "👥 Toplam Kişi:", "person_count_label")
        self.create_info_field(info_frame, "💰 Toplam İşlem:", "transaction_count_label")
        self.create_info_field(info_frame, "⏳ Bekleyen İşlem:", "pending_count_label")
        
        # Veritabanı butonları
        db_buttons_frame = ctk.CTkFrame(db_container, fg_color="transparent")
        db_buttons_frame.pack(pady=25)
        
        backup_btn = ctk.CTkButton(
            db_buttons_frame, 
            text="💾 Yedek Al", 
            command=self.backup_database,
            width=200,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("blue", "darkblue"),
            hover_color=("darkblue", "blue")
        )
        backup_btn.pack(pady=5)
        
        restore_btn = ctk.CTkButton(
            db_buttons_frame, 
            text="🔄 Geri Yükle", 
            command=self.restore_database,
            width=200,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("orange", "darkorange"),
            hover_color=("darkorange", "orange")
        )
        restore_btn.pack(pady=5)
        
        clear_btn = ctk.CTkButton(
            db_buttons_frame, 
            text="🗑️ Verileri Temizle", 
            command=self.clear_database,
            width=200,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red")
        )
        clear_btn.pack(pady=5)
        # Sadece admin için, kırmızı butonun hemen altına kullanıcı ekleme butonu
        user_role = self.current_user[-1] if self.current_user and len(self.current_user) > 7 else None
        if user_role == 'admin':
            add_user_btn = ctk.CTkButton(db_buttons_frame, text="👤 Yeni Kullanıcı Ekle", command=self.show_add_user_form, fg_color="#393e46", hover_color="#222831", text_color="#fff", font=ctk.CTkFont(size=14, weight="bold"))
            add_user_btn.pack(pady=(10, 0))
        
        # Sağ sütun - Uygulama Ayarları
        app_container = ctk.CTkFrame(content_frame, fg_color=("gray90", "gray15"), corner_radius=15)
        app_container.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Uygulama başlığı
        app_title = ctk.CTkLabel(
            app_container, 
            text="🎨 Uygulama Ayarları", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "gray90")
        )
        app_title.pack(pady=20)
        
        # Tema ayarları
        theme_frame = ctk.CTkFrame(app_container, fg_color="transparent")
        theme_frame.pack(fill="x", padx=25, pady=10)
        
        theme_label = ctk.CTkLabel(
            theme_frame, 
            text="🌙 Tema:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        theme_label.pack(anchor="w", pady=(0, 5))
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame, 
            text="Karanlık Tema",
            command=self.toggle_theme,
            font=ctk.CTkFont(size=14)
        )
        self.theme_switch.pack(anchor="w")
        self.theme_switch.select()  # Varsayılan olarak karanlık tema
        
        # Diğer ayarlar
        settings_frame = ctk.CTkFrame(app_container, fg_color="transparent")
        settings_frame.pack(fill="x", padx=25, pady=20)
        
        # Otomatik yedekleme
        auto_backup_label = ctk.CTkLabel(
            settings_frame, 
            text="🔄 Otomatik Yedekleme:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        auto_backup_label.pack(anchor="w", pady=(0, 5))
        
        self.auto_backup_switch = ctk.CTkSwitch(
            settings_frame, 
            text="Haftalık otomatik yedekleme",
            font=ctk.CTkFont(size=14)
        )
        self.auto_backup_switch.pack(anchor="w")
        
        # Bildirimler
        notification_label = ctk.CTkLabel(
            settings_frame, 
            text="🔔 Bildirimler:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        notification_label.pack(anchor="w", pady=(20, 5))
        
        self.notification_switch = ctk.CTkSwitch(
            settings_frame, 
            text="Vade tarihi yaklaşan işlemler için bildirim",
            font=ctk.CTkFont(size=14)
        )
        self.notification_switch.pack(anchor="w")
        
        # Uygulama bilgileri
        info_container = ctk.CTkFrame(app_container, fg_color=("gray85", "gray20"), corner_radius=10)
        info_container.pack(fill="x", padx=25, pady=20)
        
        app_info_label = ctk.CTkLabel(
            info_container, 
            text="ℹ️ Uygulama Bilgileri", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90")
        )
        app_info_label.pack(pady=10)
        
        version_label = ctk.CTkLabel(
            info_container, 
            text="Sürüm: 1.0.0", 
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        version_label.pack()
        
        developer_label = ctk.CTkLabel(
            info_container, 
            text="Geliştirici: Borç Takip Sistemi", 
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        developer_label.pack(pady=(0, 10))
    
    def create_info_field(self, parent, label_text, field_name):
        """Bilgi alanı oluştur"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=5)
        
        label = ctk.CTkLabel(
            field_frame, 
            text=label_text, 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        label.pack(side="left")
        
        value_label = ctk.CTkLabel(
            field_frame, 
            text="Yükleniyor...", 
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        )
        value_label.pack(side="right")
        
        setattr(self, field_name, value_label)
    
    def load_stats(self):
        """İstatistikleri yükle"""
        try:
            conn = sqlite3.connect("borctakip.db")
            c = conn.cursor()
            
            # Kişi sayısı
            c.execute("SELECT COUNT(*) FROM kisiler WHERE kullanici_id = ?", (self.user_id,))
            person_count = c.fetchone()[0]
            
            # İşlem sayısı
            c.execute("SELECT COUNT(*) FROM islemler WHERE kullanici_id = ?", (self.user_id,))
            transaction_count = c.fetchone()[0]
            
            # Bekleyen işlem sayısı
            c.execute("SELECT COUNT(*) FROM islemler WHERE kullanici_id = ? AND odendi = 0", (self.user_id,))
            pending_count = c.fetchone()[0]
            
            conn.close()
            
            # Veritabanı boyutu
            db_size = self.get_db_size()
            
            # Etiketleri güncelle
            self.db_size_label.configure(text=f"{db_size}")
            self.person_count_label.configure(text=f"{person_count}")
            self.transaction_count_label.configure(text=f"{transaction_count}")
            self.pending_count_label.configure(text=f"{pending_count}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"❌ İstatistikler yüklenirken hata oluştu: {str(e)}")
    
    def get_db_size(self):
        """Veritabanı boyutunu al"""
        try:
            if os.path.exists("borctakip.db"):
                size_bytes = os.path.getsize("borctakip.db")
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.1f} KB"
                else:
                    return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return "0 B"
        except:
            return "Bilinmiyor"
    
    def toggle_theme(self):
        """Temayı değiştir"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        messagebox.showinfo("Tema Değişikliği", f"Tema {new_mode} olarak değiştirildi!")
    
    def backup_database(self):
        """Veritabanını yedekle"""
        try:
            backup_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                title="Yedek dosyasını kaydet"
            )
            
            if backup_path:
                shutil.copy2("borctakip.db", backup_path)
                messagebox.showinfo("Başarılı", f"✅ Veritabanı başarıyla yedeklendi:\n{backup_path}")
                
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Yedekleme sırasında hata oluştu: {str(e)}")
    
    def restore_database(self):
        """Veritabanını geri yükle"""
        try:
            restore_path = filedialog.askopenfilename(
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                title="Geri yüklenecek dosyayı seç"
            )
            
            if restore_path:
                result = messagebox.askyesno("Onay", 
                    "Bu işlem mevcut veritabanını değiştirecek. Devam etmek istediğinizden emin misiniz?")
                
                if result:
                    shutil.copy2(restore_path, "borctakip.db")
                    messagebox.showinfo("Başarılı", "✅ Veritabanı başarıyla geri yüklendi!")
                    self.load_stats()
                    
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Geri yükleme sırasında hata oluştu: {str(e)}")
    
    def clear_database(self):
        """Veritabanını temizle"""
        try:
            result = messagebox.askyesno("Dikkat!", 
                "Bu işlem TÜM verileri silecek ve geri alınamaz!\n\nDevam etmek istediğinizden emin misiniz?")
            
            if result:
                # Sadece kullanıcının verilerini sil
                conn = sqlite3.connect("borctakip.db")
                c = conn.cursor()
                c.execute("DELETE FROM kisiler WHERE kullanici_id = ?", (self.user_id,))
                c.execute("DELETE FROM islemler WHERE kullanici_id = ?", (self.user_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Başarılı", "✅ Veriler başarıyla temizlendi!")
                self.load_stats()
                
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Temizleme sırasında hata oluştu: {str(e)}") 

    def show_add_user_form(self):
        # Basit kullanıcı ekleme popup'ı
        popup = ctk.CTkToplevel(self)
        popup.title("Yeni Kullanıcı Ekle")
        popup.geometry("400x350")
        popup.grab_set()
        ctk.CTkLabel(popup, text="Yeni Kullanıcı Ekle", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        ad_entry = ctk.CTkEntry(popup, width=300, placeholder_text="Ad Soyad")
        ad_entry.pack(pady=5)
        username_entry = ctk.CTkEntry(popup, width=300, placeholder_text="Kullanıcı Adı")
        username_entry.pack(pady=5)
        password_entry = ctk.CTkEntry(popup, width=300, placeholder_text="Şifre", show="*")
        password_entry.pack(pady=5)
        email_entry = ctk.CTkEntry(popup, width=300, placeholder_text="Email (isteğe bağlı)")
        email_entry.pack(pady=5)
        def add_user():
            ad = ad_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            email = email_entry.get().strip()
            if not ad or not username or not password:
                messagebox.showerror("Hata", "Tüm zorunlu alanları doldurun!")
                return
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            try:
                conn = sqlite3.connect("borctakip.db")
                c = conn.cursor()
                c.execute("INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, email, olusturma_tarihi, rol) VALUES (?, ?, ?, ?, datetime('now'), 'user')", (username, password_hash, ad, email))
                conn.commit()
                conn.close()
                messagebox.showinfo("Başarılı", "Kullanıcı başarıyla eklendi!")
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Hata", f"Kullanıcı eklenemedi: {str(e)}")
        ctk.CTkButton(popup, text="Kaydet", command=add_user, fg_color="#393e46", hover_color="#222831", text_color="#fff").pack(pady=15)
        ctk.CTkButton(popup, text="İptal", command=popup.destroy, fg_color="#888", hover_color="#555").pack() 