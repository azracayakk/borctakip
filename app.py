from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'borctakip_secret_key_2024'

# Veritabanı başlatma
def init_database():
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    # Tüm tabloları sil ve yeniden oluştur
    c.execute('DROP TABLE IF EXISTS islemler')
    c.execute('DROP TABLE IF EXISTS kisiler')
    c.execute('DROP TABLE IF EXISTS kullanicilar')
    
    # Kullanıcılar tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS kullanicilar
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ad_soyad TEXT NOT NULL,
                  kullanici_adi TEXT UNIQUE NOT NULL,
                  sifre TEXT NOT NULL,
                  email TEXT,
                  rol TEXT DEFAULT 'user')''')
    
    # Kişiler tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS kisiler
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ad_soyad TEXT NOT NULL,
                  telefon TEXT,
                  email TEXT,
                  adres TEXT,
                  kullanici_id INTEGER,
                  FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id))''')
    
    # İşlemler tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS islemler
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  kisi_id INTEGER,
                  tutar REAL NOT NULL,
                  aciklama TEXT,
                  vade_tarihi TEXT,
                  odendi INTEGER DEFAULT 0,
                  tur TEXT NOT NULL,
                  tarih TEXT,
                  kullanici_id INTEGER,
                  FOREIGN KEY (kisi_id) REFERENCES kisiler (id),
                  FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id))''')
    
    # Admin kullanıcısını ekle
    admin_sifre = hashlib.sha256('123456'.encode()).hexdigest()
    c.execute('''INSERT OR REPLACE INTO kullanicilar (kullanici_adi, ad_soyad, sifre, rol)
                 VALUES (?, ?, ?, ?)''', ('admin', 'Admin', admin_sifre, 'admin'))
    
    conn.commit()
    conn.close()

# Veritabanı başlat
init_database()

# Ana sayfa - Giriş
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# Giriş işlemi
@app.route('/login', methods=['POST'])
def login():
    kullanici_adi = request.form['kullanici_adi']
    sifre = request.form['sifre']
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    # Şifreyi hash'le
    hashed_sifre = hashlib.sha256(sifre.encode()).hexdigest()
    
    c.execute('SELECT * FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?', 
              (kullanici_adi, hashed_sifre))
    user = c.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        session['kullanici_adi'] = user[2]
        session['rol'] = user[5]
        return redirect(url_for('dashboard'))
    else:
        flash('Kullanıcı adı veya şifre hatalı!', 'error')
        return redirect(url_for('index'))

# Çıkış
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    # Özet istatistikler
    c.execute('''SELECT SUM(tutar) FROM islemler 
                 WHERE kullanici_id = ? AND tur = 'borc' AND odendi = 0''', (session['user_id'],))
    toplam_borc = c.fetchone()[0] or 0
    
    c.execute('''SELECT SUM(tutar) FROM islemler 
                 WHERE kullanici_id = ? AND tur = 'alacak' AND odendi = 0''', (session['user_id'],))
    toplam_alacak = c.fetchone()[0] or 0
    
    c.execute('''SELECT SUM(tutar) FROM islemler 
                 WHERE kullanici_id = ? AND odendi = 1''', (session['user_id'],))
    toplam_odenen = c.fetchone()[0] or 0
    
    kalan = toplam_borc - toplam_alacak
    
    conn.close()
    
    return render_template('dashboard.html', 
                         toplam_borc=toplam_borc,
                         toplam_alacak=toplam_alacak,
                         toplam_odenen=toplam_odenen,
                         kalan=kalan)

# Kişiler sayfası
@app.route('/kisiler')
def kisiler():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    search = request.args.get('search', '')
    if search:
        c.execute('''SELECT * FROM kisiler 
                     WHERE kullanici_id = ? AND ad_soyad LIKE ?''', 
                  (session['user_id'], f'%{search}%'))
    else:
        c.execute('SELECT * FROM kisiler WHERE kullanici_id = ?', (session['user_id'],))
    
    kisiler = c.fetchall()
    conn.close()
    
    return render_template('kisiler.html', kisiler=kisiler, search=search)

# Kişi ekleme
@app.route('/kisi_ekle', methods=['POST'])
def kisi_ekle():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    ad_soyad = request.form['ad_soyad']
    telefon = request.form['telefon']
    email = request.form['email']
    adres = request.form['adres']
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO kisiler (ad_soyad, telefon, email, adres, kullanici_id)
                 VALUES (?, ?, ?, ?, ?)''', (ad_soyad, telefon, email, adres, session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash('Kişi başarıyla eklendi!', 'success')
    return redirect(url_for('kisiler'))

# Borçlar sayfası
@app.route('/borclar')
def borclar():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    # Filtreleme parametreleri
    sort = request.args.get('sort', 'vade_tarihi')
    order = request.args.get('order', 'ASC')
    tutar_min = request.args.get('tutar_min', '')
    tutar_max = request.args.get('tutar_max', '')
    only_unpaid = request.args.get('only_unpaid', '')
    
    # SQL sorgusu oluştur
    query = '''SELECT i.*, k.ad_soyad FROM islemler i
               JOIN kisiler k ON i.kisi_id = k.id
               WHERE i.kullanici_id = ? AND i.tur = 'borc' '''
    params = [session['user_id']]
    
    if tutar_min:
        query += ' AND i.tutar >= ?'
        params.append(float(tutar_min))
    if tutar_max:
        query += ' AND i.tutar <= ?'
        params.append(float(tutar_max))
    if only_unpaid:
        query += ' AND i.odendi = 0'
    
    query += f' ORDER BY i.{sort} {order}'
    
    c.execute(query, params)
    borclar = c.fetchall()
    
    # Kişiler listesi (dropdown için)
    c.execute('SELECT * FROM kisiler WHERE kullanici_id = ?', (session['user_id'],))
    kisiler = c.fetchall()
    
    conn.close()
    
    return render_template('borclar.html', borclar=borclar, kisiler=kisiler)

# Borç ekleme
@app.route('/borc_ekle', methods=['POST'])
def borc_ekle():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    kisi_id = request.form['kisi_id']
    tutar = request.form['tutar']
    aciklama = request.form['aciklama']
    vade_tarihi = request.form['vade_tarihi']
    
    if not kisi_id or not tutar:
        flash('Kişi ve tutar zorunludur!', 'error')
        return redirect(url_for('borclar'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO islemler (kisi_id, tutar, aciklama, vade_tarihi, tur, tarih, kullanici_id)
                 VALUES (?, ?, ?, ?, 'borc', ?, ?)''', 
              (kisi_id, tutar, aciklama, vade_tarihi, datetime.now().strftime('%Y-%m-%d'), session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash('Borç başarıyla eklendi!', 'success')
    return redirect(url_for('borclar'))

# Borç ödendi işaretleme
@app.route('/borc_odendi/<int:borc_id>')
def borc_odendi(borc_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    c.execute('''UPDATE islemler SET odendi = 1 
                 WHERE id = ? AND kullanici_id = ? AND tur = 'borc' ''', 
              (borc_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash('Borç ödendi olarak işaretlendi!', 'success')
    return redirect(url_for('borclar'))

# Alacaklar sayfası
@app.route('/alacaklar')
def alacaklar():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    # Filtreleme parametreleri
    sort = request.args.get('sort', 'vade_tarihi')
    order = request.args.get('order', 'ASC')
    tutar_min = request.args.get('tutar_min', '')
    tutar_max = request.args.get('tutar_max', '')
    only_unpaid = request.args.get('only_unpaid', '')
    
    # SQL sorgusu oluştur
    query = '''SELECT i.*, k.ad_soyad FROM islemler i
               JOIN kisiler k ON i.kisi_id = k.id
               WHERE i.kullanici_id = ? AND i.tur = 'alacak' '''
    params = [session['user_id']]
    
    if tutar_min:
        query += ' AND i.tutar >= ?'
        params.append(float(tutar_min))
    if tutar_max:
        query += ' AND i.tutar <= ?'
        params.append(float(tutar_max))
    if only_unpaid:
        query += ' AND i.odendi = 0'
    
    query += f' ORDER BY i.{sort} {order}'
    
    c.execute(query, params)
    alacaklar = c.fetchall()
    
    # Kişiler listesi (dropdown için)
    c.execute('SELECT * FROM kisiler WHERE kullanici_id = ?', (session['user_id'],))
    kisiler = c.fetchall()
    
    conn.close()
    
    return render_template('alacaklar.html', alacaklar=alacaklar, kisiler=kisiler)

# Alacak ekleme
@app.route('/alacak_ekle', methods=['POST'])
def alacak_ekle():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    kisi_id = request.form['kisi_id']
    tutar = request.form['tutar']
    aciklama = request.form['aciklama']
    vade_tarihi = request.form['vade_tarihi']
    
    if not kisi_id or not tutar:
        flash('Kişi ve tutar zorunludur!', 'error')
        return redirect(url_for('alacaklar'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO islemler (kisi_id, tutar, aciklama, vade_tarihi, tur, tarih, kullanici_id)
                 VALUES (?, ?, ?, ?, 'alacak', ?, ?)''', 
              (kisi_id, tutar, aciklama, vade_tarihi, datetime.now().strftime('%Y-%m-%d'), session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash('Alacak başarıyla eklendi!', 'success')
    return redirect(url_for('alacaklar'))

# Alacak ödendi işaretleme
@app.route('/alacak_odendi/<int:alacak_id>')
def alacak_odendi(alacak_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    c.execute('''UPDATE islemler SET odendi = 1 
                 WHERE id = ? AND kullanici_id = ? AND tur = 'alacak' ''', 
              (alacak_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash('Alacak ödendi olarak işaretlendi!', 'success')
    return redirect(url_for('alacaklar'))

# Raporlar sayfası
@app.route('/raporlar')
def raporlar():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    # Toplam istatistikler
    c.execute('''SELECT SUM(tutar) FROM islemler 
                 WHERE kullanici_id = ? AND tur = 'borc' AND odendi = 0''', (session['user_id'],))
    toplam_borc = c.fetchone()[0] or 0
    
    c.execute('''SELECT SUM(tutar) FROM islemler 
                 WHERE kullanici_id = ? AND tur = 'alacak' AND odendi = 0''', (session['user_id'],))
    toplam_alacak = c.fetchone()[0] or 0
    
    c.execute('''SELECT SUM(tutar) FROM islemler 
                 WHERE kullanici_id = ? AND odendi = 1''', (session['user_id'],))
    toplam_odenen = c.fetchone()[0] or 0
    
    # Kişiye göre borç/alacak
    c.execute('''SELECT k.ad_soyad, SUM(i.tutar) as toplam
                 FROM islemler i
                 JOIN kisiler k ON i.kisi_id = k.id
                 WHERE i.kullanici_id = ? AND i.tur = 'borc' AND i.odendi = 0
                 GROUP BY k.id, k.ad_soyad
                 ORDER BY toplam DESC''', (session['user_id'],))
    kisi_borc = c.fetchall()
    
    c.execute('''SELECT k.ad_soyad, SUM(i.tutar) as toplam
                 FROM islemler i
                 JOIN kisiler k ON i.kisi_id = k.id
                 WHERE i.kullanici_id = ? AND i.tur = 'alacak' AND i.odendi = 0
                 GROUP BY k.id, k.ad_soyad
                 ORDER BY toplam DESC''', (session['user_id'],))
    kisi_alacak = c.fetchall()
    
    conn.close()
    
    return render_template('raporlar.html', 
                         toplam_borc=toplam_borc,
                         toplam_alacak=toplam_alacak,
                         toplam_odenen=toplam_odenen,
                         kisi_borc=kisi_borc,
                         kisi_alacak=kisi_alacak)

# Ayarlar sayfası
@app.route('/ayarlar')
def ayarlar():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    # İstatistikler
    c.execute('SELECT COUNT(*) FROM kisiler WHERE kullanici_id = ?', (session['user_id'],))
    kisi_sayisi = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM islemler WHERE kullanici_id = ?', (session['user_id'],))
    islem_sayisi = c.fetchone()[0]
    
    conn.close()
    
    return render_template('ayarlar.html', kisi_sayisi=kisi_sayisi, islem_sayisi=islem_sayisi)

# Verileri temizleme
@app.route('/verileri_temizle', methods=['POST'])
def verileri_temizle():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('borctakip.db')
    c = conn.cursor()
    
    c.execute('DELETE FROM kisiler WHERE kullanici_id = ?', (session['user_id'],))
    c.execute('DELETE FROM islemler WHERE kullanici_id = ?', (session['user_id'],))
    
    conn.commit()
    conn.close()
    
    flash('Tüm veriler başarıyla temizlendi!', 'success')
    return redirect(url_for('ayarlar'))

# Yeni kullanıcı ekleme (sadece admin)
@app.route('/kullanici_ekle', methods=['POST'])
def kullanici_ekle():
    try:
        if 'user_id' not in session or session.get('rol') != 'admin':
            flash('Bu işlem için yetkiniz yok!', 'error')
            return redirect(url_for('ayarlar'))
        
        ad_soyad = request.form.get('ad_soyad', '')
        kullanici_adi = request.form.get('kullanici_adi', '')
        sifre = request.form.get('sifre', '')
        email = request.form.get('email', '')
        
        if not all([ad_soyad, kullanici_adi, sifre]):
            flash('Ad soyad, kullanıcı adı ve şifre zorunludur!', 'error')
            return redirect(url_for('ayarlar'))
        
        conn = sqlite3.connect('borctakip.db')
        c = conn.cursor()
        
        # Kullanıcı adı kontrolü
        c.execute('SELECT * FROM kullanicilar WHERE kullanici_adi = ?', (kullanici_adi,))
        if c.fetchone():
            flash('Bu kullanıcı adı zaten kullanılıyor!', 'error')
            conn.close()
            return redirect(url_for('ayarlar'))
        
        # Şifreyi hash'le
        hashed_sifre = hashlib.sha256(sifre.encode()).hexdigest()
        
        c.execute('''INSERT INTO kullanicilar (ad_soyad, kullanici_adi, sifre, email, rol)
                     VALUES (?, ?, ?, ?, 'user')''', (ad_soyad, kullanici_adi, hashed_sifre, email))
        
        conn.commit()
        conn.close()
        
        flash('Kullanıcı başarıyla eklendi!', 'success')
        return redirect(url_for('ayarlar'))
        
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}', 'error')
        return redirect(url_for('ayarlar'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000))) 