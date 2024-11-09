# 08/11/2024
"""Selector de países para StockScraper

Proporciona una interfaz gráfica que muestra el listado de todos los países
disponibles, organizados por región, y permite seleccionar los deseados y
generar un archivo CSV con los mismos.

"""

import tkinter
from tkinter import ttk


class CountriesSelector(tkinter.Tk):
    """Selector de países para StockScraper

    Tras seleccionar unos u otros países, se puede pulsar el botón 'Generar'
    para crear la nueva lista de países.

    El constructor sólo requiere el listado de países inicial, con forma
    (región, país, token de URL).

    """

    def __init__(self, countries: list[tuple[str, str, str]], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title("Selector de países")
        self._all_countries = countries.copy()
        self.countries = countries
        self._setup()

    def _setup(self) -> None:
        """Configura la interfaz gráfica"""
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill=tkinter.BOTH, expand=True)

        # Se organizan los países por región para mostrarlos agrupados
        regions = {}
        for region, country, token in self.countries:
            if region not in regions:
                regions[region] = []
            regions[region].append((country, token))

        # Por región, se crea un Frame con los CheckBox de los países
        # Las BooleanVar almacenarán el estado de selección de cada país
        self.check_vars = {}
        regions_frame = ttk.Frame(main_frame)
        regions_frame.pack(fill=tkinter.BOTH, expand=True)
        for region, countries in regions.items():
            # Frame
            region_frame = ttk.Frame(regions_frame)
            region_frame.pack(anchor=tkinter.N, padx=10, side=tkinter.LEFT)
            # Título de región
            # Si se hace click sobre este, se marcan todos los países de la región
            # Si se hace doble click, se desmarcan
            region_label = ttk.Label(
                region_frame, text=region, font=("Arial", 12, "bold")
            )
            region_label.pack(anchor=tkinter.W)
            region_label.bind("<Button-1>", lambda e, r=region: self._set_all(True, r))
            region_label.bind(
                "<Double-Button-1>", lambda e, r=region: self._set_all(False, r)
            )
            # CheckBox de países
            for country, token in countries:
                var = tkinter.BooleanVar()
                var.set(True)
                self.check_vars[(region, country, token)] = var
                check_button = ttk.Checkbutton(region_frame, text=country, variable=var)
                check_button.pack(anchor=tkinter.W)

        # Frame con los botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tkinter.BOTH, expand=True)

        # Botón 'Generar'
        submit_button = ttk.Button(
            buttons_frame, text="Generar", command=self._new_list
        )
        submit_button.pack(pady=20, padx=10, side=tkinter.LEFT)

        # Botón de 'Marcar/Desmarcar todos'
        select_all_button = ttk.Button(
            buttons_frame, text="Marcar todos", command=lambda: self._set_all(True)
        )
        select_all_button.pack(pady=20, padx=10, side=tkinter.LEFT)
        deselect_all_button = ttk.Button(
            buttons_frame, text="Desmarcar todos", command=lambda: self._set_all(False)
        )
        deselect_all_button.pack(pady=20, padx=10, side=tkinter.LEFT)

    def _new_list(self) -> None:
        """Genera la nueva lista de países seleccionados"""
        self.countries = [
            (region, country, token)
            for (region, country, token), var in self.check_vars.items()
            if var.get()
        ]
        self.destroy()

    def _set_all(self, state: bool, region: str | None = None) -> None:
        """Marca o desmarca todos los CheckBox"""
        for key, var in self.check_vars.items():
            if region and key[0] != region:
                continue
            var.set(state)


if __name__ == "__main__":
    data = [
        ("North America", "United States", "https://us.example.com"),
        ("North America", "Canada", "https://ca.example.com"),
        ("Europe", "Germany", "https://de.example.com"),
        ("Europe", "France", "https://fr.example.com"),
        ("Asia", "Japan", "https://jp.example.com"),
        ("Asia", "South Korea", "https://kr.example.com"),
    ]
    selector = CountriesSelector(data)
    selector.mainloop()
    print(">>> Países seleccionados:", selector.countries)
