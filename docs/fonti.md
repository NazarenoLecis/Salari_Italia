# Fonti

## Fonti implementate

### Eurostat Structure of Earnings Survey

`earn_ses_hourly` contiene statistiche sulle retribuzioni orarie lorde. La pipeline acquisisce media, D1, mediana e D9 per il totale e media/mediana per sesso, età, professione, settore e regime di orario quando le celle sono pubblicate.

`earn_ses_monthly` e `earn_ses_annual` aggiungono gli stessi indicatori distributivi per retribuzioni mensili e annuali lorde. Non vengono convertite tra loro: ogni periodo retributivo resta una misura distinta.

Le tavole `earn_ses22_15`, `earn_ses22_16`, `earn_ses22_17`, `earn_ses22_18`, `earn_ses22_22`, `earn_ses22_23`, `earn_ses22_28`, `earn_ses22_29` e `earn_ses22_30` coprono l'edizione 2022 della SES e sono usate per contratto, istruzione, anzianità lavorativa, dimensione d'impresa, professione, età e settore. Sono trattate come punti 2022, non come serie storiche.

La SES è quadriennale e riguarda il perimetro definito nei metadati Eurostat. La copertura non coincide necessariamente con l'intera occupazione e può escludere imprese molto piccole o specifici settori.

### Eurostat low-wage earners

`earn_ses_pub1s` misura la quota di dipendenti con retribuzione oraria lorda inferiore a due terzi della mediana nazionale. La soglia è relativa alla distribuzione del singolo paese.

`earn_ses_pub1a` e `earn_ses_pub1i` estendono la stessa misura per classe di età e titolo di studio.

### Eurostat gender pay gap

`earn_gr_gpgr2` misura il divario retributivo di genere non corretto. Il dato non controlla per professione, settore, anzianità, istruzione, orario o altre caratteristiche.

### Eurostat labour cost levels

`lc_lci_lev` riporta livelli del costo orario del lavoro. Il costo del lavoro non coincide con la retribuzione lorda ricevuta dal dipendente.

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
