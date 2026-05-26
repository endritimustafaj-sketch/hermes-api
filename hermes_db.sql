-- =============================================================================
-- HERMES MARKETPLACE API — Database completo (schema + seed)
-- DBMS: SQLite (testim) / MySQL / PostgreSQL (prodhim)
-- Autor: AMF
-- Lënda: Arkitektura dhe Inxhinieria e Sistemeve (CIS450) — Master Shkencor
-- =============================================================================

PRAGMA foreign_keys = ON;

-- =============================================================================
-- 1. SCHEMA (DDL)
-- =============================================================================

DROP TABLE IF EXISTS pagesat;
DROP TABLE IF EXISTS fatura_detajet;
DROP TABLE IF EXISTS faturat;
DROP TABLE IF EXISTS api_keys;
DROP TABLE IF EXISTS listimet;
DROP TABLE IF EXISTS pjeset;
DROP TABLE IF EXISTS shitesit;
DROP TABLE IF EXISTS bleresit;
DROP TABLE IF EXISTS magazina;
DROP TABLE IF EXISTS markat;
DROP TABLE IF EXISTS kategorite;
DROP TABLE IF EXISTS zonat_transportit;
DROP TABLE IF EXISTS nivelet_discount;

CREATE TABLE nivelet_discount (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    emer                  TEXT    NOT NULL UNIQUE,
    perqindja             REAL    NOT NULL CHECK (perqindja >= 0 AND perqindja <= 100),
    totali_min_blerjeve   REAL    NOT NULL DEFAULT 0
);

CREATE TABLE zonat_transportit (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    emer              TEXT    NOT NULL UNIQUE,
    distanca_min_km   REAL    NOT NULL,
    distanca_max_km   REAL    NOT NULL,
    tarifa_fikse      REAL    NOT NULL,
    tarifa_per_km     REAL    NOT NULL,
    tarifa_per_kg     REAL    NOT NULL,
    CHECK (distanca_max_km > distanca_min_km)
);

CREATE TABLE kategorite (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    emer        TEXT    NOT NULL UNIQUE,
    pershkrim   TEXT
);

CREATE TABLE markat (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    emer                TEXT    NOT NULL UNIQUE,
    vendi_origjines     TEXT
);

CREATE TABLE magazina (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    emer            TEXT    NOT NULL,
    adresa          TEXT    NOT NULL,
    qyteti          TEXT    NOT NULL,
    lat             REAL    NOT NULL,
    lng             REAL    NOT NULL,
    eshte_aktiv     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE bleresit (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    emer                     TEXT    NOT NULL,
    mbiemer                  TEXT    NOT NULL,
    email                    TEXT    NOT NULL UNIQUE,
    fjalekalimi_hash         TEXT    NOT NULL,
    telefon                  TEXT,
    nipt                     TEXT,
    adresa                   TEXT    NOT NULL,
    qyteti                   TEXT    NOT NULL,
    lat                      REAL    NOT NULL,
    lng                      REAL    NOT NULL,
    nivel_discount_id        INTEGER NOT NULL DEFAULT 1,
    totali_blerjeve          REAL    NOT NULL DEFAULT 0,
    krijuar_me               TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nivel_discount_id) REFERENCES nivelet_discount(id)
);

CREATE TABLE shitesit (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    emer_kompanie            TEXT    NOT NULL,
    nipt                     TEXT    NOT NULL UNIQUE,
    email                    TEXT    NOT NULL UNIQUE,
    fjalekalimi_hash         TEXT    NOT NULL,
    telefon                  TEXT,
    adresa_magazines         TEXT    NOT NULL,
    qyteti                   TEXT    NOT NULL,
    lat                      REAL    NOT NULL,
    lng                      REAL    NOT NULL,
    eshte_verifikuar         INTEGER NOT NULL DEFAULT 0,
    komision_perqindja       REAL    NOT NULL DEFAULT 7.0,
    krijuar_me               TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pjeset (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    kodi_oem            TEXT    NOT NULL UNIQUE,
    emri                TEXT    NOT NULL,
    kategori_id         INTEGER NOT NULL,
    marka_id            INTEGER NOT NULL,
    pesha_kg            REAL    NOT NULL CHECK (pesha_kg > 0),
    pershkrimi          TEXT,
    model_kompatibil    TEXT,
    krijuar_me          TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kategori_id) REFERENCES kategorite(id),
    FOREIGN KEY (marka_id)    REFERENCES markat(id)
);

CREATE TABLE listimet (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    shites_id       INTEGER NOT NULL,
    pjese_id        INTEGER NOT NULL,
    cmimi           REAL    NOT NULL CHECK (cmimi >= 0),
    stoku           INTEGER NOT NULL DEFAULT 0 CHECK (stoku >= 0),
    aktive          INTEGER NOT NULL DEFAULT 1,
    krijuar_me      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shites_id) REFERENCES shitesit(id),
    FOREIGN KEY (pjese_id)  REFERENCES pjeset(id),
    UNIQUE (shites_id, pjese_id)
);

CREATE TABLE api_keys (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    blerese_id      INTEGER,
    shites_id       INTEGER,
    api_key         TEXT    NOT NULL UNIQUE,
    aktive          INTEGER NOT NULL DEFAULT 1,
    krijuar_me      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (blerese_id) REFERENCES bleresit(id),
    FOREIGN KEY (shites_id)  REFERENCES shitesit(id),
    CHECK ((blerese_id IS NOT NULL AND shites_id IS NULL)
        OR (blerese_id IS NULL AND shites_id IS NOT NULL))
);

