# Praxisnachbereitung Tag 1 – ETL mit Excel & Git

Dieses Repository dokumentiert die Bearbeitung der Übungsaufgabe „Tag 1 – ETL mit Excel · Git-Einstieg“. Ziel war es, reale CSV-Daten zu bereinigen, zusammenzuführen, visuell auszuwerten und die Arbeitsschritte mit Git zu versionieren.

## Struktur des Repositories

- `excel/`  
  - `Geraete.csv` – Rohdaten zu Geräten  
  - `Ausleihen.csv` – Rohdaten zu Ausleihen  
  - `Mitarbeiter.csv` – Rohdaten zu Mitarbeitern  
  - `Praxis Nachbereitung Übung Tag 1.xlsx` – Excel-Arbeitsmappe mit Import, Bereinigung, Gesamttabelle und Auswertungen  
  - `Gesamt_bereinigt.csv` – exportierte, bereinigte Gesamttabelle  
- `excel.py` – kurzes Python-Skript zum Einlesen der Excel-/CSV-Daten  
- `README.md` – diese Dokumentation

## Arbeitsablauf

1. **Git-Vorbereitung**
   - Neues Repository lokal (und optional auf GitHub) angelegt.  
   - Ordnerstruktur erstellt (`excel/`) und CSV-Dateien hineinkopiert.  
   - Erster Commit mit Startdateien.

2. **Datenimport in Excel**
   - Neue Excel-Arbeitsmappe angelegt.  
   - Import der drei CSV-Dateien (`Geraete`, `Ausleihen`, `Mitarbeiter`) jeweils auf eigene Tabellenblätter.  
   - Import-Einstellungen: Trennzeichen `;`, Zeichensatz UTF‑8, Datum im Format `TT.MM.JJJJ`.

3. **Datenbereinigung**
   - Vollständig leere Zeilen entfernt.  
   - Spaltenüberschriften vereinheitlicht  
   - Datentypen geprüft und korrigiert:
     - IDs als Zahl bzw. Text konsistent  
     - Datumswerte als Datum formatiert  
     - Preise/Netto-Kaufpreise als Zahl formatiert  
     - Ausleih und Rückgabedaten machen z.T. keinen Sinn

4. **Datenzusammenführung**
   - Geräte mit Ausleihen über die Spalte `Gerätenummer` verknüpft.  
   - Ausleihen mit Mitarbeiterdaten über `Mitarbeiter-ID` ergänzt.  
   - Ergebnis als kombinierte **Gesamttabelle** auf einem neuen Blatt `C.2 gesamt` abgelegt.  
   - Wo sinnvoll, Hilfsspalten angelegt (z.B. Status „offen/geschlossen“, Kennzeichen für aktuelle Einsätze).

5. **Visuelle Analyse (PivotTables & Diagramme)**
   - Aufbau von PivotTables auf Basis der Gesamttabelle:
     1. **Gesamtwert nicht im Einsatz befindlicher Geräte**  
        - Filter/Logik über Rückgabedatum, um Geräte zu identifizieren, die aktuell nicht im Einsatz sind.  
        - Summierung des Netto-Kaufpreises dieser Geräte.  
     2. **Ausleihen vom Gerätetyp „Laptop“**  
        - Filter (in Tabelle oder Pivot) auf `Geräte.Gerätetyp = "Laptop"`.  
        - Plausibilitätscheck: Anzahl und Verteilung der Laptop-Ausleihen geprüft.
     3. **Ausleihen pro Gerätetyp**  
        - Pivot: Zeilen = Gerätetyp, Werte = Anzahl der Ausleihen.  
        - Visualisierung als Säulen- oder Kreisdiagramm.
     4. **Gerätetyp + Standort**  
        - Erweiterung der Pivot: Zeilen = Gerätetyp, Spalten = Geräte-Standort.  
        - Visualisierung als gestapeltes Säulendiagramm zur Verteilung der Ausleihen pro Gerätetyp und Standort.

6. **Export & Python-Anbindung**
   - Bereinigte Gesamttabelle manuell als `Gesamt_bereinigt.csv` (UTF‑8) exportiert.  
   - Kurzes Python-Skript erstellt, das die bereinigte Tabelle (CSV oder Excel) einliest, um die Anbindung an weitere Auswertungen zu demonstrieren.

7. **Git-Workflow**
   - Mehrere sinnvolle Commits durchgeführt, z.B.:
     - `Startdateien hinzugefügt`  
     - `Daten bereinigt und Gesamttabelle erstellt`  
     - `Pivot-Auswertungen und Diagramme ergänzt`  
     - `Bereinigte CSV exportiert und Python-Skript hinzugefügt`  
   - (Optional) Push auf ein Remote-Repository (GitHub) mit sichtbarer Commit-Historie.

## Wichtige Erkenntnisse

- **Datenqualität:** Bereits kleine Inkonsistenzen (z.B. Datumsformat, leere oder fehlerhafte IDs) erschweren die Auswertung und müssen früh bereinigt werden.  
- **PivotTables:** PivotTables sind sehr flexibel, um unterschiedliche Sichten auf dieselben Daten zu erzeugen (z.B. nach Gerätetyp, Standort, Mitarbeiter).  
- **Reproduzierbarkeit:** Die Trennung von Rohdaten (CSV), bereinigter Gesamttabelle und den abgeleiteten Pivot-Auswertungen macht den Prozess nachvollziehbar und wiederholbar.  
- **Git:** Auch bei reinen Excel-Workflows hilft Versionskontrolle dabei, Arbeitsschritte zu dokumentieren und auf frühere Stände zurückspringen zu können.
