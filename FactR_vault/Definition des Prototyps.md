## 🌟 Definition: Wann ist der Prototyp abgeschlossen?

### 💻 Plattform und Architektur
- [ ] Die Anwendung läuft stabil und vollständig **unter Linux (Desktop)**.
- [ ] Die Architektur folgt dem Prinzip:  
  ➔ **GUI ↔ Controller ↔ Module ↔ Projekt/Datenstruktur**

---

### ✅ Vollständig implementierte Module

Die folgenden **sechs Module** sind vollständig implementiert – das umfasst:
- [ ] Interne **Logik**
- [ ] **GUI**
- [ ] **Kommunikation** mit anderen Modulen (über den Controller)
- [ ] Daten werden im Projekt gespeichert und beim Laden wiederhergestellt

#### 1. 📄 SourceAnalyzer
- [ ] Interne **Logik**
    - [ ] Arbeitet mit **Textquellen** (Markdown)
    - [ ] Markiert Inhalte mit Tags (z. B. Argument, Frage, These)
    - [ ] Darstellung farblich hervorgehoben
    - [ ] Quellen lassen sich laden, darstellen, markieren
- [ ] **GUI**
- [ ] **Kommunikation** mit anderen Modulen (über den Controller)
- [ ] Daten werden im Projekt gespeichert und beim Laden wiederhergestellt


#### 2. 💬 PromptCreator
- [ ] Interne **Logik**
    - [ ] Eingabemaske für neue Thesen, Argumente, Fragen etc.
    - [ ] Verknüpfung mit Quelle oder Marker möglich
    - [ ] Speichert neue Einträge (als Objekte)
- [ ] **GUI**
- [ ] **Kommunikation** mit anderen Modulen (über den Controller)
- [ ] Daten werden im Projekt gespeichert und beim Laden wiederhergestellt


#### 3. 📚 Collection
- [ ] Interne **Logik**
    - [ ] Zeigt alle gespeicherten Prompts
    - [ ] Sortierung und Filter nach Tag, Quelle, Datum etc.
    - [ ] Reagiert dynamisch auf neue Prompts (z. B. durch PromptCreator)
- [ ] **GUI**
- [ ] **Kommunikation** mit anderen Modulen (über den Controller)
- [ ] Daten werden im Projekt gespeichert und beim Laden wiederhergestellt

#### 4. 🧠 Visualizer
- [ ] Interne **Logik**
    - [ ] Zeigt alle gespeicherten Prompts
    - [ ] Sortierung und Filter nach Tag, Quelle, Datum etc.
    - [ ] Reagiert dynamisch auf neue Prompts (z. B. durch PromptCreator)
    - [ ] Darstellung von Argumentationsstrukturen als Mindmap
    - [ ] Verknüpfungen zwischen Thesen, Argumenten etc. sichtbar
    - [ ] Interaktive Ansicht, mindestens lesbar und klickbar
- [ ] **GUI**
- [ ] **Kommunikation** mit anderen Modulen (über den Controller)
- [ ] Daten werden im Projekt gespeichert und beim Laden wiederhergestellt


#### 5. 📆 Timeline
- [ ] Interne **Logik**
    - [ ] Darstellung zeitlicher Abläufe (Quellen, Marker etc.)
    - [ ] Visualisiert Reihenfolge, Clusterung oder Entwicklung
    - [ ] Erkennt Tageswechsel automatisch
- [ ] **GUI**
- [ ] **Kommunikation** mit anderen Modulen (über den Controller)
- [ ] Daten werden im Projekt gespeichert und beim Laden wiederhergestellt

#### 6. 🥷 Keys
- [ ] Interne **Logik** 
    - [ ] Verwaltung von Schlüsselbegriffen:
        - [ ]Personen
        - [ ] Orte
        - [ ] Ereignisse
    - [ ]Zeigt Verbindungen zu Quellen, Prompts, Zeitpunkten
    - [ ]Ermöglicht spätere Recherche oder Zusammenfassung überblicksartig
- [ ] **GUI**
- [ ] **Kommunikation** mit anderen Modulen (über den Controller)
- [ ] Daten werden im Projekt gespeichert und beim Laden wiederhergestellt

---

### 🧱 Strukturelle Anforderungen
- [ ] Projekt kann erstellt und geladen werden (`*.proj`)
- [ ] Projekt enthält:
  - [ ] Pfade
  - [ ] Erstellungsdatum
  - [ ] Verwendete Module
  - [ ] Markierungen, Quellen, Prompts
- [ ] Der Controller vermittelt erfolgreich:
  - [ ] Module ↔ GUI
  - [ ] Module ↔ Module
  - [ ] Projekt ↔ Module

---

### ❌ Nicht Teil des Prototyps
- [ ] Keine Nutzerverwaltung / Accounts
- [ ] Kein Netzwerk / Synchronisation / Mehrbenutzersystem
- [ ] Keine Medienintegration (Bilder, Audio etc.)
- [ ] Kein Undo / Redo
- [ ] Keine Web-Version (Desktop first)

---

### ✅ Abgeschlossen ist der Prototyp, wenn:
1. Die App startet und lädt ein bestehendes Projekt korrekt.
2. Alle 6 Module sind verwendbar, speichern ihre Inhalte und kommunizieren.
3. Ein reales Rechercheprojekt kann in der App vollständig erfasst und dargestellt werden.
4. Die App ist benutzbar, auch wenn sie noch nicht hübsch oder optimiert ist.