CREATE TABLE faturat (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    blerese_id              INTEGER NOT NULL,
    zona_transportit_id     INTEGER NOT NULL,
    status                  TEXT    NOT NULL DEFAULT 'E_RE'
                            CHECK (status IN ('E_RE','NE_MAGAZINE','NE_TRANSPORT','DORZUAR','ANULUAR')),
    nentotali               REAL    NOT NULL,
    discount_perqindja      REAL    NOT NULL DEFAULT 0,
    discount_shuma          REAL    NOT NULL DEFAULT 0,
    pesha_totale_kg         REAL    NOT NULL,
    distanca_km             REAL    NOT NULL,
    kosto_transporti        REAL    NOT NULL,
    totali                  REAL    NOT NULL,
    adresa_dergesa          TEXT    NOT NULL,
    lat_dergesa             REAL    NOT NULL,
    lng_dergesa             REAL    NOT NULL,
    krijuar_me              TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (blerese_id)          REFERENCES bleresit(id),
    FOREIGN KEY (zona_transportit_id) REFERENCES zonat_transportit(id)
);

CREATE TABLE fatura_detajet (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fatura_id       INTEGER NOT NULL,
    listim_id       INTEGER NOT NULL,
    sasia           INTEGER NOT NULL CHECK (sasia > 0),
    cmimi_njesi     REAL    NOT NULL,
    pesha_njesi_kg  REAL    NOT NULL,
    total_rreshti   REAL    NOT NULL,
    FOREIGN KEY (fatura_id) REFERENCES faturat(id) ON DELETE CASCADE,
    FOREIGN KEY (listim_id) REFERENCES listimet(id)
);

CREATE TABLE pagesat (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    fatura_id           INTEGER NOT NULL UNIQUE,
    shuma               REAL    NOT NULL,
    menyra_pageses      TEXT    NOT NULL
                        CHECK (menyra_pageses IN ('CASH','KARTE','TRANSFER')),
    status              TEXT    NOT NULL DEFAULT 'PA_PAGUAR'
                        CHECK (status IN ('PA_PAGUAR','PAGUAR','RIMBURSUAR')),
    krijuar_me          TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fatura_id) REFERENCES faturat(id) ON DELETE CASCADE
);

CREATE INDEX idx_pjeset_kodi_oem        ON pjeset(kodi_oem);
CREATE INDEX idx_listimet_pjese         ON listimet(pjese_id);
CREATE INDEX idx_listimet_shites        ON listimet(shites_id);
CREATE INDEX idx_bleresit_email         ON bleresit(email);
CREATE INDEX idx_shitesit_email         ON shitesit(email);
CREATE INDEX idx_shitesit_nipt          ON shitesit(nipt);
CREATE INDEX idx_faturat_blerese        ON faturat(blerese_id);
CREATE INDEX idx_fatura_detajet_fatura  ON fatura_detajet(fatura_id);
CREATE INDEX idx_api_keys_key           ON api_keys(api_key);


-- =============================================================================
-- 2. SEED DATA — Lookup tabelat
-- =============================================================================

-- Nivelet e discount-it
INSERT INTO nivelet_discount (id, emer, perqindja, totali_min_blerjeve) VALUES
(1, 'Welcome',   5.0,   -1),
(2, 'Standard',  0.0,    0),
(3, 'Silver',    5.0,    500),
(4, 'Gold',     10.0,    2000),
(5, 'Platinum', 15.0,    5000);

-- Zonat e transportit
INSERT INTO zonat_transportit (id, emer, distanca_min_km, distanca_max_km, tarifa_fikse, tarifa_per_km, tarifa_per_kg) VALUES
(1, 'Urbane',     0,    30,   2.00, 0.30, 0.40),
(2, 'Suburbane',  30,   100,  3.00, 0.50, 0.60),
(3, 'Rurale',     100,  9999, 5.00, 0.80, 0.90);

-- Magazina e platformës
INSERT INTO magazina (id, emer, adresa, qyteti, lat, lng, eshte_aktiv) VALUES
(1, 'Magazina Hermes', 'Rruga e Kavajës, Km 5', 'Tiranë', 41.3275, 19.7800, 1);

-- 15 Kategori
INSERT INTO kategorite (id, emer, pershkrim) VALUES
(1,  'Filtra',                 'Filtra vaji, ajri, karburanti, kabine'),
(2,  'Frena',                  'Disqe, pllaka, lëngje, pompa frenash'),
(3,  'Motor',                  'Pjesë motorike: rripa, qarqe, mbajtëse, pompa vaji'),
(4,  'Suspension',             'Amortizatorë, susta, krahë, mbajtëse rrote'),
(5,  'Transmision',            'Friziona, kuti shpejtësisë, lidhëse'),
(6,  'Sistemi i Karburantit',  'Pompa, injektorë, rezervuarë'),
(7,  'Sistemi i Ftohjes',      'Radiator, termostat, pompë uji, antifrizë'),
(8,  'Sistemi i Shkarkimit',   'Marmite, katalizator, sensor lambda'),
(9,  'Elektrik',               'Bateri, kandele, bobina, alternator, sensorë'),
(10, 'Ndriçim',                'Llamba, drita të përparme, fanarë, LED'),
(11, 'Karrocerie',             'Pasqyra, dyer, paraurë, mbrojtës'),
(12, 'Goma dhe Rrota',         'Goma verore/dimërore, rrota, mbulesa'),
(13, 'Vajra dhe Lëngje',       'Vaj motori, lëng frenash, antifrizë, lëng kuti'),
(14, 'Aksesorë të Brendshëm',  'Tapete, mbulesa, mbajtëse telefoni, USB chargers'),
(15, 'Aksesorë të Jashtëm',    'Polish, kit pastrimi, triangull, jelek, sun shade');

