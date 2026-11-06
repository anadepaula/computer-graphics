"""Dialogo do sistema para abrir um arquivo OFF (tkinter)."""
import sys


def escolher_off(titulo="Abrir malha OFF"):
    """Devolve o caminho escolhido, ou None se o usuario cancelar."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print("tkinter indisponivel: use a linha de comando ou arraste o "
              "arquivo para a janela.", file=sys.stderr)
        return None

    raiz = tk.Tk()
    raiz.withdraw()                 # so o dialogo, sem a janela do Tk
    raiz.update()
    caminho = filedialog.askopenfilename(
        title=titulo,
        filetypes=[("Malhas OFF", "*.off"), ("Todos os arquivos", "*.*")])
    raiz.destroy()
    return caminho or None
