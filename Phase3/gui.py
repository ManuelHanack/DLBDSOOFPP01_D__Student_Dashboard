# -*- coding: utf-8 -*-
"""
Modul: gui.py
Autor: Manuel Hanack (Matrikelnummer: IU14156336)
Studiengang: B.Sc. Cyber Security
Beschreibung:
    View-Schicht der Tkinter-GUI.
    Reine Präsentationskomponente im MVC-Muster. Delegiert alle Steuerungsaufgaben an den DashboardController.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from controller import DashboardController

class StudentDashboardApp:
    """
    GUI-Hauptfenster für das Studien-Dashboard.
    Nutzt das IU-Farbschema und interagiert ausschließlich mit dem DashboardController.
    """
    def __init__(self, root: tk.Tk, controller: DashboardController):
        self.root = root
        self.controller = controller
        self.root.title("IU Student Progress Dashboard")
        self.root.geometry("1100x780")
        self.root.minsize(950, 650)

        # IU Corporate Colors
        self.COLOR_PRIMARY = "#002F4B"     # IU Dunkelblau
        self.COLOR_ACCENT = "#2B4C7E"      # Sekundärblau
        self.COLOR_BG = "#F4F6F9"          # HintergrundHellgrau
        self.COLOR_CARD = "#FFFFFF"        # Kartenweiß
        self.COLOR_TEXT = "#2C3E50"        # Text Dunkel
        self.COLOR_HIGHLIGHT = "#008B8B"   # Akzent Teal

        self.root.configure(bg=self.COLOR_BG)
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.build_ui()
        self.refresh_ui()

    def build_ui(self) -> None:
        """Erstellt das Layout der Benutzeroberfläche."""
        main_container = tk.Frame(self.root, bg=self.COLOR_BG, padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Header (Stammdaten)
        info = self.controller.get_student_info()
        header_frame = tk.Frame(main_container, bg=self.COLOR_PRIMARY, padx=20, pady=15)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title_lbl = tk.Label(header_frame, text="IU STUDENT PROGRESS DASHBOARD", font=("Segoe UI", 16, "bold"), fg="white", bg=self.COLOR_PRIMARY)
        title_lbl.pack(anchor="w")

        sub_text = f"Studierender: {info['name']} | Matrikelnr.: {info['matrikelnummer']} | Studiengang: {info['studiengang']} (Teilzeit, {info['regelsesemester']} Sem.)"
        sub_lbl = tk.Label(header_frame, text=sub_text, font=("Segoe UI", 10), fg="#E0E0E0", bg=self.COLOR_PRIMARY)
        sub_lbl.pack(anchor="w", pady=(5, 0))

        # 2. KPI Cards Frame
        self.kpi_frame = tk.Frame(main_container, bg=self.COLOR_BG)
        self.kpi_frame.pack(fill=tk.X, pady=(0, 15))

        self.card_ects = self._create_kpi_card(self.kpi_frame, "ECTS-FORTSCHRITT", "0 / 180 ECTS", "Soll: 45 ECTS (Sem. 2)")
        self.card_ects.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.card_grade = self._create_kpi_card(self.kpi_frame, "NOTENDURCHSCHNITT", "0.00", "Ziel: <= 2.0 (ECTS-gewichtet)")
        self.card_grade.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 10))

        self.card_status = self._create_kpi_card(self.kpi_frame, "MODUL-STATUS", "0 Offen | 0 In Arb.", "0 von 29 bestanden")
        self.card_status.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 3. Progress Bar Frame
        progress_frame = tk.Frame(main_container, bg=self.COLOR_CARD, padx=15, pady=12, highlightbackground="#DCDCDC", highlightthickness=1)
        progress_frame.pack(fill=tk.X, pady=(0, 15))

        p_top = tk.Frame(progress_frame, bg=self.COLOR_CARD)
        p_top.pack(fill=tk.X, pady=(0, 5))

        tk.Label(p_top, text="Gesamter Studienfortschritt (180 ECTS Ziel)", font=("Segoe UI", 10, "bold"), fg=self.COLOR_TEXT, bg=self.COLOR_CARD).pack(side=tk.LEFT)
        self.lbl_progress_pct = tk.Label(p_top, text="0.0 %", font=("Segoe UI", 10, "bold"), fg=self.COLOR_HIGHLIGHT, bg=self.COLOR_CARD)
        self.lbl_progress_pct.pack(side=tk.RIGHT)

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X)

        # 4. Filter & Action Toolbar
        toolbar = tk.Frame(main_container, bg=self.COLOR_BG)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(toolbar, text="Semester:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG, fg=self.COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 5))
        self.combo_sem = ttk.Combobox(toolbar, values=["Alle", "Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6"], state="readonly", width=12)
        self.combo_sem.set("Alle")
        self.combo_sem.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_sem.bind("<<ComboboxSelected>>", self.on_filter_changed)

        tk.Label(toolbar, text="Status:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG, fg=self.COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 5))
        self.combo_status = ttk.Combobox(toolbar, values=["Alle", "Offen", "In Bearbeitung", "Bestanden"], state="readonly", width=15)
        self.combo_status.set("Alle")
        self.combo_status.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_status.bind("<<ComboboxSelected>>", self.on_filter_changed)

        btn_edit = tk.Button(toolbar, text="✏️ Note / Status eintragen", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PRIMARY, fg="white", activebackground=self.COLOR_ACCENT, activeforeground="white", relief=tk.FLAT, padx=10, pady=4, command=self.open_grade_dialog)
        btn_edit.pack(side=tk.RIGHT)

        # 5. Module Treeview Table
        table_frame = tk.Frame(main_container, bg=self.COLOR_CARD, highlightbackground="#DCDCDC", highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("code", "name", "ects", "semester", "note", "status", "versuch")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("code", text="Modul-Code")
        self.tree.heading("name", text="Modul-Bezeichnung")
        self.tree.heading("ects", text="ECTS")
        self.tree.heading("semester", text="Sem.")
        self.tree.heading("note", text="Note")
        self.tree.heading("status", text="Status")
        self.tree.heading("versuch", text="Versuch")

        self.tree.column("code", width=130, anchor="center")
        self.tree.column("name", width=380, anchor="w")
        self.tree.column("ects", width=60, anchor="center")
        self.tree.column("semester", width=60, anchor="center")
        self.tree.column("note", width=80, anchor="center")
        self.tree.column("status", width=130, anchor="center")
        self.tree.column("versuch", width=70, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_kpi_card(self, parent: tk.Widget, title: str, main_val: str, sub_val: str) -> tk.Frame:
        card = tk.Frame(parent, bg=self.COLOR_CARD, padx=15, pady=12, highlightbackground="#DCDCDC", highlightthickness=1)
        
        lbl_t = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg="#7F8C8D", bg=self.COLOR_CARD)
        lbl_t.pack(anchor="w")

        lbl_m = tk.Label(card, text=main_val, font=("Segoe UI", 16, "bold"), fg=self.COLOR_PRIMARY, bg=self.COLOR_CARD)
        lbl_m.pack(anchor="w", pady=(3, 2))

        lbl_s = tk.Label(card, text=sub_val, font=("Segoe UI", 8), fg="#555555", bg=self.COLOR_CARD)
        lbl_s.pack(anchor="w")

        card.lbl_main = lbl_m
        card.lbl_sub = lbl_s
        return card

    def refresh_ui(self) -> None:
        """Lädt die Daten vom Controller neu und aktualisiert die UI-Komponenten."""
        # KPIs abfragen
        kpis = self.controller.get_kpis()

        self.card_ects.lbl_main.config(text=f"{kpis['aktuell_ects']} / {kpis['ziel_ects']} ECTS")
        self.card_ects.lbl_sub.config(text=f"Soll-Stand: {kpis['soll_ects']} ECTS (Sem. 2)")

        schnitt_text = f"{kpis['notenschnitt']:.2f}" if kpis['notenschnitt'] > 0 else "N/A"
        self.card_grade.lbl_main.config(text=schnitt_text)

        self.card_status.lbl_main.config(text=f"{kpis['offen_cnt']} Offen | {kpis['in_bearbeitung_cnt']} In Arb.")
        self.card_status.lbl_sub.config(text=f"{kpis['bestanden_cnt']} von {kpis['gesamt_module']} bestanden")

        # Progress bar
        pct = kpis['fortschritt_prozent']
        self.progress_bar['value'] = pct
        self.lbl_progress_pct.config(text=f"{pct:.1f} %")

        # Modultabelle befüllen
        for item in self.tree.get_children():
            self.tree.delete(item)

        sem_filter = self.combo_sem.get()
        status_filter = self.combo_status.get()
        filtered_modules = self.controller.get_filtered_modules(sem_filter, status_filter)

        for m in filtered_modules:
            note_str = f"{m.note:.1f}" if m.note is not None else "-"
            # Find semester
            sem_num = 1
            for sem in self.controller.studiengang.semester_liste:
                if m in sem.module:
                    sem_num = sem.nummer
                    break

            self.tree.insert("", tk.END, values=(
                m.code,
                m.name,
                m.ects,
                f"Sem. {sem_num}",
                note_str,
                m.status.value,
                m.pruefungsleistung.versuch
            ))

    def on_filter_changed(self, event: Any = None) -> None:
        self.refresh_ui()

    def open_grade_dialog(self) -> None:
        """Öffnet den Dialog zur Noteneingabe für das ausgewählte Modul."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie zuerst ein Modul aus der Tabelle aus.")
            return

        item_values = self.tree.item(selected[0], "values")
        code = item_values[0]
        modul_name = item_values[1]
        current_note = item_values[4]
        current_status = item_values[5]
        current_versuch = item_values[6]

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Note eintragen: {code}")
        dialog.geometry("420x320")
        dialog.configure(bg=self.COLOR_BG)
        dialog.transient(self.root)
        dialog.grab_set()

        container = tk.Frame(dialog, bg=self.COLOR_BG, padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text=modul_name, font=("Segoe UI", 10, "bold"), fg=self.COLOR_PRIMARY, bg=self.COLOR_BG, wraplength=360, justify="left").pack(anchor="w", pady=(0, 15))

        # Form fields
        form = tk.Frame(container, bg=self.COLOR_BG)
        form.pack(fill=tk.X, pady=(0, 15))

        tk.Label(form, text="Status:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG).grid(row=0, column=0, sticky="w", pady=5)
        combo_dialog_status = ttk.Combobox(form, values=["Offen", "In Bearbeitung", "Bestanden"], state="readonly")
        combo_dialog_status.set(current_status)
        combo_dialog_status.grid(row=0, column=1, sticky="e", pady=5)

        tk.Label(form, text="Note (IU Notenskala):", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG).grid(row=1, column=0, sticky="w", pady=5)
        entry_note = ttk.Entry(form)
        entry_note.insert(0, current_note if current_note != "-" else "")
        entry_note.grid(row=1, column=1, sticky="e", pady=5)

        tk.Label(form, text="Versuch (1 - 3):", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG).grid(row=2, column=0, sticky="w", pady=5)
        spin_versuch = ttk.Spinbox(form, from_=1, to=3, width=18)
        spin_versuch.set(current_versuch)
        spin_versuch.grid(row=2, column=1, sticky="e", pady=5)

        def save() -> None:
            status_val = combo_dialog_status.get()
            note_raw = entry_note.get().strip().replace(",", ".")
            versuch_val = int(spin_versuch.get())

            note_val: Optional[float] = None
            if note_raw:
                try:
                    note_val = float(note_raw)
                except ValueError:
                    messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Zahl für die Note ein.")
                    return

            try:
                # Controller aufrufen zur Validierung und Speicherung
                self.controller.update_module_grade(code, note_val, status_val, versuch_val)
                messagebox.showinfo("Erfolg", f"Modul '{code}' erfolgreich aktualisiert!")
                dialog.destroy()
                self.refresh_ui()
            except Exception as ex:
                messagebox.showerror("Validierungsfehler", str(ex))

        btn_save = tk.Button(container, text="Speichern", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PRIMARY, fg="white", relief=tk.FLAT, padx=15, pady=5, command=save)
        btn_save.pack(anchor="e")