-- 30 Marka të industrisë
INSERT INTO markat (id, emer, vendi_origjines) VALUES
(1,  'Bosch',           'Gjermani'),
(2,  'Mahle',           'Gjermani'),
(3,  'NGK',             'Japoni'),
(4,  'Brembo',          'Itali'),
(5,  'Sachs',           'Gjermani'),
(6,  'Mann',            'Gjermani'),
(7,  'Continental',     'Gjermani'),
(8,  'Valeo',           'Francë'),
(9,  'Lemforder',       'Gjermani'),
(10, 'Febi Bilstein',   'Gjermani'),
(11, 'Castrol',         'Mbretëria e Bashkuar'),
(12, 'Mobil',           'SHBA'),
(13, 'Pirelli',         'Itali'),
(14, 'Michelin',        'Francë'),
(15, 'Hella',           'Gjermani'),
(16, 'Philips',         'Holandë'),
(17, 'Osram',           'Gjermani'),
(18, 'Denso',           'Japoni'),
(19, 'Varta',           'Gjermani'),
(20, 'Exide',           'SHBA'),
(21, 'Gates',           'SHBA'),
(22, 'Magneti Marelli', 'Itali'),
(23, 'Total',           'Francë'),
(24, 'Liqui Moly',      'Gjermani'),
(25, 'Bilstein',        'Gjermani'),
(26, 'TRW',             'SHBA'),
(27, 'SKF',             'Suedi'),
(28, 'AC Delco',        'SHBA'),
(29, 'K&N',             'SHBA'),
(30, 'Generic',         'Kinë');


-- =============================================================================
-- 3. SEED DATA — Shitësit (7 kompani në qytete të ndryshme)
-- =============================================================================
-- Shënim: fjalekalimi_hash është placeholder; në kod gjenerohet me bcrypt
INSERT INTO shitesit (id, emer_kompanie, nipt, email, fjalekalimi_hash, telefon, adresa_magazines, qyteti, lat, lng, eshte_verifikuar, komision_perqindja) VALUES
(1, 'AutoPjese Sh.p.k.',       'L91234567A', 'info@autopjese.al',     '$2b$12$placeholder_hash_01', '+355692111111', 'Rruga e Kavajës 200',    'Tiranë',  41.3300, 19.8100, 1, 7.0),
(2, 'Durrës Parts',            'L92345678B', 'info@durresparts.al',   '$2b$12$placeholder_hash_02', '+355692222222', 'Rruga Egnatia 50',       'Durrës',  41.3100, 19.4500, 1, 7.0),
(3, 'Korça Auto',              'L93456789C', 'sales@korca-auto.al',   '$2b$12$placeholder_hash_03', '+355692333333', 'Bulevardi Republika',    'Korçë',   40.6186, 20.7808, 1, 8.0),
(4, 'Vlora Motors',            'L94567890D', 'kontakt@vloramotors.al','$2b$12$placeholder_hash_04', '+355692444444', 'Lagjia Pavarësia 12',    'Vlorë',   40.4660, 19.4900, 1, 7.5),
(5, 'Shkodra Spare',           'L95678901E', 'info@shkodraspare.al',  '$2b$12$placeholder_hash_05', '+355692555555', 'Rruga 28 Nëntori 33',    'Shkodër', 42.0683, 19.5126, 1, 7.5),
(6, 'Elektriku Online',        'L96789012F', 'shitje@elektriku.al',   '$2b$12$placeholder_hash_06', '+355692666666', 'Rruga Bardhyl 21',       'Tiranë',  41.3225, 19.8240, 1, 6.5),
(7, 'Auto Aksesore Tirana',    'L97890123G', 'info@autoaksesore.al',  '$2b$12$placeholder_hash_07', '+355692777777', 'Rruga e Durrësit 150',   'Tiranë',  41.3360, 19.8000, 1, 8.5);


-- =============================================================================
-- 4. SEED DATA — Blerësit (5 me nivele të ndryshme)
-- =============================================================================
INSERT INTO bleresit (id, emer, mbiemer, email, fjalekalimi_hash, telefon, nipt, adresa, qyteti, lat, lng, nivel_discount_id, totali_blerjeve) VALUES
(1, 'Arben',  'Hoxha',  'arben.hoxha@example.com',     '$2b$12$placeholder_hash_b1', '+355681000001', NULL,         'Rruga Myslym Shyri 10',       'Tiranë', 41.3270, 19.8060, 1, 0),       -- Welcome (klient i ri)
(2, 'Besa',   'Kola',   'besa.kola@example.com',       '$2b$12$placeholder_hash_b2', '+355681000002', NULL,         'Rruga Komuna e Parisit 5',    'Tiranë', 41.3220, 19.8030, 3, 720),     -- Silver
(3, 'Gent',   'Marku',  'gent.marku@example.com',      '$2b$12$placeholder_hash_b3', '+355681000003', NULL,         'Lagjia 14, Rruga Aleksandër', 'Durrës', 41.3120, 19.4480, 4, 2350),    -- Gold
(4, 'Edmond', 'Beqiri', 'edmond.beqiri@example.com',   '$2b$12$placeholder_hash_b4', '+355681000004', NULL,         'Rruga Justin Godard 7',       'Vlorë',  40.4680, 19.4920, 2, 180),     -- Standard
(5, 'AutoServis Bega', 'Sh.p.k.', 'admin@autoservisbega.al', '$2b$12$placeholder_hash_b5', '+355681000005', 'L98765432H', 'Rruga Hoxha Tahsim 23',     'Tiranë', 41.3290, 19.8090, 5, 6800);  -- Platinum (biznes)


