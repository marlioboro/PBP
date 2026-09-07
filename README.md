# Portofolio Pribadi Ammar

Proyek Django sederhana untuk menampilkan portofolio pribadi menggunakan HTML5 dan CSS3. Halaman berisi profil, kemampuan teknis, dan pengalaman yang disusun secara responsif untuk layar desktop maupun mobile.

## Menjalankan Proyek

```powershell
py -m pip install -r requirements.txt
py manage.py runserver
```

Setelah server berjalan, buka `http://127.0.0.1:8000/` di browser.

### Tugas 1

1. **Elemen Semantik HTML5** Iya, saya pakai `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<figure>`, sama `<footer>`. Awalnya kepikiran pakai `<div>` semua biar cepet, tapi semantic tag ternyata bikin struktur halaman jauh lebih gampang dibaca ulang. `<section>` saya pakai buat bagian besar kayak Profile, Skills, Experience. `<article>` buat bungkus info profil dan tiap pengalaman kerja, `<figure>` buat foto profil. Jadi fungsi tiap bagian tetep jelas walau ini masih static web.
2. **Tantangan Responsive** Yang paling nyusahin itu pas layout desktop mulai dikecilin ke tablet dan mobile. Hero yang tadinya dua kolom jadi sempit banget, terus tiga skill card sama baris Experience juga nggak muat lagi buat nampilin teks dengan nyaman. Solusinya saya set breakpoint CSS: hero jadi satu kolom, grid Skills dari tiga kolom jadi satu kolom, tiap item Experience ditumpuk vertikal. Buat nentuin elemen mana yang diprioritaskan, saya liat dulu urutan informasinya. Nama dan identitas tetep paling atas, baru foto, bio, sama link sosial. Saya cek hasilnya di ukuran desktop 1440px dan mobile 390px. Padding sama elemen dekoratif saya kecilin di mobile, tapi nggak saya sembunyiin karena masih muat dan nggak bikin horizontal overflow.
3. **Batasan Static Web** Yang paling kerasa itu pas mau update konten. Tiap mau nambah skill atau pengalaman baru, saya masih harus buka HTML terus tulis manual satu-satu. Rawan salah salin dan bakal makin susah dikelola kalau isi portofolionya nambah banyak. Website ini juga belum bisa nerima pesan, nyimpen data, atau nampilin detail proyek secara dinamis. Buat iterasi selanjutnya, saya pengen pindahin data proyek dan pengalaman ke database biar bisa dikelola lewat Django Admin. Mau nambahin halaman detail proyek, filter kategori, sama contact form yang beneran ngirim dan validasi pesan tanpa harus ubah HTML manual.

##### Penggunaan AI

Saya pakai Codex sebagai pendamping selama ngerjain tugas ini. Codex bantu saya nyusun dan ngerapiin struktur HTML semantik, CSS responsif, penyesuaian konten berdasarkan CV, sama audit akhir terhadap checklist tugas.

Saya sendiri yang nentuin data dan bagian mana yang mau ditampilin, milih arah desain, minta revisi kalau kontennya belum sesuai kondisi nyata, nyoba website-nya secara lokal, dan ngatur semua commit Git sendiri. Saya juga selalu ngecek ulang saran dari AI karena beberapa jawaban awalnya masih terlalu umum dan perlu disesuaikan sama implementasi sebenarnya.
