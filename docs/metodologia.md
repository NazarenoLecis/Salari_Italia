# Metodologia

## Unità statistica

Il repository integra tavole aggregate pubblicate da fonti ufficiali. Una riga del dataset armonizzato rappresenta una statistica riferita a una popolazione definita dalle dimensioni disponibili nella fonte.

La pipeline non interpreta una media settoriale come salario individuale e non ricostruisce una distribuzione completa partendo soltanto da media, mediana o pochi percentili.

## Concetti retributivi

Ogni osservazione specifica `pay_concept` e `pay_period`.

- `gross_earnings` indica la retribuzione lorda del lavoratore.
- `labour_cost` comprende la spesa sostenuta dal datore di lavoro secondo la definizione della fonte.
- `low_wage_earners` indica la quota sotto la soglia definita dalla Structure of Earnings Survey.
- `gender_pay_gap_unadjusted` indica la differenza percentuale non corretta tra le retribuzioni orarie medie di uomini e donne.
- `gender_pay_gap_adjusted` indica la componente unexplained della decomposizione Blinder-Oaxaca Eurostat su SES 2022.
- `gender_pay_gap_decomposition` contiene le componenti della stessa decomposizione: parte spiegata complessiva e contributi di età, istruzione, occupazione, anzianità, contratto, orario, settore, dimensione, controllo dell'impresa e localizzazione.

Retribuzione mensile e annuale incorporano anche differenze nelle ore, nei mesi lavorati e nella continuità occupazionale. La retribuzione oraria misura un oggetto diverso e viene mantenuta separata.

Nelle tavole Eurostat SES mensili e annuali il codice `working_time` deve essere letto esplicitamente. `TOTAL` combina lavoratori a tempo pieno e part-time; `FT` e `PT` separano i due gruppi; `TOT_FTE` e `PT_FTE` riportano grandezze in equivalenti full-time quando pubblicate. Per confronti di livelli annuali tra paesi o nel tempo, `TOT_FTE` o `FT` sono generalmente piu' interpretabili del solo `TOTAL`.

## Territorio

`geography_basis` identifica il significato geografico del dato.

- `reporting_country` indica il paese che trasmette la statistica.
- Le future fonti italiane dovranno distinguere residenza del lavoratore, luogo di lavoro, sede dell'impresa e unità locale.

I dati comunali basati sulle dichiarazioni fiscali descrivono il territorio di residenza e possono includere redditi che non derivano da lavoro dipendente. Non vengono assimilati automaticamente ai salari del luogo di lavoro.

## Armonizzazione

La pipeline conserva i codici originali delle classificazioni e le relative etichette. ISCO, NACE, ISCED, classi di età e dimensioni d'impresa non vengono ricodificate in categorie più larghe senza un mapping documentato.

Le dimensioni originali di ogni osservazione vengono conservate in `dimensions_json`. Questo campo consente di verificare l'esatta cella della tavola di origine.

## Indicatori derivati

Quando D1, mediana e D9 sono disponibili per la stessa popolazione, la pipeline calcola:

- `d9_d1`;
- `d9_median`;
- `median_d1`.

I rapporti vengono calcolati soltanto tra osservazioni che condividono anno, territorio e tutte le altre dimensioni. Non vengono combinati percentili riferiti a popolazioni diverse.

Il gender pay gap adjusted non viene stimato dalla pipeline a partire da aggregati pubblici. Viene riportato solo quando una fonte ufficiale pubblica una decomposizione già documentata. Nel caso Eurostat 2025, la componente adjusted/unexplained corregge per caratteristiche osservate nei microdati SES 2022, ma non deve essere letta automaticamente come sola discriminazione perché restano variabili non osservate e segregazioni più fini delle classificazioni disponibili.

## Qualità e riservatezza

I flag pubblicati dalla fonte vengono conservati in `quality_flag`. Valori provvisori, stimati, interrotti o riservati devono essere interpretati sulla base dei metadati della fonte.

Le tavole territoriali molto granulari possono essere soppresse o aggregate per proteggere la riservatezza. L'assenza di una cella non equivale a zero.
