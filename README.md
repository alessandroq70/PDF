# 📎 Unisci PDF

App web semplice per **unire due o più file PDF** in un unico documento.
Selezioni i file, li ordini come vuoi, e al salvataggio l'app ti **chiede dove
salvare** il risultato.

## Caratteristiche

- Selezione di **2 o più PDF** (clic o trascinamento).
- **Riordino** dei file prima dell'unione (frecce su/giù): l'ordine determina
  l'ordine delle pagine nel documento finale.
- Rimozione dei singoli file e pulsante per svuotare l'elenco.
- Al salvataggio apre un vero dialogo **"Salva con nome"** su Chrome ed Edge
  (i browser predefiniti su Windows), così scegli cartella e nome del file.
  Sugli altri browser il file viene scaricato nella cartella Download.

## Requisiti

- [Python 3.9+](https://www.python.org/downloads/) installato
  (durante l'installazione su Windows spunta *"Add Python to PATH"*).

## Avvio rapido (Windows)

1. Scarica/clona questa cartella.
2. Fai **doppio clic su `run.bat`**.
   - Al primo avvio crea l'ambiente e installa le dipendenze (ci vuole un minuto).
   - Si apre automaticamente il browser su <http://127.0.0.1:5000>.
3. Per chiudere l'app, premi `CTRL+C` nella finestra del terminale.

## Avvio manuale (qualsiasi sistema)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Poi apri <http://127.0.0.1:5000> nel browser.

## Come si usa

1. Clicca sull'area tratteggiata (o trascina i PDF) per aggiungere i file.
2. Riordina i file con le frecce ▲ ▼ se necessario.
3. Clicca **"Unisci e salva"** e scegli dove salvare il PDF unito.

## Struttura del progetto

```
.
├── app.py              # Server web Flask (route / e /merge)
├── pdf_merger.py       # Logica di unione dei PDF (testabile in isolamento)
├── templates/
│   └── index.html      # Interfaccia
├── static/
│   ├── app.js          # Logica lato browser (selezione, ordine, salvataggio)
│   └── style.css       # Stile
├── tests/
│   └── test_merge.py   # Test della logica di unione
├── requirements.txt    # Dipendenze Python
└── run.bat             # Avvio rapido su Windows
```

## Test

```bash
pip install pytest
pytest
```

## Note

- I file vengono elaborati **in locale**, sul tuo computer: nulla viene
  inviato a internet.
- Limite di caricamento predefinito: 200 MB totali (modificabile in `app.py`).
