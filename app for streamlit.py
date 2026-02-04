import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from load_and_clean import load_and_clean
from wet_dry_classification import classify_wet_dry
from spell_analysis import extract_spells
from rainfall_statistics import rainfall_intensity_stats
from synthetic_rainfall_generator import generate_synthetic
from harvest_summary import compute_harvest, summarize_harvest
from reference_table_builder import build_reliability_table
from export_results import export_results_to_json
from export_results import export_results_to_json




class MCSApp(tk.Tk):
    
    

    def export_json(self):
        if self.harvest_summary is None or self.reliability_table is None:
            messagebox.showwarning(
                "No Results",
                "Please run the analysis before exporting."
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Save Results as JSON",
        )

        if not path:
            return

        try:
            metadata = {
                "roof_area_per_class_m2": self.roof.get(),
                "number_of_classrooms": self.cls.get(),
                "students_per_class": self.studs.get(),
                "demand_L_per_student_per_day": self.demand.get(),
                "simulation_years": int(
                    self.harvest_df["synthetic_year"].nunique()
                ),
            }

            export_results_to_json(
                output_path=path,
                metadata=metadata,
                harvest_summary=self.harvest_summary,
                reliability_table=self.reliability_table,
            )

            messagebox.showinfo(
                "Export Successful",
                f"Results exported successfully:\n{path}"
            )

        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            self.harvest_summary = None
            self.reliability_table = None
            self.harvest_df = None

    def __init__(self):
        super().__init__()
        self.title("MCS – Rainwater Harvesting Decision Support Tool")
        self.geometry("1100x750")
        self.harvest_summary = None
        self.reliability_table = None
        self.harvest_df = None
        self.raw_df = None
        self._build_ui()

    def _build_ui(self):
        # ================= ROOT CONTAINER =================
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        # ================= FILE UPLOAD =================
        upload = ttk.LabelFrame(root, text="1. Upload Raw Rainfall CSV")
        upload.pack(fill=tk.X, pady=6)

        self.path_var = tk.StringVar()
        ttk.Entry(upload, textvariable=self.path_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=6
        )
        ttk.Button(upload, text="Browse", command=self.upload_csv).pack(
            side=tk.LEFT, padx=6
        )
        
        


        # ================= PARAMETERS =================
        params = ttk.LabelFrame(root, text="2. School Parameters")
        params.pack(fill=tk.X, pady=6)

        self.roof = tk.DoubleVar(value=63.0)
        self.cls = tk.IntVar(value=4)
        self.studs = tk.IntVar(value=40)
        self.demand = tk.DoubleVar(value=5.0)

        grid = ttk.Frame(params)
        grid.pack(fill=tk.X, padx=6, pady=4)

        fields = [
            ("Roof area / classroom (m²)", self.roof),
            ("Number of classrooms", self.cls),
            ("Students / classroom", self.studs),
            ("Demand (L / student / day)", self.demand),
        ]

        for r, (lbl, var) in enumerate(fields):
            ttk.Label(grid, text=lbl).grid(row=r, column=0, sticky="w", pady=2)
            ttk.Entry(grid, textvariable=var, width=10).grid(row=r, column=1, pady=2)

        # ================= RUN BUTTON =================
        ttk.Button(
            root,
            text="3. Compute Harvest & Tank Reliability",
            command=self.run_pipeline
        ).pack(pady=8)

        
        self.export_btn = ttk.Button(
            root,
            text="4. Export Results to JSON",
            command=self.export_json,
            state=tk.DISABLED
        )
        self.export_btn.pack(pady=6)
        
        # ================= OUTPUT AREA =================
        output_frame = ttk.LabelFrame(root, text="Results")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        self.output = tk.Text(output_frame, wrap="word")
        self.output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            output_frame, orient="vertical", command=self.output.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output.config(yscrollcommand=scrollbar.set)

    # ================= FILE LOAD =================
    def upload_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        try:
            self.raw_df = load_and_clean(path)
            self.path_var.set(path)
            messagebox.showinfo("Loaded", "Rainfall data loaded successfully.")
        except Exception as e:
            messagebox.showerror("File Error", str(e))

    # ================= PIPELINE =================
    def run_pipeline(self):
        if self.raw_df is None:
            messagebox.showwarning("Missing Data", "Please upload a CSV first.")
            return

        def task():
            try:
                self.output.delete("1.0", tk.END)

                # ---- Synthetic Rainfall ----
                hist = classify_wet_dry(self.raw_df)
                spells = extract_spells(hist)
                intensity = rainfall_intensity_stats(hist)
                synth = generate_synthetic(spells, intensity)

                # ---- Harvest ----
                harvest_df = compute_harvest(
                    synth,
                    roof_area=self.roof.get(),
                    classrooms=self.cls.get(),
                    runoff_coeff=0.9,
                    gutter_eff=0.95,
                    first_flush=2.0,
                )

                harvest = summarize_harvest(harvest_df)

                # ---- DISPLAY HARVEST FIRST ----
                self.output.insert(tk.END, "HARVEST POTENTIAL\n")
                self.output.insert(
                    tk.END,
                    f"Annual Harvest: {harvest['annual_L']:,.0f} L / year\n\n"
                )

                self.output.insert(tk.END, "Monthly Harvest (L):\n")
                for m, v in harvest["monthly_L"].items():
                    self.output.insert(tk.END, f"  Month {m}: {v:,.0f}\n")

                # ---- Tank Reliability ----
                daily_demand = (
                    self.cls.get() * self.studs.get() * self.demand.get()
                )

                table = build_reliability_table(
                    harvest_df,
                    tank_sizes=range(500, 30001, 500),
                    daily_demand_L=daily_demand,
                )
                
                # ---- EXPORT TO JSON ----
                metadata = {
                    "roof_area_per_class_m2": self.roof.get(),
                    "number_of_classrooms": self.cls.get(),
                    "students_per_class": self.studs.get(),
                    "demand_L_per_student_per_day": self.demand.get(),
                    "simulation_years": int(harvest_df["synthetic_year"].nunique()),
                }

                json_path = export_results_to_json(
                    output_path=".",
                    metadata=metadata,
                    harvest_summary=harvest,
                    reliability_table=table,
                )

                self.output.insert(
                    tk.END,
                    f"\n\nJSON results exported to:\n{json_path}\n"
                )


                self.output.insert(tk.END, "\nTANK RELIABILITY (Top 20)\n")
                self.output.insert(
                    tk.END,
                    table.head(20).to_string(index=False)
                )
                
                # ---- STORE RESULTS FOR EXPORT ----
                self.harvest_df = harvest_df
                self.harvest_summary = harvest
                self.reliability_table = table

                # Enable export button
                self.export_btn.config(state=tk.NORMAL)


            except Exception as e:
                messagebox.showerror("Processing Error", str(e))

        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    app = MCSApp()
    app.mainloop()
