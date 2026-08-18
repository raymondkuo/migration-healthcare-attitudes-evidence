#!/usr/bin/env bash
# Retry the sources that blocked the plain downloader, using a full Chrome header set.
set -u
# derive the workspace from this script's own location, so no local path is baked in
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

fetch () {  # fetch <url> <outfile> <referer>
  curl -sL --compressed --max-time 120 \
    -A "$UA" \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,application/pdf,*/*;q=0.8' \
    -H 'Accept-Language: en-US,en;q=0.9,es;q=0.8,it;q=0.7,he;q=0.6,ko;q=0.5' \
    -H 'sec-ch-ua: "Chromium";v="126", "Google Chrome";v="126", "Not-A.Brand";v="99"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "Windows"' \
    -H 'Sec-Fetch-Dest: document' \
    -H 'Sec-Fetch-Mode: navigate' \
    -H 'Sec-Fetch-Site: none' \
    -H 'Sec-Fetch-User: ?1' \
    -H 'Upgrade-Insecure-Requests: 1' \
    ${3:+-e "$3"} \
    -o "$2" -w "  %{http_code}  %{size_download} bytes  %{content_type}\n" "$1"
}

echo "== MEX  IOM/UPMRIP Boletin de Estadisticas Migratorias 2023"
fetch "https://mexico.iom.int/sites/g/files/tmzbdl1686/files/documents/2024-03/estadisticas-migratorias-2023.pdf" \
      "$BASE/countries/MEX_Mexico/sources/irregular_proxy_detections__UPMRIP_SEGOB_boletin_2023.pdf" \
      "https://mexico.iom.int/"

echo "== ISR  Population and Immigration Authority, Foreigners in Israel 2022 Q1"
fetch "https://www.gov.il/BlobFolder/generalpage/foreign_workers_stats/he/zarim_2022_q1.pdf" \
      "$BASE/countries/ISR_Israel/sources/irregular_stock__PIBA_zarim_2022_q1.pdf" \
      "https://www.gov.il/he/pages/foreign_workers_stats"

echo "== CHE  SEM Sans-Papiers in der Schweiz 2015"
fetch "https://www.sem.admin.ch/dam/sem/de/data/internationales/illegale-migration/sans_papiers/ber-sanspapiers-2015-d.pdf" \
      "$BASE/countries/CHE_Switzerland/sources/irregular_stock__SEM_sanspapiers_2015.pdf" \
      "https://www.sem.admin.ch/"

echo "== KOR  Korean National Police University press"
fetch "https://press.police.ac.kr/pds/1476878914562.pdf" \
      "$BASE/countries/KOR_South_Korea/sources/irregular_proxy_overstayers__KNPU_press_2015.pdf" \
      "https://press.police.ac.kr/"

echo "== ITA  ISMU XXV Rapporto 2019"
fetch "https://www.ismu.org/comunicato-stampa-xxv-rapporto-ismu/" \
      "$BASE/countries/ITA_Italy/sources/irregular_stock__ISMU_XXV_rapporto_2019.html" \
      "https://www.ismu.org/"

echo "== ITA  ISMU XXVII Rapporto 2021"
fetch "https://www.ismu.org/xxvii-rapporto-sulle-migrazioni-2021-comunicato-stampa-11-2-2022/" \
      "$BASE/countries/ITA_Italy/sources/irregular_stock__ISMU_XXVII_rapporto_2021.html" \
      "https://www.ismu.org/"

echo "== ITA  Cinformi on ISMU XXVI Rapporto 2020"
fetch "https://www.cinformi.it/Comunicazione/Notizie/I-dati-del-Rapporto-ISMU-sulle-migrazioni-2020" \
      "$BASE/countries/ITA_Italy/sources/irregular_stock__Cinformi_ISMU_XXVI_2020.html" \
      "https://www.cinformi.it/"

echo "== JPN  nisshinkyo mirror of MOJ overstayer table"
fetch "https://www.nisshinkyo.org/news/pdf/G-26-2.pdf" \
      "$BASE/countries/JPN_Japan/sources/irregular_proxy_overstayers__nisshinkyo_G-26-2.pdf" \
      "https://www.nisshinkyo.org/"

echo
echo "== resulting file sizes =="
for f in \
  "$BASE/countries/MEX_Mexico/sources/irregular_proxy_detections__UPMRIP_SEGOB_boletin_2023.pdf" \
  "$BASE/countries/ISR_Israel/sources/irregular_stock__PIBA_zarim_2022_q1.pdf" \
  "$BASE/countries/CHE_Switzerland/sources/irregular_stock__SEM_sanspapiers_2015.pdf" \
  "$BASE/countries/KOR_South_Korea/sources/irregular_proxy_overstayers__KNPU_press_2015.pdf" \
  "$BASE/countries/ITA_Italy/sources/irregular_stock__ISMU_XXV_rapporto_2019.html" \
  "$BASE/countries/ITA_Italy/sources/irregular_stock__ISMU_XXVII_rapporto_2021.html" \
  "$BASE/countries/ITA_Italy/sources/irregular_stock__Cinformi_ISMU_XXVI_2020.html" \
  "$BASE/countries/JPN_Japan/sources/irregular_proxy_overstayers__nisshinkyo_G-26-2.pdf" ; do
  if [ -f "$f" ]; then printf "%10s  %s\n" "$(stat -c%s "$f")" "$(basename "$f")"; fi
done
