# Fonti

## Fonti implementate

### Eurostat Structure of Earnings Survey

`earn_ses_hourly` contiene statistiche sulle retribuzioni orarie lorde. La pipeline acquisisce media, D1, mediana e D9 per il totale e media/mediana per sesso, età, professione, settore e regime di orario quando le celle sono pubblicate.

`earn_ses_monthly` e `earn_ses_annual` aggiungono gli stessi indicatori distributivi per retribuzioni mensili e annuali lorde. Non vengono convertite tra loro: ogni periodo retributivo resta una misura distinta. Per queste due tavole la pipeline acquisisce anche le categorie di orario `TOTAL`, `FT`, `PT`, `TOT_FTE` e `PT_FTE` quando pubblicate, cosi' la dashboard puo' distinguere i totali grezzi dai valori in equivalenti full-time.

Le tavole `earn_ses22_15`, `earn_ses22_16`, `earn_ses22_17`, `earn_ses22_18`, `earn_ses22_22`, `earn_ses22_23`, `earn_ses22_28`, `earn_ses22_29` e `earn_ses22_30` coprono l'edizione 2022 della SES e sono usate per contratto, istruzione, anzianità lavorativa, dimensione d'impresa, professione, età e settore. Sono trattate come punti 2022, non come serie storiche.

La SES è quadriennale e riguarda il perimetro definito nei metadati Eurostat. La copertura non coincide necessariamente con l'intera occupazione e può escludere imprese molto piccole o specifici settori.

### Eurostat low-wage earners

`earn_ses_pub1s` misura la quota di dipendenti con retribuzione oraria lorda inferiore a due terzi della mediana nazionale. La soglia è relativa alla distribuzione del singolo paese.

`earn_ses_pub1a` e `earn_ses_pub1i` estendono la stessa misura per classe di età e titolo di studio.

### Eurostat gender pay gap

`earn_gr_gpgr2` misura il divario retributivo di genere non corretto. Il dato non controlla per professione, settore, anzianità, istruzione, orario o altre caratteristiche.

La pubblicazione Eurostat `KS-01-25-035`, "Gender pay gaps in the European Union - 2025 edition", integra la decomposizione Blinder-Oaxaca basata su microdati `SES 2022`. La tabella 2 viene acquisita come fonte ufficiale separata per `gender_pay_gap_decomposition` e `gender_pay_gap_adjusted`. L'indicatore adjusted corrisponde alla componente unexplained/residua della decomposizione ed è un benchmark 2022, non una serie annuale.

### Eurostat labour cost levels

`lc_lci_lev` riporta livelli del costo orario del lavoro. Il costo del lavoro non coincide con la retribuzione lorda ricevuta dal dipendente.

### OECD average annual wages

`DSD_EARNINGS@AV_AN_WAGE` misura il salario medio annuo per dipendente equivalente full-time nell'economia totale. La pipeline acquisisce la serie in `EUR` a prezzi costanti/base 2025 quando la fonte la pubblica; non converte autonomamente i paesi non-euro da valute nazionali o dollari PPP.

### Eurostat Labour Force Survey

Le tavole LFS `lfsa_ergan`, `lfsa_argan`, `une_rt_a` e `lfsa_eppga` sono integrate come indicatori annuali di contesto: tasso di occupazione 20-64, tasso di attivita' 20-64, tasso di disoccupazione 15-74 e quota di occupati part-time 15-64.

Queste serie servono per controllare composizione e dinamica del mercato del lavoro quando una serie salariale sembra anomala. Non sono filtri della SES e non devono essere fuse con le celle retributive: hanno fonte, popolazione e definizioni proprie.

### ISTAT

La pipeline integra ISTAT RACLI, famiglia `533_957`, "Retribuzioni orarie dei dipendenti del settore privato". I dataflow `533_957_DF_DCSC_RACLI_8`-`24` sono usati per dettaglio territoriale provinciale e settori Ateco a due cifre.

Le misure pubbliche integrate sono retribuzione oraria lorda media, primo decile, mediana e nono decile. Non sono microdati e non consentono di ricostruire un istogramma completo della distribuzione individuale.

Le dimensioni integrate includono sesso, età, titolo di studio, paese di nascita, contratto, regime orario, dimensione d'impresa, qualifica contrattuale, giornate retribuite, provincia e settore Ateco. Il perimetro è il settore privato dipendente.

Stato: `implementato`.

## Fonti italiane da collegare

### INPS

Gli osservatori amministrativi INPS possono coprire retribuzioni imponibili e giornate lavorate per categorie di dipendenti, territorio, sesso, età, qualifica e caratteristiche del rapporto. Ogni archivio ha un proprio perimetro contributivo e non descrive automaticamente tutti i lavoratori.

Stato: `da_mappare`.

### MEF, dichiarazioni fiscali

Le statistiche sulle dichiarazioni possono aggiungere redditi da lavoro dipendente e assimilati per comune di residenza. La variabile è fiscale, annuale e riferita ai contribuenti. Non identifica direttamente professione, luogo di lavoro o salario orario.

Stato: `da_mappare`.

## Fonti complementari

Le fonti seguenti possono essere usate per pannelli specifici senza sostituire le statistiche generali sui salari:

- ARAN e Conto annuale RGS per il pubblico impiego;
- AlmaLaurea per gli esiti occupazionali dei laureati;
- Eurostat EU-SILC per redditi individuali e familiari;
- Labour Force Survey per caratteristiche dell'occupazione, quando la variabile retributiva e la granularità sono adeguate.

Ogni integrazione deve indicare se il dato riguarda persone, rapporti di lavoro, contribuenti, imprese o famiglie.