-- =============================================================================
-- 5. SEED DATA — Pjesët (80 pjesë në katalog)
-- =============================================================================

-- ============ Kategoria 1: FILTRA ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(1,  'BOSCH-0986452060', 'Filtër vaji premium',           1, 1, 0.350, 'Filtër vaji për motorë benzine 1.6-2.0L',     'VW Golf 5/6/7, Audi A3 8P/8V, Skoda Octavia 2/3'),
(2,  'MAHLE-OC205',      'Filtër vaji ekonomik',          1, 2, 0.320, 'Filtër vaji standard',                         'VW Golf 5/6, Audi A3 8P'),
(3,  'MANN-W7008',       'Filtër vaji Mann',              1, 6, 0.310, 'Filtër vaji me valvul tërheqëse',              'BMW 3 Series E90/F30, BMW 5 Series E60/F10'),
(4,  'BOSCH-F026400123', 'Filtër ajri',                   1, 1, 0.450, 'Filtër ajri me letër të valëzuar',             'VW Golf 5/6, Audi A3 8P'),
(5,  'MAHLE-LX1566',     'Filtër ajri sportiv',           1, 2, 0.480, 'Filtër ajri me flux të rritur',                'VW Golf GTI, Audi S3'),
(6,  'MANN-C2380',       'Filtër ajri standard',          1, 6, 0.420, 'Filtër ajri OEM cilësi',                       'Mercedes C-Class W203/W204'),
(7,  'BOSCH-F026402115', 'Filtër karburanti diesel',      1, 1, 0.650, 'Filtër naftë me ngrohës',                      'VW Passat B6/B7 TDI, Audi A4 B7/B8 TDI'),
(8,  'MAHLE-KL169',      'Filtër karburanti benzine',     1, 2, 0.480, 'Filtër benzine inline',                        'VW Golf 4/5 benzin'),
(9,  'BOSCH-1987432217', 'Filtër kabine me karbon',       1, 1, 0.380, 'Filtër ajri kabine me karbon aktiv',           'VW Golf 5/6, Audi A3 8P'),
(10, 'MANN-CUK2939',     'Filtër kabine antibakterial',   1, 6, 0.350, 'Filtër kabine me trajtim antibakterial',       'BMW 3 Series E90/F30');

-- ============ Kategoria 2: FRENA ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(11, 'BREMBO-09945911',  'Disk freni i përparmë 312mm',   2, 4, 7.500, 'Disk freni i ventiluar 312×25mm',              'VW Golf 5/6 GTI, Audi A3 8P 2.0 TDI'),
(12, 'BREMBO-08A53620',  'Disk freni i pasmë 282mm',      2, 4, 5.800, 'Disk freni i pasmë solid 282×12mm',            'VW Golf 5/6/7, Audi A3 8P'),
(13, 'BREMBO-P85075',    'Pllaka frenash të përparme',    2, 4, 2.100, 'Set 4 pllaka frenash me sensor',               'VW Golf 5/6, Audi A3 8P, Skoda Octavia 2'),
(14, 'BREMBO-P85020',    'Pllaka frenash të pasme',       2, 4, 1.800, 'Set 4 pllaka frenash te pasme',                'VW Golf 5/6, Audi A3 8P'),
(15, 'TRW-GDB1497',      'Pllaka frenash TRW të përparme',2, 26, 2.050, 'Set pllaka frenash ekonomike',                'BMW 3 Series E90, BMW 1 Series E87'),
(16, 'BOSCH-0204114',    'Lëng frenash DOT4 1L',          2, 1, 1.100, 'Lëng frenash sintetik DOT4',                   'Universale (të gjitha makinat)'),
(17, 'CASTROL-DOT4',     'Lëng frenash Castrol DOT4 1L',  2, 11, 1.100, 'Lëng frenash DOT4 me pikë vlimi e lartë',     'Universale');

-- ============ Kategoria 3: MOTOR ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(18, 'GATES-T1058',      'Rrip i kohës (timing belt)',    3, 21, 0.250, 'Rrip kohor me dhëmbë',                         'VW Golf 5/6 1.9 TDI, Audi A3 8P 1.9 TDI'),
(19, 'CONTI-CT1028',     'Rrip shërbimi (serpentine)',    3, 7,  0.180, 'Rrip i shumëfishtë V me 6 brinjë',             'VW Golf 5/6, Audi A3 8P'),
(20, 'GATES-K025603XS',  'Kit rrip kohor komplet',        3, 21, 1.850, 'Set rrip + roller + pompë uji',                'VW Passat 1.9 TDI, Audi A4 B7 TDI'),
(21, 'FEBI-100148',      'Mbajtëse motori e djathtë',     3, 10, 1.800, 'Mbajtëse motori hydraulike',                   'VW Golf 5/6, Audi A3 8P'),
(22, 'LEMFORDER-3061101','Mbajtëse motori Lemforder',     3, 9,  1.900, 'Mbajtëse motori OEM',                          'BMW 3 Series E90/F30'),
(23, 'BOSCH-0451103316', 'Pompë vaji',                    3, 1,  2.200, 'Pompë vaji motori me 3 rotorë',                'VW Golf 5/6 1.9 TDI');

