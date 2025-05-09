Die Anwendung basiert auf PyQt5 und folgt dem Prinzip der Trennung von GUI, Controller und Modulen, was eine klare Kommunikation und Modularität zwischen den verschiedenen Bereichen ermöglicht. Der Controller vermittelt die Kommunikation zwischen den Modulen, steuert die Datenverwaltung und koordiniert die Interaktion zwischen den Komponenten.

**Modules:**

- Das erste Modul, das implementiert wurde, ist die **PromptCollection**. Es stellt eine GUI zur Verfügung, die es dem Benutzer ermöglicht, alle gespeicherten "Prompts" in einer Tabelle anzuzeigen. Die Tabelle listet Kategorien, Positionen, Inhalte und Quellen auf und ermöglicht eine dynamische Aktualisierung der Anzeige, wenn neue Prompts hinzugefügt werden. Dieses Modul ist vollständig in die Architektur integriert und funktioniert wie erwartet: Die Kommunikation zwischen der **PromptCollection** und der zugrunde liegenden Datenbank läuft über den Controller und stellt sicher, dass neue Daten korrekt angezeigt werden. Die **Datenbank** selbst speichert und lädt die Prompts, wobei sie auf Änderungen reagiert und die Anzeige entsprechend anpasst.
    

**Controller und Datenverwaltung:**

- Der **Controller** steuert die verschiedenen Module und ermöglicht deren Kommunikation untereinander. Es wird sichergestellt, dass alle Module ihre jeweiligen Daten speichern und beim Laden eines Projekts wiederhergestellt werden. Das Speichern von Daten wie Prompts, Quellen und Markierungen wird effizient gehandhabt, sodass sie beim nächsten Laden des Projekts zugänglich sind.
    

**Projekterstellung und -verwaltung:**

- Ein grundlegendes **Projekt**-System wurde noch nicht vollständig implementiert, aber es gibt Fortschritte in der Verwaltung und Speicherung von Daten innerhalb des Controllers. Ein **Projekt** soll später Pfade, Erstellungsdaten, verwendete Module sowie alle relevanten Daten wie Markierungen und Quellen umfassen. Die Logik für das Speichern und Laden eines Projekts ist jedoch teilweise vorhanden.
    

**GUI und Interaktive Elemente:**

- Die **GUI** der App wurde so entworfen, dass sie einfach und funktional ist, aber die Benutzeroberfläche könnte noch weiter optimiert werden, um die Benutzerfreundlichkeit zu erhöhen. Die grundlegende Interaktivität, wie das Anzeigen von Daten in der Tabelle der **PromptCollection**, ist bereits implementiert, jedoch sind noch weitere UI-Elemente für die anderen Module erforderlich, um eine vollständige Benutzererfahrung zu gewährleisten.
    

**Zukünftige Module:**

- Weitere Module wie **SourceAnalyzer**, **PromptCreator**, **Visualizer**, **Timeline** und **Keys** müssen noch implementiert werden. Jedes dieser Module wird spezifische Funktionalitäten hinzufügen, wie z. B. das Markieren von Texten, die Verwaltung von Schlüsselbegriffen, die Darstellung von Argumentationsstrukturen und Zeitabläufen. Sobald diese Module entwickelt sind, wird die Kommunikation zwischen den Modulen über den Controller weiter ausgebaut.
    

**Nicht implementierte Funktionen:**

- Funktionen wie eine Nutzerverwaltung, Netzwerk-Synchronisation, Undo/Redo sowie die Web-Version sind momentan nicht Teil des Prototyps und könnten in späteren Phasen des Projekts hinzugefügt werden. Ebenso fehlt noch die Integration von Medien (Bilder, Audio), was eine erweiterte Funktionalität darstellen würde.
    

Insgesamt befindet sich das Projekt in einer stabilen Entwicklungsphase, wobei die Grundfunktionen der App weitgehend implementiert sind. Die Anwendung kann starten, Daten laden und eine erste Interaktion mit gespeicherten Prompts ermöglichen. Es ist jedoch noch Arbeit erforderlich, um die restlichen Module zu integrieren und die Benutzeroberfläche weiter zu verfeinern, um die vollständige Funktionalität und Benutzerfreundlichkeit des Prototyps zu gewährleisten.