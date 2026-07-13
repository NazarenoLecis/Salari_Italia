# Matrice di copertura

| Dimensione | Eurostat SES | Altre fonti | Stato nel repository |
|---|---:|---|---|
| Media, D1, mediana e D9 | Sì, orario/mensile/annuale | INPS o microdati per maggiore dettaglio | Implementato |
| Sesso | Sì | ISTAT, INPS | Implementato per Eurostat e ISTAT RACLI |
| Età | Sì | ISTAT, INPS | Implementato per Eurostat e ISTAT RACLI |
| Professione | Sì, ISCO | ISTAT | Implementato per Eurostat |
| Settore economico | Sì, NACE | ISTAT, INPS | Implementato per Eurostat e ISTAT RACLI Ateco |
| Tempo pieno e part-time | Sì | ISTAT, INPS | Implementato per Eurostat e ISTAT RACLI |
| Dimensione d'impresa | Sì, tavole SES 2022 | ISTAT, INPS | Implementato per Eurostat 2022 e ISTAT RACLI |
| Titolo di studio | Sì, tavole SES 2022 e quota low-wage | ISTAT, EU-SILC o microdati SES | Implementato per Eurostat 2022 e ISTAT RACLI |
| Anzianità lavorativa | Sì, tavole SES 2022 | ISTAT, INPS | Implementato per Eurostat 2022 |
| Qualifica contrattuale | No; disponibile solo proxy professione/manuale-non manuale in alcune tavole | ISTAT, INPS, contratti collettivi | Implementato per ISTAT RACLI |
| Tempo determinato/indeterminato | Sì, tavole SES 2022 `emp_cont` | ISTAT, INPS | Implementato per Eurostat 2022 e ISTAT RACLI |
| Pubblico/privato | Non separato nelle richieste iniziali | RGS, ARAN, INPS, ISTAT | Da mappare |
| Regione | No nella tavola europea acquisita | ISTAT, INPS, MEF | Disponibile come territorio ISTAT quando pubblicato in RACLI |
| Provincia | No | INPS, MEF, eventuali tavole ISTAT | Implementato per ISTAT RACLI |
| Comune | No | MEF per residenza fiscale | Da mappare con limiti |
| Salario orario | Sì | ISTAT | Implementato |
| Retribuzione mensile | Sì | ISTAT, INPS, MEF | Implementato per Eurostat |
| Retribuzione annuale | Sì | INPS, ISTAT, MEF | Implementato per Eurostat |
| Retribuzione netta | No nelle tavole integrate | MEF, Eurostat net earnings per casi tipo | Non stimata |
| Reddito dichiarato | No | MEF dichiarazioni fiscali | Da mappare separatamente |
| Imponibile contributivo | No | INPS | Da mappare separatamente |
| Costo del lavoro | Sì | ISTAT | Implementato |
| Gender pay gap | Sì, non corretto; adjusted/decomposizione nella pubblicazione Eurostat SES 2022 | Elaborazioni su microdati | Implementato unadjusted annuale e adjusted/decomposizione 2022 |
| Dipendenti e autonomi | SES riguarda dipendenti | INPS, ISTAT, MEF | Da mappare senza mescolare perimetri |
| Cittadinanza/nazionalità | No nelle tavole integrate | ISTAT, INPS | Paese di nascita implementato per ISTAT RACLI; cittadinanza da mappare |

Una cella indicata come implementata significa che il codice di acquisizione e armonizzazione è presente. La disponibilità effettiva dipende dalle osservazioni pubblicate dalla fonte per paese e anno.