-- ============ Kategoria 4: SUSPENSION ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(24, 'BILSTEIN-22-141927','Amortizator i përparmë',       4, 25, 4.500, 'Amortizator gas i përparmë',                  'VW Golf 5/6, Audi A3 8P'),
(25, 'SACHS-313270',     'Amortizator i pasmë',           4, 5,  4.200, 'Amortizator gas i pasmë',                      'VW Golf 5/6'),
(26, 'BILSTEIN-19-219660','Amortizator BMW',              4, 25, 4.800, 'Amortizator i përparmë BMW',                   'BMW 3 Series E90/F30'),
(27, 'LEMFORDER-3037201','Krah i përparmë',               4, 9,  3.100, 'Krah suspension i përparmë me kokë sferike',   'VW Golf 5/6, Audi A3 8P'),
(28, 'FEBI-23036',       'Sustë e përparme',              4, 10, 2.800, 'Sustë spirale e përparme',                     'VW Golf 5/6 1.9 TDI'),
(29, 'SKF-VKBA3525',     'Mbajtëse rrote e përparme',     4, 27, 1.500, 'Set mbajtëse rrote me ABS',                    'VW Golf 5/6, Audi A3 8P'),
(30, 'SKF-VKBA6543',     'Mbajtëse rrote e pasme',        4, 27, 1.350, 'Set mbajtëse rrote e pasme me ABS',            'VW Golf 5/6');

-- ============ Kategoria 5: TRANSMISION ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(31, 'SACHS-3000951077', 'Friksion komplet (disk+presion)',5, 5, 12.500, 'Set friksioni 240mm me disk e presion',       'VW Golf 5/6, Audi A3 8P 2.0 TDI'),
(32, 'VALEO-826806',     'Liriues ngjitës (release)',     5, 8,  0.700, 'Liriues ngjitës hidraulik',                    'VW Golf 5/6'),
(33, 'SACHS-1862-510-211','Kalliçe friziona (disk)',      5, 5,  3.500, 'Disk friziona 240mm 22Z',                      'VW Golf 5/6 1.9 TDI');

-- ============ Kategoria 6: SISTEMI I KARBURANTIT ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(34, 'BOSCH-0580254044', 'Pompë karburanti elektrike',    6, 1,  1.200, 'Pompë karburanti në rezervuar 3.5 bar',        'VW Golf 5/6, Audi A3 8P'),
(35, 'BOSCH-0280155712', 'Injektor karburanti',           6, 1,  0.250, 'Injektor multipoint EV6',                      'VW Golf 5 1.6 FSI');

-- ============ Kategoria 7: SISTEMI I FTOHJES ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(36, 'MAHLE-CP122000P',  'Pompë uji',                     7, 2,  1.400, 'Pompë uji me trupore alumini',                 'VW Golf 5/6 1.9/2.0 TDI'),
(37, 'MAHLE-TH3-87',     'Termostat',                     7, 2,  0.280, 'Termostat 87°C me banjo',                      'VW Golf 5/6'),
(38, 'MAHLE-CR1539-000P','Radiator',                      7, 2,  6.500, 'Radiator alumini 650×400×32mm',                'VW Golf 5/6 1.9 TDI');

-- ============ Kategoria 8: SISTEMI I SHKARKIMIT ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(39, 'BOSCH-0258006028', 'Sensor lambda i përparmë',      8, 1,  0.180, 'Sensor lambda planar 4-tela',                  'VW Golf 5/6 benzin'),
(40, 'DENSO-DOX0150',    'Sensor lambda Denso',           8, 18, 0.190, 'Sensor lambda OEM Denso',                      'Toyota, Lexus, BMW disa modele');

-- ============ Kategoria 9: ELEKTRIK ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(41, 'NGK-BKR6E',        'Kandele standarde NGK',         9, 3,  0.080, 'Kandele me elektrodë nikeli',                  'Universale për motorë benzine'),
(42, 'NGK-IZFR6T11',     'Kandele iridium NGK',           9, 3,  0.085, 'Kandele iridium-platinium long-life',          'VW Golf 5/6 TSI, Audi A3 8P TFSI'),
(43, 'BOSCH-FR7DC',      'Kandele Bosch Super',           9, 1,  0.082, 'Kandele me elektrodë bakri',                   'Universale benzin'),
(44, 'VARTA-E11',        'Bateri 74Ah Blue Dynamic',      9, 19, 18.500,'Bateri 74Ah 680A 12V',                         'VW Golf 5/6, Audi A3 8P benzin'),
(45, 'VARTA-D24',        'Bateri 60Ah AGM Blue Dynamic',  9, 19, 16.800,'Bateri 60Ah 540A AGM',                         'VW Golf 5/6 start-stop'),
(46, 'VARTA-E39',        'Bateri 70Ah Silver Dynamic',    9, 19, 17.900,'Bateri 70Ah 760A',                             'VW Passat B6/B7, Audi A4 B7/B8'),
(47, 'EXIDE-EA770',      'Bateri 77Ah Exide',             9, 20, 19.200,'Bateri 77Ah 760A',                             'BMW 3 Series E90, Mercedes C-Class'),
(48, 'BOSCH-F005A00026', 'Alternator 90A',                9, 1,  5.800, 'Alternator 12V 90A me regulator',              'VW Golf 5/6 1.9 TDI'),
(49, 'BOSCH-0001125042', 'Starter motori',                9, 1,  4.200, 'Starter 12V 2.0kW reduktor',                   'VW Golf 5/6 TDI'),
(50, 'BOSCH-0986221024', 'Bobinë ndezje',                 9, 1,  0.350, 'Bobinë ndezje individuale stick-coil',         'VW Golf 5/6 TSI, Audi A3 8P TFSI'),
(51, 'BOSCH-0280218060', 'Sensor MAF (fluks ajri)',       9, 1,  0.180, 'Sensor fluks ajri me 5 pin',                   'VW Golf 5/6 TDI'),
(52, 'BOSCH-0265007897', 'Sensor ABS i përparmë',         9, 1,  0.120, 'Sensor ABS aktiv',                             'VW Golf 5/6, Audi A3 8P');

