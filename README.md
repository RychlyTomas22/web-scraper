# Web scraper a analýza článků iDNES.cz

Starší lokální projekt v Pythonu pro sběr odkazů na články iDNES.cz, získání údajů z článků a jejich následnou analýzu, vizualizaci a volitelný import do MySQL.

> Tento repozitář je dodatečný upload již dokončeného projektu. Projekt původně nevznikal v Gitu, takže zde není jeho průběžná historie commitů. Skripty odrážejí původní lokální prostředí; jejich běh proti současné podobě webu nebyl znovu ověřen.

## Co obsahuje

| Soubor | Úloha |
| --- | --- |
| `articlecolletor.py` | Sbírá odkazy na články podle kategorií a ukládá je do `article_links.json`. |
| `articleprocessor.py` | Načítá odkazy, z článků získává nadpis, text, datum, počet obrázků a komentářů a ukládá je do `articles_data.json`. |
| `cleaner.py` | Odstraňuje z `articles_data.json` záznamy bez textu a duplicitní titulky. Soubor přepisuje. |
| `data_analyzer.py` | Vypisuje statistiky nad nasbíranými články. |
| `data_visualizer.py` | Vytváří grafy z nasbíraných článků. |
| `uploadToSQL.py` | Volitelně importuje články do MySQL. |
| `QueryDB.py` | Spouští ukázkové SQL dotazy nad importovanými články. |

## Požadavky

- Python 3 a balíčky z `requirements.txt`
- Google Chrome a odpovídající ChromeDriver pro sběr článků
- MySQL pouze pro `uploadToSQL.py` a `QueryDB.py`

Nainstalujte závislosti:

```bash
python -m pip install -r requirements.txt
```

V obou skriptech pro sběr jsou cesty k prohlížeči a ChromeDriveru pevně nastavené podle původního počítače. Před spuštěním upravte `chrome_options.binary_location` a `chrome_driver_path` podle svého prostředí. `articleprocessor.py` také nastavuje `cs_CZ.UTF-8`; pokud tento název locale systém nepodporuje, je potřeba toto nastavení upravit nebo odstranit (názvy českých měsíců skript převádí vlastní tabulkou).

## Postup

Příkazy spouštějte z kořenové složky projektu, protože skripty používají relativní cesty k souborům.

1. `python articlecolletor.py` vytvoří `article_links.json`.
2. `python articleprocessor.py` načte odkazy a vytvoří `articles_data.json`.
3. Volitelně spusťte `python cleaner.py`; předem si ponechte kopii dat, pokud chcete zachovat původní výstup.
4. `python data_analyzer.py` vypíše statistiky.
5. Pro `python data_visualizer.py` nejprve vytvořte složku `graphs/data_vizualizer/`, do které skript ukládá PNG grafy.

`article_links.json` a `articles_data.json` jsou generovaná data a v repozitáři nejsou. Sběr používá selektory původního webu a může vyžadovat úpravy, pokud se struktura stránek od té doby změnila.

## MySQL (volitelné)

Pro import je třeba mít vlastní databázi a tabulku `articles` se sloupci `title`, `article_text`, `image_count`, `time_date`, `comments_count` a `category`. SQL soubor pro vytvoření databáze ani data nejsou součástí repozitáře.

Před použitím nastavte připojení v `uploadToSQL.py` a `QueryDB.py` podle své lokální MySQL. Potom lze spustit `python uploadToSQL.py` a `python QueryDB.py`. Import očekává již vytvořený `articles_data.json`.
