# =========================================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA (UNAD)
# ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA (ECBTI)
# CURSO: PROGRAMACIÓN - FASE 4 (COMPONENTE PRÁCTICO)
#
# APORTE PARTE 1: NÚCLEO, EXCEPCIONES, LOGS, CLASE CLIENTE E INTERFAZ
# =========================================================================

from abc import ABC, abstractmethod
import datetime
import tkinter as tk
from tkinter import messagebox

# =========================================================================
# 1. EXCEPCIONES PERSONALIZADAS
# =========================================================================

class ErrorSistemaFJ(Exception):
    #Clase base para todas las excepciones personalizadas del sistema Software FJ
    pass


class ErrorDatoInvalido(ErrorSistemaFJ):
    #Excepción lanzada cuando un dato ingresado no cumple con las validaciones.
    pass


class ServicioNoDisponibleError(ErrorSistemaFJ):
    #Excepción lanzada cuando se solicita un servicio no disponible
    pass


class ErrorReserva(ErrorSistemaFJ):
    #Excepción lanzada ante fallos en la gestión de reservas.
    pass


# =========================================================================
# 2. SISTEMA DE REGISTRO DE LOGS (USO DE TRY / EXCEPT / ELSE / FINALLY)
# =========================================================================

def registrar_log(mensaje, tipo="INFO"):
    #Registra eventos y errores en el archivo 'sistema_log.txt'.
    #Aplica la estructura completa try/except/else/finally exigida en la guía.
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entrada = f"[{timestamp}] [{tipo}] {mensaje}\n"
    archivo = None

    try:
        # Intentar abrir el archivo de registro en modo append (agregar)
        archivo = open("sistema_log.txt", "a", encoding="utf-8")
        archivo.write(entrada)
    except IOError as e:
        # Captura de error de Entrada/Salida
        print(f"Error crítico al escribir en el log del sistema: {e}")
    else:
        # Se ejecuta únicamente si no hubo ningún error de escritura
        pass
    finally:
        # Garantiza el cierre del recurso en cualquier circunstancia
        if archivo:
            archivo.close()


# =========================================================================
# 3. CLASE ABSTRACTA BASE (ENTIDADES GENERALES)
# =========================================================================

class EntidadBase(ABC):
    #Clase abstracta base para las entidades generales del sistema.
    #Obliga a sus clases derivadas a implementar el método obtener_informacion().

    @abstractmethod
    def obtener_informacion(self):
        #Método abstracto que debe ser implementado por cada clase hija.
        pass


# =========================================================================
# 4. CLASE CLIENTE (ENCAPSULAMIENTO Y VALIDACIONES ROBUSTAS)
# =========================================================================

class Cliente(EntidadBase):
    #Gestiona la información personal de los clientes de Software FJ.
    #Aplica encapsulamiento estricto mediante atributos privados (__).

    def __init__(self, nombre, identificacion, correo, telefono):
        nom_clean = str(nombre).strip()
        id_clean = str(identificacion).strip()
        correo_clean = str(correo).strip()
        tel_clean = str(telefono).strip()

        # Validaciones estrictas que disparan excepciones personalizadas
        if not nom_clean:
            err = "El nombre del cliente no puede estar vacío."
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err)

        if not id_clean.isdigit() or len(id_clean) < 5:
            err = f"La identificación '{id_clean}' es inválida. Debe ser numérica y tener al menos 5 dígitos."
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err)

        if "@" not in correo_clean or "." not in correo_clean:
            err = f"El correo electrónico '{correo_clean}' es inválido. Debe contener '@' y un dominio válido."
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err)

        if not tel_clean.isdigit() or len(tel_clean) < 7:
            err = f"El teléfono '{tel_clean}' es inválido. Debe contener al menos 7 dígitos numéricos."
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err)

        # Asignación a atributos estrictamente privados (__)
        self.__nombre = nom_clean.title()
        self.__identificacion = id_clean
        self.__correo = correo_clean
        self.__telefono = tel_clean

        registrar_log(f"Cliente creado exitosamente: {self.__nombre} (ID: {self.__identificacion})")

    # Métodos públicos para consultar atributos privados (Getters)
    def obtener_nombre(self):
        return self.__nombre

    def obtener_identificacion(self):
        return self.__identificacion

    def obtener_correo(self):
        return self.__correo

    def obtener_telefono(self):
        return self.__telefono

    def obtener_informacion(self):
        #Implementación obligatoria del método abstracto de EntidadBase.
        return f"Cliente: {self.__nombre} | ID: {self.__identificacion} | Correo: {self.__correo} | Tel: {self.__telefono}"


