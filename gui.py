import tkinter as tk
from tkinter import messagebox
import asyncio
import json
from main import main

class TelekDadosGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hygark's TelekDados")
        
        tk.Label(root, text="Link do canal/grupo fonte:").grid(row=0, column=0, padx=5, pady=5)
        self.source_entry = tk.Entry(root, width=50)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(root, text="Link do canal/grupo destino:").grid(row=1, column=0, padx=5, pady=5)
        self.dest_entry = tk.Entry(root, width=50)
        self.dest_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(root, text="Telegram API ID:").grid(row=2, column=0, padx=5, pady=5)
        self.api_id_entry = tk.Entry(root, width=50)
        self.api_id_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(root, text="Telegram API Hash:").grid(row=3, column=0, padx=5, pady=5)
        self.api_hash_entry = tk.Entry(root, width=50)
        self.api_hash_entry.grid(row=3, column=1, padx=5, pady=5)
        
        tk.Label(root, text="Número de telefone (+55...):").grid(row=4, column=0, padx=5, pady=5)
        self.phone_entry = tk.Entry(root, width=50)
        self.phone_entry.grid(row=4, column=1, padx=5, pady=5)
        
        tk.Label(root, text="Grafana API Key (opcional):").grid(row=5, column=0, padx=5, pady=5)
        self.grafana_key_entry = tk.Entry(root, width=50)
        self.grafana_key_entry.grid(row=5, column=1, padx=5, pady=5)
        
        tk.Button(root, text="Iniciar Backup", command=self.start_backup).grid(row=6, column=0, columnspan=2, pady=10)
    
    def start_backup(self):
        source = self.source_entry.get()
        dest = self.dest_entry.get()
        api_id = self.api_id_entry.get()
        api_hash = self.api_hash_entry.get()
        phone = self.phone_entry.get()
        grafana_key = self.grafana_key_entry.get()
        
        if not all([source, dest, api_id, api_hash, phone]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
            return
        
        try:
            asyncio.run(main(source, dest, api_id, api_hash, phone, grafana_key))
            messagebox.showinfo("Sucesso", "Backup concluído! Verifique output.json, chart.html e Grafana.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no backup: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    app = TelekDadosGUI(root)
    root.mainloop()