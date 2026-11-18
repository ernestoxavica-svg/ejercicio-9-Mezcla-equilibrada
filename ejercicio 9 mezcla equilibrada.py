"""
ADA3 - Ejercicio 9: Despacho de pedidos por tiempo de entrega
Método de ordenamiento externo: MEZCLA EQUILIBRADA (Balanced Natural Merge)

El programa detecta las secuencias ascendentes naturales ("corridas") ya
presentes en los pedidos, las distribuye alternadamente en dos archivos
auxiliares (F1 y F2) y las fusiona hasta obtener una sola corrida ordenada.
"""
import tkinter as tk
from tkinter import ttk, messagebox


def obtener_corridas(lista):
    """Divide la lista en secuencias ascendentes naturales (corridas/runs)."""
    if not lista:
        return []
    corridas = []
    actual = [lista[0]]
    for i in range(1, len(lista)):
        if lista[i][1] >= lista[i - 1][1]:
            actual.append(lista[i])
        else:
            corridas.append(actual)
            actual = [lista[i]]
    corridas.append(actual)
    return corridas


def intercalar_dos_corridas(c1, c2):
    """Intercala dos corridas ordenadas en una sola corrida ordenada."""
    res = []
    i, j = 0, 0
    while i < len(c1) and j < len(c2):
        if c1[i][1] <= c2[j][1]:
            res.append(c1[i])
            i += 1
        else:
            res.append(c2[j])
            j += 1
    res.extend(c1[i:])
    res.extend(c2[j:])
    return res


def mezcla_equilibrada(lista):
    """Ordena `lista` de pedidos (id_pedido, minutos) por Mezcla Equilibrada.

    Aprovecha el orden natural existente: detecta corridas, las reparte de forma
    equilibrada entre F1 y F2 y fusiona pares de corridas hasta quedar 1 sola.
    Regresa (lista_ordenada, pasos).
    """
    datos = list(lista)
    pasos = []
    pasada = 1

    while True:
        corridas = obtener_corridas(datos)
        if len(corridas) <= 1:
            if pasada == 1:
                pasos.append("Los datos ya estaban ordenados en 1 sola corrida natural.")
            break

        # 1. Distribución alternada (equilibrada) de corridas en F1 y F2
        f1 = corridas[0::2]
        f2 = corridas[1::2]

        # 2. Fusión de corridas correspondientes de F1 y F2
        nuevos_datos = []
        max_pares = max(len(f1), len(f2))
        for k in range(max_pares):
            if k < len(f1) and k < len(f2):
                nuevos_datos.extend(intercalar_dos_corridas(f1[k], f2[k]))
            elif k < len(f1):
                nuevos_datos.extend(f1[k])
            else:
                nuevos_datos.extend(f2[k])

        datos = nuevos_datos
        tiempos_str = ", ".join(f"{min_}m" for _, min_ in datos)
        pasos.append(
            f"Pasada {pasada}: {len(corridas)} corridas naturales "
            f"(F1={len(f1)}, F2={len(f2)}) -> [{tiempos_str}]"
        )
        pasada += 1

    return datos, pasos


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Despacho de Pedidos - Mezcla Equilibrada")
        self.geometry("580x580")
        self.resizable(False, False)
        ttk.Style(self).theme_use("clam")

        self.pedidos = []  # lista de (pedido, minutos)

        ttk.Label(self, text="Despacho de Pedidos por Urgencia",
                  font=("Segoe UI", 16, "bold")).pack(pady=(15, 0))
        ttk.Label(self, text="Ordenamiento por tiempo de entrega con Mezcla Equilibrada",
                  foreground="#555").pack(pady=(0, 10))

        # --- Formulario ---
        form = ttk.Frame(self)
        form.pack(pady=5)
        ttk.Label(form, text="Pedido / Cliente:").grid(row=0, column=0, padx=5)
        self.pedido = ttk.Entry(form, width=20)
        self.pedido.grid(row=0, column=1, padx=5)
        ttk.Label(form, text="Entrega (min):").grid(row=0, column=2, padx=5)
        self.minutos = ttk.Entry(form, width=10)
        self.minutos.grid(row=0, column=3, padx=5)
        ttk.Button(form, text="Agregar", command=self.agregar).grid(row=0, column=4, padx=5)
        self.minutos.bind("<Return>", lambda e: self.agregar())

        # --- Tabla ---
        self.tabla = ttk.Treeview(self, columns=("pedido", "tiempo"), show="headings", height=10)
        self.tabla.heading("pedido", text="Pedido / Cliente")
        self.tabla.heading("tiempo", text="Tiempo Estimado (min)")
        self.tabla.column("pedido", width=300)
        self.tabla.column("tiempo", width=180, anchor="center")
        self.tabla.pack(padx=20, pady=10)

        # --- Botones ---
        botones = ttk.Frame(self)
        botones.pack()
        ttk.Button(botones, text="Ordenar (Mezcla Equilibrada)", command=self.ordenar).pack(side="left", padx=5)
        ttk.Button(botones, text="Cargar ejemplo", command=self.ejemplo).pack(side="left", padx=5)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left", padx=5)

        # --- Registro de pasos ---
        ttk.Label(self, text="Corridas naturales detectadas por pasada:").pack(anchor="w", padx=20, pady=(10, 0))
        self.log = tk.Text(self, height=7, width=68, state="disabled",
                           font=("Consolas", 9), bg="#f5f5f5", relief="flat")
        self.log.pack(padx=20, pady=5)

    def agregar(self):
        pedido = self.pedido.get().strip()
        try:
            mins = int(self.minutos.get())
        except ValueError:
            messagebox.showwarning("Dato inválido", "Los minutos deben ser un número entero.")
            return
        if not pedido:
            messagebox.showwarning("Falta pedido", "Escribe el identificador o cliente del pedido.")
            return
        if mins <= 0:
            messagebox.showwarning("Dato inválido", "El tiempo debe ser mayor a 0 minutos.")
            return
        self.pedidos.append((pedido, mins))
        self.pedido.delete(0, "end")
        self.minutos.delete(0, "end")
        self.pedido.focus()
        self.mostrar()

    def ordenar(self):
        if len(self.pedidos) < 2:
            messagebox.showinfo("Pocos datos", "Agrega al menos 2 pedidos.")
            return
        self.pedidos, pasos = mezcla_equilibrada(self.pedidos)
        self.mostrar()
        self.escribir_log(pasos)

    def mostrar(self):
        self.tabla.delete(*self.tabla.get_children())
        for pedido, mins in self.pedidos:
            self.tabla.insert("", "end", values=(pedido, f"{mins} min"))

    def escribir_log(self, lineas):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.insert("end", "\n".join(lineas))
        self.log.config(state="disabled")

    def ejemplo(self):
        # Contiene 3 corridas naturales: [15, 25, 45], [10, 30, 60], [20, 35]
        self.pedidos = [
            ("PED-01 (Farmacia)", 15), ("PED-02 (Supermercado)", 25), ("PED-03 (Restaurante)", 45),
            ("PED-04 (Urgente Médica)", 10), ("PED-05 (Papelería)", 30), ("PED-06 (Ferretería)", 60),
            ("PED-07 (Cafetería)", 20), ("PED-08 (Librería)", 35)
        ]
        self.mostrar()
        self.escribir_log(["Ejemplo cargado (con 3 corridas naturales). Presiona 'Ordenar (Mezcla Equilibrada)'."])

    def limpiar(self):
        self.pedidos.clear()
        self.mostrar()
        self.escribir_log([])


if __name__ == "__main__":
    App().mainloop()