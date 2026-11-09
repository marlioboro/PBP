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

### Tugas 3

1. **Kenapa menggunakan `ModelForm` dan `{% csrf_token %}`**

Saya menggunakan `ModelForm` karena struktur form bisa langsung mengikuti model Django. Field, tipe input, validasi, dan proses penyimpanan tidak perlu ditulis ulang secara manual. Pada `ExperienceForm`, saya cukup menentukan field yang boleh diisi, lalu form yang sama bisa dipakai untuk create dan update. Untuk update, objek lama diberikan lewat `instance`, sehingga `form.save()` memperbarui data yang sudah ada dan tidak membuat objek baru.

`{% csrf_token %}` diperlukan pada form POST untuk mencegah Cross-Site Request Forgery. Django membuat token yang terhubung dengan pengguna atau browser, lalu memeriksa token tersebut ketika request diterima. Request perubahan data yang tidak membawa token valid akan ditolak, sehingga situs lain tidak bisa diam-diam menyuruh browser pengguna mengirim form ke website ini.

2. **Kenapa JSON lebih banyak dipakai dibanding XML**

JSON lebih ringkas karena memakai pasangan key-value dan array tanpa opening serta closing tag sebanyak XML. Struktur JSON juga langsung cocok dengan object dan array pada JavaScript, jadi lebih mudah dikirim dari backend dan diproses oleh frontend. Hampir semua bahasa modern sudah punya parser JSON bawaan. XML tetap berguna untuk sistem yang membutuhkan namespace, schema, atau format dokumen yang kompleks, tetapi untuk API web modern JSON biasanya lebih sederhana dan menghasilkan payload yang lebih kecil.

3. **Alur view saat mengembalikan JSON dan alasan serialization**

Ketika `/api/experiences/` dibuka, `main/urls.py` mengarahkan request ke `get_experiences_json`. View mengambil data `Experience` melalui Django ORM, menerapkan filter judul jika ada, lalu `serializers.serialize()` mengubah QuerySet tersebut menjadi teks JSON. Teks itu dikembalikan lewat `HttpResponse` dengan content type `application/json`.

Serialization diperlukan karena objek model dan QuerySet Django bukan data JSON biasa. Di dalamnya ada objek Python serta tipe seperti UUID dan `datetime` yang tidak bisa langsung dikirim sebagai respons JSON. Serializer mengubahnya menjadi struktur teks yang konsisten dan bisa dibaca client. Pada halaman Experience, respons tersebut di-deserialize kembali menjadi objek yang dapat digunakan oleh Django Template Language.

#### Penggunaan AI

Saya memakai Codex sebagai pendamping untuk membaca checklist Tugas 3, menyusun CRUD Experience, membuat endpoint JSON beserta proses deserialisasi, menulis unit test, dan melakukan audit akhir. Pengerjaan dilakukan bertahap per fitur, kemudian setiap tahap diuji sebelum dibuat menjadi commit terpisah.

Saya menentukan bahwa Experience menjadi bagian portofolio yang dikembangkan, mempertahankan arah desain pixel-game, dan akan melakukan QA serta push Git sendiri. Saya juga meninjau hasil implementasi supaya alur create, update, delete, pencarian, dan tampilan data sesuai dengan website yang sebenarnya.

Ringkasan log prompting:

1. Audit requirement Tugas 3.
2. Implementasi `ExperienceForm` dan create data.
3. Implementasi endpoint JSON, filter, dan deserialisasi.
4. Implementasi update dan delete data.
5. Unit test dan audit akhir checklist.

### Tugas 4

Pada Tugas 4, website ditambahin sistem register, login, dan logout menggunakan autentikasi bawaan Django. Session dipakai supaya Django tetap mengenali akun di request berikutnya, sedangkan cookie `last_login` menyimpan waktu login terakhir dan dihapus lagi saat logout. Project dan Experience tetap bisa dibaca tanpa login, tapi semua tindakan yang mengubah data diperiksa lagi di sisi server.

Hak akses yang diterapkan:

| Peran | Baca data | Star/unstar | Update Experience | Create/delete |
| --- | --- | --- | --- | --- |
| Pengunjung | Ya | Harus login | Tidak | Tidak |
| Pengguna biasa | Ya | Ya | Tidak | Tidak |
| Editor | Ya | Ya | Ya | Tidak |
| Superuser | Ya | Ya | Ya | Ya |

Role Editor diterapkan dengan Django Group bernama `Editor`. Migration membuat group tersebut secara otomatis, tetapi penentuan akun Editor tetap dilakukan lewat Django Admin. Pemeriksaan izin tidak cuma dilakukan di template. View tetap memeriksa akun dengan `login_required`, `is_superuser`, dan keanggotaan group, sehingga mengetik URL aksi secara langsung tidak bisa melewati aturan akses.