-- ============ Kategoria 10: NDRIÇIM ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(53, 'PHILIPS-12972PRC1','Llambë H7 standarde',           10, 16, 0.040, 'Llambë halogjene H7 55W 12V',                  'Universale'),
(54, 'PHILIPS-12972XVPS2','Llambë H7 X-treme Vision Pro',10, 16, 0.045, 'Llambë H7 +150% më shumë dritë',               'Universale'),
(55, 'OSRAM-64210NBP',   'Llambë H7 Osram Night Breaker', 10, 17, 0.040, 'Llambë H7 +150% dritë e bardhë',               'Universale'),
(56, 'PHILIPS-12342PRB1','Llambë H4 standarde',           10, 16, 0.045, 'Llambë halogjene H4 60/55W',                   'Universale'),
(57, 'PHILIPS-11972LED', 'Llambë LED H7 Ultinon Pro9100', 10, 16, 0.120, 'LED H7 6500K, life-time',                      'Universale (homologim sipas vendit)'),
(58, 'HELLA-1AL009295-031','Dritë e përparme komplet',    10, 15, 5.500, 'Dritë e përparme me dyfishtë reflektor',       'VW Golf 5'),
(59, 'MAGNETI-712450521129','Dritë e pasme komplet',      10, 22, 3.200, 'Dritë e pasme me LED',                         'VW Golf 6');

-- ============ Kategoria 11: KARROCERIE ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(60, 'HELLA-9EH-355-018','Pasqyrë anësore djathtas',      11, 15, 1.800, 'Pasqyrë elektrike me ngrohje',                 'VW Golf 5/6'),
(61, 'HELLA-9EH-355-019','Pasqyrë anësore majtas',        11, 15, 1.800, 'Pasqyrë elektrike me ngrohje',                 'VW Golf 5/6');

-- ============ Kategoria 12: GOMA DHE RROTA ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(62, 'MICHELIN-2055516PRIMACY','Gomë verore 205/55 R16',  12, 14, 9.200, 'Michelin Primacy 4 — 205/55 R16 91V',          'Universale 16-inch'),
(63, 'PIRELLI-2055516P7',     'Gomë verore Pirelli P7',   12, 13, 9.500, 'Pirelli Cinturato P7 — 205/55 R16 91V',        'Universale 16-inch'),
(64, 'MICHELIN-2055516ALPIN6','Gomë dimërore Alpin 6',    12, 14, 9.800, 'Michelin Alpin 6 — 205/55 R16 94H',            'Universale 16-inch'),
(65, 'CONTI-2254517SPORT',    'Gomë verore 225/45 R17',   12, 7,  10.500,'Continental SportContact 6 — 225/45 R17 94Y',  'Universale 17-inch'),
(66, 'PIRELLI-1856515CINT',   'Gomë verore 185/65 R15',   12, 13, 8.200, 'Pirelli Cinturato P1 — 185/65 R15 88H',        'VW Polo, Skoda Fabia');

-- ============ Kategoria 13: VAJRA DHE LËNGJE ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(67, 'CASTROL-5W30EDGE5L', 'Vaj motori Castrol Edge 5W-30 5L', 13, 11, 4.600, 'Vaj sintetik 5W-30 5 litra LongLife', 'Universale modern'),
(68, 'MOBIL-5W40-5L',      'Vaj motori Mobil 1 5W-40 5L',      13, 12, 4.700, 'Vaj sintetik 5W-40 5L',               'Universale modern'),
(69, 'TOTAL-5W30QUARTZ5L', 'Vaj motori Total Quartz 5W-30 5L', 13, 23, 4.600, 'Vaj sintetik 5W-30 5L',               'Universale modern'),
(70, 'LIQUI-1855-1L',      'Vaj kuti shpejtësisë 75W-90 1L',   13, 24, 0.950, 'Vaj sintetik për kutia manuale 1L',   'Universale'),
(71, 'CASTROL-G12-5L',     'Antifrizë G12 5L',                 13, 11, 5.500, 'Antifrizë rozë G12+ 5L i përqendruar', 'VW, Audi, Skoda, Seat');

-- ============ Kategoria 14: AKSESORË TË BRENDSHËM ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(72, 'GEN-MAT-RUB-4P',  'Set tapete gome 4 copë',           14, 30, 4.800, 'Tapete gome universale, 4 copë',          'Universale'),
(73, 'GEN-MAT-TEX-4P',  'Set tapete tekstil 4 copë',        14, 30, 2.500, 'Tapete tekstil me anti-rrëshqitje',       'Universale'),
(74, 'GEN-WHL-COV-LEA', 'Mbulesë volani prej lëkure',       14, 30, 0.300, 'Mbulesë volani lëkure 37-39cm',           'Universale'),
(75, 'GEN-SEAT-COV-FUL','Set mbulesa sediljesh komplet',    14, 30, 3.500, 'Set 9 copë mbulesa sediljesh',            'Universale'),
(76, 'GEN-USB-CHRG-2P', 'Karikues USB 12V me 2 porte',      14, 30, 0.150, 'Karikues 2× USB-A 3.1A + voltmetër',     'Universale 12V'),
(77, 'GEN-PHN-MNT-MAG', 'Mbajtëse telefoni magnetike',      14, 30, 0.180, 'Mbajtëse magnetike për dashboard',         'Universale'),
(78, 'GEN-AIR-FRSH-2P', 'Aroma makine 2 copë',              14, 30, 0.080, 'Aroma për ajroqarkullimi, 2 copë',        'Universale');

