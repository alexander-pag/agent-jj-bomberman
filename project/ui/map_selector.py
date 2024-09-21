import tkinter as tk
from tkinter import filedialog
from config.constants import DEFAULT_DIRECTORY_JHAIR


def select_map():
    """
    Abre una ventana de diálogo para seleccionar un archivo de mapa desde una ruta por defecto.

    Returns:
        file_path: Ruta del archivo seleccionado.
    """
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo de mapa",
        initialdir=DEFAULT_DIRECTORY_JHAIR,
        filetypes=(("Archivos de mapa", "*.txt"), ("Todos los archivos", "*.*")),
    )

    root.destroy()
    return file_path