#### Setup Tugas 4

```powershell
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Setelah server berjalan, buka `http://127.0.0.1:8000/admin/`, login dengan akun superuser, lalu buka **Authentication and Authorization → Groups → Editor** untuk menambahkan akun yang ingin dijadikan Editor. Akun biasa dapat dibuat melalui halaman `/register/`.

Untuk menjalankan pemeriksaan dan unit test:

```powershell
py manage.py check
py manage.py test
```

#### Penggunaan AI

Aku pake Codex sebagai pendamping buat bantu ninjau checklist Tutorial dan Tugas 4, ngecek implementasi autentikasi dan hak akses, serta bantu nyusun unit test untuk tiap peran. Aku ngasih instruksi dan revisi secara bertahap, mulai dari register, login, logout, cookie `last_login`, role Editor, sampe fitur star dan pengamanan endpoint JSON.

Aku sendiri yang nentuin Experience sebagai bagian Tugas 3 yang mau dilanjutin, nentuin pembagian hak akses tiap role, ngecek apakah tombol yang muncul udah sesuai, dan mastiin alur websitenya masih cocok sama desain portofolio sebelumnya. Aku juga yang ngatur urutan pengerjaan antara Tutorial 4 dan Tugas 4, minta commit dibagi per fitur, jalanin dan ngecek website secara lokal, serta ngelola push ke GitHub dan PWS.

Selama prosesnya, aku tetap ngecek ulang hasil dari AI dan minta perbaikan kalau belum sesuai kondisi tugas. Salah satu revisinya adalah mengganti pemeriksaan lama yang masih pake `is_staff` menjadi pembagian antara Editor dan superuser, serta memastikan pembatasan akses bukan cuma di tombol template, tapi juga diperiksa langsung di view. Dengan begitu, user yang nggak punya izin tetap nggak bisa menjalankan aksi hanya dengan membuka URL-nya secara langsung.

### Tugas 5

Halaman Experience sekarang memuat data dari `/api/experiences/` lewat Fetch API. Pencarian judul memakai debounce, dan ada filter kategori. Superuser bisa menambah pengalaman dari modal tanpa reload; pengguna yang login bisa memberi atau membatalkan star tanpa reload. Hak akses create, edit, dan delete tetap diperiksa di view Django. Data dari JSON ditampilkan dengan `textContent`, sementara input teks baru dibersihkan lewat `ExperienceForm`.

Untuk mencoba secara lokal, jalankan `py manage.py runserver`, buka `/experience/`, lalu coba pencarian dan filter. Login sebagai superuser untuk mencoba modal tambah pengalaman, atau sebagai pengguna biasa untuk mencoba star. Jalankan `py manage.py test main` untuk pengujian otomatis.

1. **Debouncing pada pencarian AJAX**

   Debouncing menunda pencarian sampai pengguna berhenti mengetik selama jeda tertentu. Di halaman Experience, timer 300 ms di-reset setiap ada input baru. Jadi kalau aku mengetik “RISTEK”, browser tidak perlu mengirim request untuk setiap huruf; hasil baru diminta setelah ketikan berhenti. Ini mengurangi request yang tidak perlu dan mencegah hasil lama menimpa hasil pencarian terbaru.

2. **Fungsi `await` saat memakai `fetch()`**

   `fetch()` langsung mengembalikan Promise, bukan data respons yang siap dipakai. `await fetch(...)` menunggu respons HTTP, lalu `await response.json()` menunggu isi respons selesai dibaca dan diubah menjadi object JavaScript. Tanpa `await`, kode berikutnya bisa berjalan sebelum data tersedia; mencoba membaca `.ok` atau me-loop hasil JSON seolah-olah sudah ada akan salah. Alur yang sama bisa ditulis dengan `.then()`, tetapi tetap harus menangani Promise-nya.

3. **XSS dan data AJAX**

   XSS terjadi ketika input yang berisi kode HTML atau JavaScript ikut dijalankan di browser orang lain. Template Django biasanya meng-escape variabel secara otomatis. Saat data JSON dirakit sendiri oleh JavaScript dan dimasukkan lewat `innerHTML`, perlindungan itu tidak otomatis berlaku. Karena itu, teks Experience dibuat sebagai node DOM lalu diisi dengan `textContent`, supaya tag berbahaya tampil sebagai teks. `ExperienceForm` juga memakai `strip_tags` saat menerima judul dan deskripsi. Pembersihan di server ini menjadi lapisan tambahan, bukan pengganti cara menampilkan data yang aman di browser.

