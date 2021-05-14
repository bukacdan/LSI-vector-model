# LSI Vektorový model

## Popis projektu
Cílem projektu bylo vytvořit webovou aplikaci implementující LSI vektorový model k vyhledávání nad kolekcí textových dokumentů. 

Vstupem do vyhledávacího formuláře je textový dotaz uživatele, podobně jako u klasických webových vyhledávačů, a hodnota přepínače, která určuje, zda bude vyhledáváno v kolekci sekvenčně, nebo optimalizovaně pomocí LSI vektorového modelu.

Výstupem aplikace je seřazený seznam náhledů dokumentů z kolekce, které nejpřesněji odpovídají zadanému dotazu. Daný náhled je možno rozkliknout a přečíst v plném rozsahu.

## Způsob řešení
### Data
Za zdroj textových dat byl vybrán dataset [20 newsgroups](http://qwone.com/~jason/20Newsgroups/) obsahující přibližně 20 tisíc textových dokumentů rozdělených téměř rovnoměrně do 20 kategorií. Tento dataset je stahován přímo pomocí [knihovní funkce](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_20newsgroups.html) v scikit-learn.

### Čištění dat
Textová data mohou obsahovat nežádoucí šum, proto bylo potřeba je pročistit. S dokumenty byly postupně prováděny tyto úpravy:
1. převod na malá písmena
2. odstranění e-mailových adres
3. odstranění non-alfabetických znaků
4. lemmatizace
5. odstranění krátkých slov

### Tvorba vyhledávacího modelu
Nejprve byla vytvořena term-by-document matice o rozměrech (<počet dokumentů>, <počet termů>). Hodnoty v ní byly převáženy pomocí tf-idf schématu. Tato matice byla dále dekomponována pomocí singular-value-decomposition (SVD) na matice:
* **u**
    * rozměry: (<počet dokumentů>, <k = počet konceptů>)
    * concept-by-document matice
* **s**
    * rozměry: (<n = počet konceptů>, )
    * vektor konceptů
* **vt**
    * rozměry: (<k = počet konceptů>, <počet termů>)
    * concept-by-term matice

### Hledání optimálního počtu konceptů
Cílem bylo nalézt optimální počet $k$ konceptů tak, aby $k$ bylo co nejnižší (kvůli rychlosti vyhledávání) a výsledky zároveň co nejpřesnější.

### Zobrazení dotazu do prostoru konceptů
Dále bylo zapotřebí zobrazit lematizovaný dotaz uživatele jako vektor do prostoru konceptů, následně změřit kosinovou vzdálenost $v$ tohoto vektoru od vektorů ostatních dokuemntů.


## Implementace

### Programovací jazyk a technologie
K vývoji byl použit programovací jazyk [Python](https://www.python.org/) a mikro webový framework [Flask](https://flask.palletsprojects.com/en/1.1.x/).

Při testování dílčích částí algoritmu byl využit [Jupyter notebook](../logic/logic.ipynb).

Celá aplikace je kontejnerizovaná v [Dockeru](https://www.docker.com/) a spouštěná pomocí [Docker Compose](https://docs.docker.com/compose/).

### Knihovny
* [Pandas](https://pandas.pydata.org/) k analýze a provádění souhrnných transformací nad daty
* [Numpy](https://numpy.org/) a [Scipy](https://www.scipy.org/) k práci s maticemi
* [NLTK](https://www.nltk.org/) k analýze a zpracování přirozeného jazyka
* [scikit-learn](https://scikit-learn.org/stable/) k tvorbě LSI modelu
* [Kneed](https://kneed.readthedocs.io/en/stable/) k hledání zlomu v křivce počtu konceptů

### Stavba aplikace
Veškerá logika aplikace se nachází v modulu [lsiModel](https://gitlab.fit.cvut.cz/latkamat/lsi-vector-model/blob/master/web/lsiModel.py) ve třídě LSI. 

Důležité třídní metody:
* `prepare`
    * pokud není lokálně stažen dataset s dokumenty, stáhne je
    * pročistí dokumenty
    * vytvoří model pro vyhledávání (ten se vytvoří pouze jednou při inicializaci, poté už zůstává uvnitř třídy)

* `svd_optimal_k`
    * nalezne optimální počet konceptů

* `process_query`
    * zpracuje dotaz uživatele na slova a promítne jej do prostoru konceptů
    * změří kosinovou podobnost mezi dotazem a dokumenty
    * lematizuje dotaz
    * vrátí seznam dokumentů odpovídajících dotazu

* `process_query_seq`
    * rozdělí dotaz uživatele na slova
    * pro každé slovo sekvenčně prochází term-by-document matici a vrací dokumenty, ve kterých se slovo nachází

Třídu je při prvním spuštění třeba inicializovat. Tato operace může trvat 1-2 minuty. Aplikace do konzole vypisuje, která fáze inicializace právě probíhá, we webovém prostředí běží waiting gif.

Když uživatel potvrdí dotaz ve formuláři na hlavní stránce, je tento dotaz předán LSI třídě. Ta dotaz vyhodnotí a vrátí seznam výsledných dokumentů. Ty jsou zobrazeny v seznamu výsledků.

## Ukázka vstupu
![vstup uživatele](./img/user_input.png)
uživatel zadal vstup "washington" a nevybral možnost vyhledávat sekvenčně

![výsledky vyhledávání](./img/search_results.png)
Aplikace vrátila výsledky za 0.15s, bylo zobrazeno prvních 100 výsledků.

Ke každému dotazu jsou uvedena následující data:
* původní dotaz
* lematizovaný dotaz
* úhlová vzdálenost výsledku
* index dokumentu
* kategorie dokumentu

![detail výsledku](./img/results_detail.png)
V horní části obrazovky je původní text (před čištěním) v plném rozsahu Pod ním jsou uvedeny podobné dokumenty.

## Experimentální sekce
Nejprve bylo potřeba určit optimální počet $k$ konceptů. Byly testovány hodnoty $k$ z intervalu $\langle 1, 200 \rangle$ a pozorovány hodnoty v matici $S$ při singular value decomposition.

![optimální počet komponent](./img/optimal_components_search.png)

Na ose x je zobrazen počet konceptů, na ose y hodnoty singular values tedy "důležitost" konceptů. Křivka se lomí v bodě x=15.

V dalším experimentu byly zkoušeny hodnoty pro $k$ z intervalu $\langle 1, 50\rangle$ inkrementované vždy po dvou (pro více hodnot trval výpočet příliš dlouho). Zároveň bylo pro každou hodnotu $k$ zkoušeno zpracování dotazu s lemmatizací i bez. Výsledky byly zkoušeny na čtyřech různých dotazech.

![výsledky hledání pro různé k](./img/experiment.png)

V grafech je vidět, že pro nižší hodnoty $k$ je kosinová vzdálenost menší, nicméně při prozkoumání výsledných dokumentů se ukázalo, že obsahově nejsou příliš relevantní vzhledem k dotazu.
Růst funkce průměrné kosinové vzdálenosti v závislosti na $k$ se definitivně zpomaluje okolo bodu $k=15$, což odpovídá nalezenému optimálnímu počtu konceptů v předchozím experimentu.

Zároveň se ukázalo, že lemmatizace dotazu nemá žádný vliv na výsledky (křivka průměrné vzdálenosti s lemmatizací překrývá křivku průměrné vzdálenosti bez lemmatizace).

## Diskuze
Největším problémem modelu je, že pokud je mu zadán dotaz, ze kterého není možné extrahovat žádný term získaný z datasetu, tedy vektor tohoto dotazu je nulový, všechny dokumenty v kolekci jsou stejně dobré, tedy mají stejnou kosinovou vzdálenost. Model proto vrátí jako nejlepší výsledek první dokument v kolekci (shodou náhod o Pittsburg Penguins a Jaromíru Jágrovi).

Dalším nedostatkem je řešení sekvenčního prohledávání. V ideálním případě by mělo být realizováno pomocí nastavení počtu konceptů $k$ na maximální hodnotu (v tomto případě počet dokumentů). Pro takto vysokou hodnotu (téměř 20000) však nestačila operační paměť a program zkolaboval.

## Závěr
Podařilo se implementovat LSI vektorový model k information retrieval. Při zadání dotazu, z něhož lze extrahovat alespoň 1 term získaný z datasetu, model vrací relevantní výsledky, zároveň je možné pro každý dokument z množiny výsledků najít a zobrazit podobné dokumenty.

Při řešení jsme se potýkali s menšími problémy, zvlášť bylo nutné vyladit správné promítání dotazu do prostoru konceptů. Drobné zádrhely nastaly i při práci s webovým GUI.

Projekt hodnotíme jako zajímavý a přínosný.