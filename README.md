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

### Tugas 2

1. **Alur MVT pas buka halaman Projects**

Pas user buka `/projects/`, request pertama masuk ke `urls.py` project Django, terus diteruskan ke `main/urls.py`. Route bernama `show_projects` ngarahin request ke fungsi `show_projects` di `views.py`.

Di view itu, semua data proyek diambil dari model `Project` pake Django ORM, terus dimasukin ke context dengan nama `project_list`, ditambah jumlah total proyek, proyek yang udah released, dan proyek featured. Context ini terus diteruskan ke `projects.html`.

Template `projects.html` pake looping DTL buat nampilin tiap proyek. Kalau database belum punya data proyek, bagian `{% empty %}` bakal nampilin pesan belum ada proyek yang ditambahin. Template ini juga extend `base.html`, jadi navbar, footer, theme toggle, sama struktur dasarnya tetep konsisten sama halaman lain.

2. **Kenapa data mending disimpen di model**

Data proyek lebih baik disimpen di model biar konten sama tampilan kepisah. Template tugasnya cuma nampilin data, sedangkan detail kayak judul, kategori, status, teknologi, dan link proyek disimpen di database.

Kalau semua proyek ditulis langsung di HTML, aku harus copy struktur card tiap kali mau nambah proyek. Ribet, rawan typo dan duplikasi, serta makin susah diurus kalau jumlah proyeknya nambah banyak.

Dengan model, proyek bisa ditambah atau di-update lewat Django Admin tanpa perlu oprek template lagi. Nyimpen data di model juga bikin datanya lebih gampang dipake ulang. Data yang sama sekarang bisa ditampilin di halaman daftar, halaman detail, statistik, filter, atau fitur lain kalau websitenya dikembangin lebih lanjut.

3. **Bedanya `makemigrations` sama `migrate`**

`makemigrations` dipake buat ngedeteksi perubahan di model, terus bikin file migration yang ngejelasin perubahan struktur database-nya. Perintah ini belum langsung ngubah database.

Sementara itu, `migrate` dipake buat nerapin file migration itu ke database beneran. Django bakal bikin atau ubah tabel berdasarkan migration yang belum diterapin.

Contohnya, pas aku nambahin model `Project`, aku jalanin:

```bash
python manage.py makemigrations
python manage.py migrate
```

Perintah pertama bikin file migration buat model `Project`, sedangkan perintah kedua nerapin migration itu sampe tabelnya beneran kebuat di database.

#### Penggunaan AI

Aku pake Codex buat bantu ninjau checklist tugas, nyusun implementasi MVT, bikin unit test, dan ngembangin tampilan website yang responsif. Codex juga bantu pas bikin model, migration, view, route, template dinamis, serta beberapa fitur tambahan kayak theme toggle dan elemen dekoratif bergaya pixel-game.

Strategi prompting aku lakuin secara bertahap, mulai dari implementasi fitur utama, pengujian, audit sesuai instruksi tugas, sampe revisi berdasarkan hasil QA. Aku juga minta tiap masalah yang ketemu diperbaiki satu-satu biar hasil akhirnya tetep sesuai sama implementasi website yang sebenarnya.

Aku sendiri yang nentuin data dan proyek yang mau ditampilin, milih arah desain pixel-game, ngasih foto dan profil itch.io, serta ngecek hasilnya secara lokal. Aku juga yang ngasih koreksi kalau ada data atau desain yang belum sesuai, kayak ngubah kategori RISTEK jadi organisasi, nambahin BEM Fasilkom UI, mindahin Sortify AI ke Projects, ganti foto sama rasionya, ngubah tulisan di hero, serta minta penyesuaian responsive dan elemen game. Proses commit, push ke GitHub dan PWS, sampe milih commit yang dikumpulin juga aku kelola sendiri.

Ringkasan log prompting:

1. Audit requirement Tugas 2.
2. Implementasi model `Project` dan migration.
3. Implementasi view, route, dan template dinamis.
4. Penambahan unit test.
5. QA responsive dan perbaikan desain.