#### Penggunaan AI

Aku pake Codex untuk bantu membaca checklist Tugas 5, menerapkan pola AJAX dari Tutorial 5 ke Experience, menulis pengujian hak akses dan validasi, serta mengecek hasil implementasi. Aku menentukan Experience sebagai bagian yang dilanjutkan dari Tugas 3–4, mempertahankan pembagian peran dan desain pixel-game yang sudah dipilih sebelumnya, dan meminta perubahan dikerjakan bertahap. Log prompting dan revisinya tersedia di task Codex yang aku pakai selama pengerjaan. Hasil kode tetap perlu aku cek lagi di browser lokal sebelum dikumpulkan.

### Tutorial 7

API baru menggunakan Django REST Framework tanpa mengubah model atau data lama. `ProjectSerializer` dan `ExperienceSerializer` menentukan field yang boleh dibaca dan ditulis, membersihkan input teks, serta menghitung status star berdasarkan akun yang sedang membuka API. API view terpisah dari view halaman HTML dan tersedia di `/api/v1/projects/` serta `/api/v1/experiences/`, masing-masing dengan route detail UUID dan `/star/`. Halaman Projects dan Experience kini mengambil data dari API tersebut; pencarian, modal tambah, toast, dan tampilan pixel-game tetap digunakan.

GET daftar dan detail dapat diakses semua orang. POST, PUT, PATCH, dan DELETE Project hanya untuk superuser; star untuk akun login. Pada Experience, Editor juga boleh PUT/PATCH, sedangkan tambah dan hapus tetap khusus superuser. Perubahan data melalui session memerlukan token CSRF. Endpoint JSON lama tetap ada agar integrasi sebelumnya tidak rusak.

Untuk menjalankan dan menguji:

```powershell
env\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
python manage.py test main
```

Buka `/api/v1/projects/` atau `/api/v1/experiences/` untuk melihat Browsable API. Tambahkan `?format=json` untuk JSON mentah. Test API ada di `main/tests_api.py` dan mencakup CRUD, pencarian, validasi, hak akses, CSRF, serta star.

#### Penggunaan AI

Aku memakai Codex untuk membantu membaca langkah Tutorial 7, menyesuaikan serializer dan API dengan field portofolioku, memindahkan halaman AJAX ke respons DRF, menyusun test, dan memeriksa tampilan lokal. Aku memilih untuk mempertahankan Projects dan Experience beserta desain dan pembagian peran yang sudah dibuat pada tugas sebelumnya. Aku akan melakukan QA akhir sebelum push dan pengumpulan sendiri.

### Tugas 6

Pada Tugas 6, pola DRF dari Tutorial 7 diterapkan ke bagian **Experience**, yaitu bagian yang aku kerjakan sendiri sejak Tugas 3. Model dan data lama tetap dipakai, jadi tidak ada migration baru.

| Komponen | Implementasi |
| --- | --- |
| Serializer | `ExperienceSerializer` di `main/serializers.py` memakai `fields` eksplisit. `star_count`, `is_starred`, dan `starred_by_names` adalah `SerializerMethodField` yang read-only. `validate_title` dan `validate_description` membersihkan input dengan `strip_tags` dan menolak teks yang isinya cuma tag. |
| Permission | `IsPortfolioOwnerOrEditorOrReadOnly` di `main/permissions.py` dipakai untuk daftar dan detail. Endpoint star memakai `IsAuthenticated`, dan akun pemberi star selalu diambil dari `request.user`. |
| API view | `experience_list` (GET, POST), `experience_detail` (GET, PUT, PATCH, DELETE), dan `experience_star` (POST) di `main/api_views.py` memakai `@api_view` dan `SessionAuthentication`. |
| URL | `/api/v1/experiences/`, `/api/v1/experiences/<uuid>/`, dan `/api/v1/experiences/<uuid>/star/` dengan nama `api:experience-list`, `api:experience-detail`, dan `api:experience-star`. |
| Pencarian | Parameter query `?title=` dan `?category=` pada endpoint daftar. |
| Halaman | `/experience/` menampilkan, mencari, menambah, mengedit, memberi star, dan menghapus data lewat `fetch()` tanpa reload. Modal yang sama dipakai untuk tambah (POST) dan edit (PATCH). Pesan 400 dan 403 dari API muncul di toast. |

Status HTTP yang dikembalikan: `201` saat data dibuat, `400` untuk input tidak valid, `403` untuk aksi yang tidak diizinkan atau tanpa token CSRF, `404` untuk UUID yang tidak ada, dan `204` setelah data dihapus.

