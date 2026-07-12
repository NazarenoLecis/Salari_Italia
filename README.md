# Salari Italia

Repository per costruire una base dati riproducibile e una dashboard sulla distribuzione delle retribuzioni in Italia.

Il progetto distingue sempre il concetto retributivo, il periodo di riferimento e la popolazione osservata. Retribuzione lorda, reddito da lavoro, imponibile contributivo, costo del lavoro e salario contrattuale non vengono trattati come misure equivalenti.

## Obiettivi

- descrivere media, mediana, decili e altre misure della distribuzione salariale;
- confrontare retribuzioni per sesso, età, professione, settore, orario di lavoro e dimensione d'impresa;
- aggiungere progressivamente titolo di studio, qualifica, contratto, pubblico o privato e territorio;
- distinguere territorio di residenza, luogo di lavoro e sede dell'impresa;
- integrare fonti italiane e confronti europei mantenendo definizioni e copertura verificabili.

## Stato iniziale

La pipeline implementa le fonti Eurostat che possono essere scaricate tramite Dissemination API:

- `earn_ses_hourly`: distribuzione delle retribuzioni orarie lorde della Structure of Earnings Survey;
- `earn_ses_monthly`: distribuzione delle retribuzioni mensili lorde della Structure of Earnings Survey;
- `earn_ses_annual`: distribuzione delle retribuzioni annuali lorde della Structure of Earnings Survey;
- tavole `earn_ses22_*`: retribuzioni medie 2022 per istruzione, contratto, anzianità, professione, età e dimensione d'impresa;
- `earn_ses_pub1s`: quota di lavoratori a bassa retribuzione;
- `earn_ses_pub1a` e `earn_ses_pub1i`: quota di lavoratori a bassa retribuzione per età e istruzione;
- `earn_gr_gpgr2`: divario retributivo di genere non corretto;
- `lc_lci_lev`: livelli del costo orario del lavoro.

Le fonti ISTAT, INPS e MEF sono censite nella documentazione e verranno collegate solo dopo aver definito endpoint, classificazioni e unità statistiche comparabili.

## Struttura

```text
src/salari_italia/       codice della pipeline
scripts/                 esecuzione delle fasi operative
dashboard/               applicazione Streamlit
docs/                    metodologia, fonti e dizionario dati
tests/                   test automatici
data/                     dati e controlli generati dalla pipeline
```

## Installazione

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Esecuzione

```bash
python scripts/run_pipeline.py
streamlit run dashboard/app.py
```

Per modificare i paesi scaricati:

```bash
SALARI_GEOGRAPHIES=IT,DE,FR,ES,NL,EU27_2020 python scripts/run_pipeline.py
```

Gli output vengono salvati in:

- `data/processed/salari_eurostat.csv`;
- `data/processed/salari_eurostat.json`;
- `data/processed/salari_eurostat.parquet`;
- `data/processed/salari_dashboard.json`;
- `data/validation/pipeline_report.json`.

Il workflow `update-data.yml` esegue la pipeline il primo giorno di ogni mese alle 04:00 UTC e può essere avviato manualmente. CSV, JSON, payload dashboard e rapporto di validazione vengono aggiornati su `main`; raw, file intermedi e Parquet restano fuori da Git.

## Schema dati

Lo schema armonizzato usa una riga per osservazione statistica. Le dimensioni principali sono anno, territorio, sesso, età, istruzione, professione, settore, contratto, orario, dimensione d'impresa, concetto retributivo, statistica, percentile, valore e unità di misura.

La documentazione completa è in:

- `docs/metodologia.md`
- `docs/fonti.md`
- `docs/dizionario_dati.md`
- `docs/matrice_copertura.md`