-- ============ Kategoria 15: AKSESORË TË JASHTËM ============
INSERT INTO pjeset (id, kodi_oem, emri, kategori_id, marka_id, pesha_kg, pershkrimi, model_kompatibil) VALUES
(79, 'BOSCH-WIPER-AERO','Furça xhami aerodinamike (set 2)',15, 1,  0.450, 'Set 2 furça xhami 60+45cm',                'VW Golf 5/6, Audi A3 8P'),
(80, 'CASTROL-POL-500', 'Polish karocerie 500ml',           15, 11, 0.620, 'Polish abrazive për gërvishtje sipërfaqe', 'Universale'),
(81, 'GEN-CLEAN-KIT-5', 'Kit pastrimi makine 5 copë',       15, 30, 1.800, 'Kit 5 produkte: shampoo, polish, etj.',   'Universale'),
(82, 'GEN-SUN-SHD-XL',  'Karton mbrojtës dielli (XL)',      15, 30, 0.450, 'Karton aluminizuar 145×80cm',             'Universale'),
(83, 'GEN-TIRE-INF-12V','Pompë gome 12V me manometër',      15, 30, 1.500, 'Kompresor portativ 12V 150PSI',           'Universale 12V'),
(84, 'GEN-WARN-TRI-EU', 'Triangull rrugor refleks (EU)',    15, 30, 0.850, 'Triangull i homologuar E4',                'Universale'),
(85, 'GEN-TOW-ROP-5T',  'Litar tërheqës 5m 3 tonë',         15, 30, 1.200, 'Litar tërheqës me grepa karabin 3T',       'Universale'),
(86, 'GEN-EM-VEST-OR',  'Jelek refleks portokalli',         15, 30, 0.180, 'Jelek refleks i homologuar EN ISO 20471', 'Universale'),
(87, 'K&N-RU-1740',     'Filtër ajri sportiv K&N',          15, 29, 0.520, 'Filtër konik me larje për performancë',    'Universale me adapter');


-- =============================================================================
-- 6. SEED DATA — Listimet (ofertat per shitës-pjesë)
-- Disa pjesë listohen nga shumë shitës me çmime të ndryshme (për krahasim)
-- =============================================================================

-- ============ Filtra: filtri Bosch listohet nga 5 shitës me çmime te ndryshme ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 1, 12.50, 50),    -- AutoPjese Tiranë
(2, 1, 11.80, 30),    -- Durrës Parts (më lirë)
(3, 1, 13.20, 25),    -- Korça Auto
(4, 1, 12.90, 20),    -- Vlora Motors
(5, 1, 13.50, 15);    -- Shkodra Spare

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 2,  8.90, 80),
(2, 2,  8.50, 60),
(1, 3,  9.50, 40),
(2, 3,  9.20, 35),
(3, 3,  9.80, 22);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 4, 14.50, 60),
(2, 4, 13.90, 45),
(4, 4, 14.20, 25);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 5, 38.00, 12),
(2, 5, 36.50, 8);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 6, 13.20, 30),
(3, 6, 12.80, 20),
(5, 6, 13.50, 18);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 7, 22.00, 40),
(2, 7, 21.50, 30);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 8, 15.50, 25),
(3, 8, 14.90, 18);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 9, 18.50, 35),
(2, 9, 17.90, 25),
(7, 9, 19.00, 15);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 10, 20.00, 22),
(3, 10, 19.50, 15);

-- ============ Frena ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 11, 95.00, 18),
(2, 11, 89.00, 12),
(3, 11, 99.00, 8),
(4, 11, 92.00, 10);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 12, 78.00, 20),
(2, 12, 74.50, 14);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 13, 65.00, 25),
(2, 13, 62.00, 20),
(3, 13, 68.00, 12),
(4, 13, 64.00, 15),
(5, 13, 66.00, 10);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 14, 55.00, 28),
(2, 14, 52.00, 22);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(2, 15, 35.00, 30),
(3, 15, 36.50, 18);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 16,  6.50, 100),
(2, 16,  6.20, 80),
(6, 16,  6.80, 50);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 17,  7.50, 60),
(7, 17,  7.80, 40);

-- ============ Motor ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 18, 28.00, 25),
(2, 18, 26.50, 18);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 19, 18.50, 40),
(2, 19, 17.80, 30),
(3, 19, 19.00, 20);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 20, 165.00, 12),
(2, 20, 158.00, 8);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 21, 48.00, 15),
(3, 21, 46.50, 10);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(2, 22, 52.00, 12);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 23, 95.00, 8),
(2, 23, 89.00, 5);

-- ============ Suspension ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 24, 145.00, 14),
(2, 24, 138.00, 10),
(3, 24, 149.00, 8);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 25, 95.00, 18),
(2, 25, 89.00, 12);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(2, 26, 158.00, 6);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 27, 68.00, 20),
(2, 27, 65.00, 15),
(3, 27, 70.00, 10);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 28, 42.00, 16);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 29, 38.00, 22),
(2, 29, 35.50, 18);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 30, 35.00, 20);

-- ============ Transmision ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 31, 285.00, 8),
(2, 31, 275.00, 5);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 32, 32.00, 15),
(2, 32, 30.50, 10);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 33, 145.00, 10);

-- ============ Sistemi Karburantit ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 34, 125.00, 12),
(2, 34, 118.00, 8);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 35, 95.00, 20),
(6, 35, 92.00, 15);

-- ============ Sistemi Ftohjes ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 36, 75.00, 18),
(2, 36, 72.00, 12);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 37, 22.00, 30),
(2, 37, 20.50, 22);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 38, 165.00, 8),
(2, 38, 155.00, 6);