Hak akses API Experience mengikuti peran dari Tugas 4:

| Peran | GET | Star | PUT/PATCH | POST/DELETE |
| --- | --- | --- | --- | --- |
| Pengunjung | Ya | Tidak (403) | Tidak (403) | Tidak (403) |
| Pengguna biasa | Ya | Ya | Tidak (403) | Tidak (403) |
| Editor | Ya | Ya | Ya | Tidak (403) |
| Superuser | Ya | Ya | Ya | Ya |

View halaman lama dari Tugas 3–4 sudah sesuai aturan ini: tambah dan hapus hanya untuk superuser, edit untuk Editor dan superuser. Yang berubah hanya `show_experience`, yang sekarang juga mengirim form ke Editor supaya modal edit bisa dipakai.

#### Menjalankan dan menguji Tugas 6

```powershell
env\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
python manage.py test main
```

Buka `/api/v1/experiences/` untuk melihat Browsable API, atau tambahkan `?format=json` untuk JSON mentah. Untuk mencoba setiap peran di halaman `/experience/`:

1. Login sebagai superuser untuk mencoba tambah, edit, dan hapus.
2. Tambahkan sebuah akun ke group `Editor` lewat Django Admin, lalu login dengan akun itu. Tombol Edit muncul, tetapi tombol tambah dan hapus tidak.
3. Login sebagai pengguna biasa untuk mencoba star.

Test Tugas 6 ada di `main/tests_experience_api.py` dan memakai `APITestCase`. Cakupannya:
- penolakan menulis untuk pengunjung dan pengguna biasa, dengan pengecekan isi database;
- Editor bisa PATCH/PUT tetapi ditolak saat POST dan DELETE;
- pemilik bisa membuat, mengubah, dan menghapus data;
- validasi input, termasuk `strip_tags`, kategori, dan URL tidak valid;
- star, termasuk penolakan untuk pengunjung;
- test `APIClient(enforce_csrf_checks=True)` dengan `.login()` yang membuktikan permintaan tanpa token CSRF ditolak.

1. **Apa itu REST, kenapa JSON aja belum cukup, dan bedanya PUT sama PATCH**

   REST itu gaya ngerancang API di mana data dianggap sebagai resource yang punya alamat sendiri. Contohnya, satu pengalaman di portofolioku alamatnya `/api/v1/experiences/<uuid>/`. Mau ngapain sama resource itu ditentuin lewat method HTTP: GET buat baca, POST buat bikin, PUT/PATCH buat ubah, DELETE buat hapus. Hasilnya dikasih tau lewat status code, misalnya 201 kalau berhasil dibuat, 400 kalau input salah, 403 kalau nggak boleh, 404 kalau nggak ketemu, dan 204 kalau udah dihapus.

   Jadi API yang balikin JSON belum tentu RESTful. Contohnya endpoint lama aku di Tugas 5, `/experience/add-ajax/`. Aksinya ditulis di URL, bukan lewat method, dan bentuknya beda-beda tiap fitur. Kalau ada API yang semua responsnya status 200 padahal gagal, itu juga bukan REST walaupun isinya JSON. JSON cuma format datanya, sedangkan REST itu soal cara ngatur resource, method, dan status-nya.

   PUT dipake buat ganti data secara utuh, jadi semua field wajib harus dikirim ulang. PATCH cuma ngubah field yang dikirim aja. Misalnya kalau aku mau edit semua isi pengalaman sekaligus, PUT cocok. Tapi kalau aku cuma mau ngisi `ended_at` pas kepanitiaan udah selesai, atau ganti kategorinya doang, PATCH lebih pas karena nggak perlu ngirim ulang judul dan deskripsi. Modal edit di halaman Experience aku pake PATCH.

2. **Peran serializer dan kenapa lebih enak dari `JsonResponse` manual**

   Serializer itu kayak penerjemah dua arah antara model Django dan JSON. Pas data keluar, serializer ngubah objek `Experience` jadi JSON, termasuk field tambahan kayak `category_display`, `star_count`, sama `is_starred`. Pas data masuk, serializer yang ngecek input dari client. Pilihan `category` harus valid, `thumbnail` harus URL, dan `title` sama `description` dibersihin pake `strip_tags` di `validate_<field>`. Kalau semua aman, baru disimpen lewat `save()`.

   Di Tutorial 5 aku masih nyusun dictionary satu-satu terus dibalikin pake `JsonResponse`. Validasinya juga harus ditulis sendiri atau numpang ke form. Ribet, dan gampang lupa field mana yang harusnya nggak boleh ikut keluar. Pake serializer, satu kelas bisa dipake buat list, detail, create, sama update sekaligus. Field yang read-only cukup ditulis sekali, dan kalau input salah, error-nya otomatis keluar rapi per field dengan status 400. Kodenya jadi lebih pendek dan konsisten.

