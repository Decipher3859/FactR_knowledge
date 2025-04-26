


### controller.py
- [ ] statt ```set_module_manager``` vielleicht alle Hauptklassen Singleton gestalten?

### database_manager.py
- [ ] Die Datenbank bezieht sich im Moment noch auf jedes einzelne Projekt. Da ich auch Projekte mergen möchte oder zumindest Schnittmengen bilden will, macht es wahrscheinlich Sinn, eine Datenbank pro User anzulegen.
### project.py
- [ ] ```self.source_file_path = os.path.join(self.project_path, "source", "text.md")```
	- [ ] Bezieht sich momentan nur auf "text.md". Das ist eine Beipsieldatei. Eigentlich sollen alle Dateien im Source-Ordner verwaltet werden.
- [ ] delete_tag_entry() löscht eine Zeile. Wenn mehrere Zeilen getaggt werden, funktioniert die Methode nicht mehr
- [ ] Ich habe schonmal die .proj vorbereitet, damit ich mit weniger Abhängigkeiten an die Wichtigen Infos komme. Noch nicht implementiert ist zum beispiel, dass das Programm die Pfade da raus zieht.
```
project_data = {
	"project_name": self.project_name,
	"created_at": datetime.now().isoformat(),
	"database": {
		"host": "localhost",
		"user": "DAuser",
		"password": "5J#Y2j8B6hFwhpNvY67Gv#EJaXGpc2ZM",
	},
	"tags": [],
	"parameter": [],
	"paths": {
		"project_path": self.project_dir,
		"source_folder": os.path.join(self.project_dir, "sources")
	}
```
### gui.py
- [ ]  ```self.project.create_discourse_project()```
	- [ ] Überschreibt das aktuelle Projekt jedes Mal. Muss erst prüfen, ob Projekt schon vorhanden ist und dann entweder laden oder neu erstellen.
- [ ] ```def remove_tag(self):```
	- [ ] remove_tag() hat keinen selected_text übergeben bekommen. Das ist für vie Verwaltung der Listen oder später Datenbanken aber wichtig, weil remove_tag() so nie die id oder quelle weiterverarbeiten kann, wenn sie den textinhalt nicht kennt.
	- [ ] Wenn die aufgerufen wird, ```action.triggered.connect(self.remove_tag)```  muss remove_tag(selected_text) ergänzt werden und mit lambda ausgeführt. ```action.triggered.connect(lambda: self.remove_tag(selected_text))```

## source_analyzer.py
- [ ] ```show_inline_menu(self, event)``` kann bisher nur taggen oder löschen. es sollte auch tags umwandeln können, wenn bereits getaggt wurde.

### tag_manager.py

- [ ] Zu den Tags "Argument" 'arg' ergänzen. Manches ist halt nicht eindeutig ein Beleg, sondern nur ein Argument für eine These.