-- ============ Sistemi Shkarkimit ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 39, 78.00, 14),
(6, 39, 75.00, 10);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 40, 85.00, 8),
(6, 40, 82.00, 6);

-- ============ Elektrik (Elektriku Online ka shumicën) ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 41,  4.50, 200),
(2, 41,  4.20, 150),
(3, 41,  4.80, 100),
(6, 41,  4.30, 250);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 42, 12.50, 80),
(6, 42, 11.80, 100);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 43,  5.50, 150),
(6, 43,  5.20, 120);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 44, 125.00, 15),
(2, 44, 118.00, 12),
(6, 44, 115.00, 20);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 45, 145.00, 10),
(6, 45, 138.00, 14);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 46, 135.00, 12),
(6, 46, 128.00, 15);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(2, 47, 165.00, 8),
(6, 47, 158.00, 10);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 48, 195.00, 8),
(6, 48, 185.00, 10);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 49, 175.00, 10),
(6, 49, 168.00, 12);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 50, 65.00, 25),
(6, 50, 62.00, 30);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 51, 95.00, 18),
(6, 51, 90.00, 22);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 52, 38.00, 30),
(6, 52, 35.50, 35);

-- ============ Ndriçim ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 53,  5.50, 200),
(6, 53,  5.20, 150),
(7, 53,  5.80, 100);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 54, 18.00, 60),
(6, 54, 16.50, 80),
(7, 54, 18.50, 40);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 55, 22.00, 50),
(6, 55, 20.50, 70);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 56,  6.50, 120),
(7, 56,  6.80, 80);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(6, 57, 85.00, 30),
(7, 57, 89.00, 20);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 58, 185.00, 6),
(6, 58, 178.00, 8);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 59, 125.00, 8),
(6, 59, 118.00, 10);

-- ============ Karrocerie ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 60, 145.00, 8),
(2, 60, 138.00, 6);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 61, 145.00, 8),
(2, 61, 138.00, 6);

-- ============ Goma dhe Rrota ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 62, 125.00, 20),
(2, 62, 118.00, 16),
(4, 62, 122.00, 12);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 63, 115.00, 18),
(2, 63, 108.00, 14);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 64, 135.00, 12),
(5, 64, 128.00, 10);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 65, 175.00, 8),
(2, 65, 168.00, 6);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 66, 78.00, 24),
(2, 66, 74.00, 20);

-- ============ Vajra dhe Lëngje ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 67, 48.00, 40),
(2, 67, 45.00, 30),
(3, 67, 49.00, 20),
(7, 67, 46.50, 35);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 68, 55.00, 30),
(2, 68, 52.00, 25),
(7, 68, 53.50, 28);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 69, 42.00, 35),
(2, 69, 39.50, 28);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 70, 18.50, 40),
(2, 70, 17.50, 30);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 71, 28.00, 35),
(2, 71, 26.00, 25);

-- ============ Aksesorë të Brendshëm (Auto Aksesore Tirana ka shumicën) ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 72, 22.00, 50),
(1, 72, 24.00, 30);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 73, 15.50, 70),
(1, 73, 16.50, 40);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 74,  9.50, 100),
(1, 74, 10.50, 60);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 75, 35.00, 40),
(1, 75, 38.00, 20);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 76,  8.50, 120),
(6, 76,  8.20, 80);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 77, 12.00, 80);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 78,  4.50, 200),
(1, 78,  5.00, 100);

-- ============ Aksesorë të Jashtëm ============
INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(1, 79, 24.00, 60),
(7, 79, 22.50, 80);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 80, 15.50, 50),
(1, 80, 16.50, 30);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 81, 28.00, 40),
(1, 81, 30.00, 25);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 82, 11.50, 70),
(1, 82, 12.50, 40);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 83, 32.00, 30),
(1, 83, 34.00, 20);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 84,  8.50, 100),
(1, 84,  9.50, 60);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 85, 18.50, 50),
(1, 85, 19.50, 30);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 86,  4.50, 200);

INSERT INTO listimet (shites_id, pjese_id, cmimi, stoku) VALUES
(7, 87, 65.00, 25);


-- =============================================================================
-- 7. SEED DATA — API keys testimi
-- =============================================================================
INSERT INTO api_keys (blerese_id, shites_id, api_key, aktive) VALUES
(1,    NULL, 'BLER-test-arben-7f3a2b1c9d8e0f1a', 1),
(5,    NULL, 'BLER-test-bega-4e5f6a7b8c9d0e1f',  1),
(NULL, 1,    'SHIT-test-autopjese-1a2b3c4d5e6f', 1),
(NULL, 6,    'SHIT-test-elektriku-9z8y7x6w5v4u', 1);


-- =============================================================================
-- VERIFIKIM I SHPEJTË (ekzekutohet pas import-it për të verifikuar të dhënat)
-- =============================================================================
SELECT 'Nivelet e discount-it:' AS info, COUNT(*) AS sasia FROM nivelet_discount
UNION ALL SELECT 'Zonat e transportit:',  COUNT(*) FROM zonat_transportit
UNION ALL SELECT 'Magazina:    ',         COUNT(*) FROM magazina
UNION ALL SELECT 'Kategoritë:',           COUNT(*) FROM kategorite
UNION ALL SELECT 'Markat:',               COUNT(*) FROM markat
UNION ALL SELECT 'Shitësit:',             COUNT(*) FROM shitesit
UNION ALL SELECT 'Blerësit:',             COUNT(*) FROM bleresit
UNION ALL SELECT 'Pjesët:',               COUNT(*) FROM pjeset
UNION ALL SELECT 'Listimet:',             COUNT(*) FROM listimet
UNION ALL SELECT 'API keys:',             COUNT(*) FROM api_keys;