3. **Bedanya autentikasi sama otorisasi, dan kenapa nggak cukup cuma nyembunyiin tombol**

   Autentikasi itu ngecek "ini siapa?". Di proyekku `SessionAuthentication` baca cookie session terus ngisi `request.user`. Otorisasi itu ngecek "orang ini boleh ngelakuin ini nggak?". Bagian ini diurus permission class kayak `IsPortfolioOwnerOrEditorOrReadOnly` dan `IsAuthenticated`. Jadi bisa aja user udah login (lolos autentikasi), tapi tetep ditolak 403 karena perannya nggak punya izin, misalnya Editor yang nyoba hapus pengalaman.

   Kalau cuma nyembunyiin tombol di template, itu cuma ngatur tampilan. Orang tetep bisa ngirim `DELETE /api/v1/experiences/<uuid>/` langsung dari console browser, `curl`, atau Postman tanpa pernah liat tombolnya. Makanya izin harus dicek di server, karena server satu-satunya bagian yang nggak bisa diubah sama user. Ini juga yang aku buktiin di test: request dikirim langsung sebagai tiap peran, terus aku cek database-nya beneran nggak berubah.

4. **Kenapa tetep butuh CSRF token, dan kenapa `force_authenticate` nggak cukup buat ngetesnya**

   Karena API-ku pake `SessionAuthentication`, browser bakal otomatis ngirim cookie session setiap ada request ke website ini, termasuk kalau request-nya dipicu dari website lain. Tanpa CSRF token, situs jahat bisa diam-diam nyuruh browser user yang lagi login buat ngirim POST atau DELETE ke API-ku, dan server bakal ngira itu request yang sah. CSRF token itu nilai yang cuma bisa dibaca halaman dari domainku sendiri, lewat cookie `csrftoken`, terus dikirim di header `X-CSRFToken`. Makanya semua `fetch()` yang ngubah data di `experience.js` selalu bawa header itu.

   `force_authenticate` itu jalan pintas buat test. User langsung ditempel ke request tanpa lewat proses login session, jadi pengecekan CSRF-nya juga ikut kelewat. Artinya test kayak gitu cuma bisa buktiin permission-nya bener, bukan buktiin CSRF-nya jalan. Buat ngetes CSRF, aku pake `APIClient(enforce_csrf_checks=True)` sama `.login()` biar session-nya beneran ada. Terus aku cek request tanpa token ditolak 403 dan datanya nggak berubah, sedangkan request yang bawa token berhasil.

#### Penggunaan AI

Untuk Tugas 6 aku memakai Claude sebagai pendamping. Claude membaca checklist Tugas 6, mengaudit kode Experience dari branch Tutorial 7 terhadap checklist itu, lalu menunjukkan bagian yang belum terpenuhi. Hasil auditnya: serializer, permission, dan endpoint Experience sudah ada sejak Tutorial 7. Yang belum ada adalah cara mengedit lewat PUT/PATCH dari halaman (tombol Edit masih membuka halaman form lama) dan test `APITestCase` khusus Experience yang lengkap untuk setiap peran.

Bagian yang dibantu AI:
- mengubah modal tambah menjadi modal tambah/edit yang mengirim PATCH ke API;
- menampilkan pesan error 400/403 dari DRF di toast;
- menulis `main/tests_experience_api.py`;
- menyusun draf jawaban pertanyaan reflektif.

Strategi promptingku adalah meminta audit dulu sebelum menulis kode, lalu mengerjakan celahnya satu per satu, dan menjalankan seluruh test setelah setiap perubahan.

Catatan keterbatasan dan koreksi manual:
- Satu test lama dari Tugas 5 (`test_action_controls_match_each_role`) gagal karena masih mengharapkan Editor tidak menerima form. Aturannya memang berubah di Tugas 6 (Editor butuh modal edit), jadi aku memilih menyesuaikan test-nya, bukan menghapusnya.
- Input `datetime-local` tidak membawa zona waktu, sementara server memakai UTC. Nilai `ended_at` saat edit diisi dalam UTC supaya tidak bergeser 7 jam ketika disimpan ulang. Ini perlu aku cek manual di browser.
- AI tidak bisa membuka halaman lokal di browser-ku, jadi QA tampilan modal edit, toast, dan alur tiap peran aku lakukan sendiri sebelum push dan pengumpulan.