# =========================================================================
# 5. INTERFAZ GRÁFICA (PRUEBA FUNCIONAL DEL MÓDULO CLIENTES)
# =========================================================================

class AplicacionSoftwareFJ:
    def __init__(self, ventana):
        self.clientes_registrados = []

        ventana.title("Software FJ - Módulo de Gestión de Clientes (Parte 1)")
        ventana.geometry("520x600")

        marco = tk.Frame(ventana, padx=15, pady=15)
        marco.pack(fill="both", expand=True)

        tk.Label(marco, text="Registro de Clientes y Pruebas de Excepciones", font=("arial", 12, "bold"), fg="darkblue").grid(row=0, column=0, columnspan=2, pady=10)

        # Campos de entrada
        self.entradas = {}
        campos = ["Nombre Completo", "Identificación", "Correo Electrónico", "Teléfono"]
        
        for idx, texto in enumerate(campos, start=1):
            tk.Label(marco, text=texto + ":", font=("arial", 10)).grid(row=idx, column=0, sticky="w", pady=5)
            self.entradas[texto] = tk.Entry(marco, width=32)
            self.entradas[texto].grid(row=idx, column=1, pady=5)

        # Botón de registro
        tk.Button(
            marco, text="Registrar Cliente (Validar)", command=self.registrar_cliente_gui, 
            bg="#28A745", fg="white", font=("arial", 10, "bold"), width=30
        ).grid(row=5, column=0, columnspan=2, pady=12)

        # Listbox para ver clientes exitosos
        tk.Label(marco, text="Clientes Registrados en Memoria:", font=("arial", 9, "bold")).grid(row=6, column=0, columnspan=2, sticky="w", pady=2)
        self.lista_clientes = tk.Listbox(marco, width=58, height=6)
        self.lista_clientes.grid(row=7, column=0, columnspan=2, pady=5)

        # Área de texto para logs y resultados
        tk.Label(marco, text="Consola de Eventos y Excepciones Capturadas:", font=("arial", 9, "bold")).grid(row=8, column=0, columnspan=2, sticky="w", pady=2)
        self.salida_texto = tk.Text(marco, width=58, height=7)
        self.salida_texto.grid(row=9, column=0, columnspan=2, pady=5)

    def registrar_cliente_gui(self):
        #Toma los datos de la interfaz, instancia Cliente y atrapa excepciones si fallan
        nombre = self.entradas["Nombre Completo"].get()
        identificacion = self.entradas["Identificación"].get()
        correo = self.entradas["Correo Electrónico"].get()
        telefono = self.entradas["Teléfono"].get()

        try:
            # Intentar crear el objeto Cliente (dispara excepciones si hay errores)
            nuevo_cliente = Cliente(nombre, identificacion, correo, telefono)
            
            # Si todo sale bien:
            self.clientes_registrados.append(nuevo_cliente)
            self.lista_clientes.insert(tk.END, f"{nuevo_cliente.obtener_nombre()} - ID: {nuevo_cliente.obtener_identificacion()}")
            
            mensaje_exito = f"Éxito: Cliente {nuevo_cliente.obtener_nombre()} registrado correctamente."
            self.salida_texto.delete("1.0", tk.END)
            self.salida_texto.insert(tk.END, mensaje_exito)
            
            messagebox.showinfo("Registro Exitoso", mensaje_exito)
            
            # Limpiar entradas
            for entry in self.entradas.values():
                entry.delete(0, tk.END)

        except ErrorDatoInvalido as e:
            # Captura específica de nuestra excepción personalizada
            error_msg = f"Excepción Controlada (Dato Inválido): {e}"
            self.salida_texto.delete("1.0", tk.END)
            self.salida_texto.insert(tk.END, error_msg)
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            # Captura general de cualquier otro error imprevisto
            error_msg = f"Error Inesperado: {e}"
            self.salida_texto.delete("1.0", tk.END)
            self.salida_texto.insert(tk.END, error_msg)
            messagebox.showerror("Error Crítico", str(e))


# Ejecución principal de la aplicación
if __name__ == "__main__":
    ventana = tk.Tk()
    AplicacionSoftwareFJ(ventana)
    ventana.mainloop()