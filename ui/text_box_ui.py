# ui/text_box_ui.py

import threading
import tkinter as tk


class TextBoxUI:
    """
    A floating Tkinter text box window.
    - Always visible in AI Mode and F1 Mode
    - Hidden in Engineer Mode unless paused
    - Sends text to InputManager via callback
    """

    def __init__(self, on_submit_callback):
        self.on_submit = on_submit_callback
        self._visible = False
        self._thread_started = False
        self._root = None
        self._entry = None

    # ---------------------------------------------------------
    # INTERNAL: Tkinter thread
    # ---------------------------------------------------------
    def _run_tk(self):
        self._root = tk.Tk()
        self._root.title("Saul Input")
        self._root.geometry("400x120")
        self._root.resizable(False, False)

        # Center the window
        self._center_window()

        # Entry box
        self._entry = tk.Entry(self._root, font=("Segoe UI", 14))
        self._entry.pack(fill="both", expand=True, padx=10, pady=10)
        self._entry.bind("<Return>", self._on_enter)

        # Start hidden
        self._root.withdraw()

        self._root.mainloop()

    # ---------------------------------------------------------
    # INTERNAL: Center window
    # ---------------------------------------------------------
    def _center_window(self):
        self._root.update_idletasks()
        w = 400
        h = 120
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self._root.geometry(f"{w}x{h}+{x}+{y}")

    # ---------------------------------------------------------
    # INTERNAL: Handle Enter key
    # ---------------------------------------------------------
    def _on_enter(self, event):
        text = self._entry.get().strip()
        if text:
            self.on_submit(text)
        self._entry.delete(0, tk.END)

    # ---------------------------------------------------------
    # PUBLIC: Start UI thread
    # ---------------------------------------------------------
    def start(self):
        if not self._thread_started:
            t = threading.Thread(target=self._run_tk, daemon=True)
            t.start()
            self._thread_started = True

    # ---------------------------------------------------------
    # PUBLIC: Show centered
    # ---------------------------------------------------------
    def show_centered(self):
        if self._root and not self._visible:
            self._center_window()
            self._root.deiconify()
            self._entry.focus_set()
            self._visible = True

    # ---------------------------------------------------------
    # PUBLIC: Hide
    # ---------------------------------------------------------
    def hide(self):
        if self._root and self._visible:
            self._root.withdraw()
            self._visible = False
