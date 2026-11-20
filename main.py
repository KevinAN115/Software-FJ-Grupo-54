# =========================================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA (UNAD)
# ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA (ECBTI)
# CURSO: PROGRAMACIÓN - FASE 4 (COMPONENTE PRÁCTICO)
# SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS - SOFTWARE FJ
# =========================================================================

from abc import ABC, abstractmethod
import datetime
import tkinter as tk
from tkinter import messagebox

# =========================================================================
# 1. EXCEPCIONES PERSONALIZADAS
# =========================================================================

class ErrorSistemaFJ(Exception):
    """Clase base para todas las excepciones personalizadas del sistema Software FJ"""
    pass


class ErrorDatoInvalido(ErrorSistemaFJ):
    """Excepción lanzada cuando un dato ingresado no cumple con las validaciones."""
    pass


class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Excepción lanzada cuando se solicita un servicio no disponible"""
    pass


class ErrorReserva(ErrorSistemaFJ):
    """Excepción lanzada ante fallos en la gestión de reservas."""
    pass


# =========================================================================
# 2. SISTEMA DE REGISTRO DE LOGS (USO DE TRY / EXCEPT / ELSE / FINALLY)
# =========================================================================

def registrar_log(mensaje, tipo="INFO"):
    """Registra eventos y errores en el archivo 'sistema_log.txt'.
    Aplica la estructura completa try/except/else/finally exigida en la guía."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entrada = f"[{timestamp}] [{tipo}] {mensaje}\n"
    archivo = None

    try:
        archivo = open("sistema_log.txt", "a", encoding="utf-8")
        archivo.write(entrada)
    except IOError as e:
        print(f"Error crítico al escribir en el log del sistema: {e}")
    else:
        pass
    finally:
        if archivo:
            archivo.close()


# =========================================================================
# 3. CLASE ABSTRACTA BASE (ENTIDADES GENERALES)
# =========================================================================

class EntidadBase(ABC):
    """Clase abstracta base para las entidades generales del sistema."""

    @abstractmethod
    def obtener_informacion(self):
        pass


# =========================================================================
# 4. CLASE CLIENTE (ENCAPSULAMIENTO Y VALIDACIONES ROBUSTAS)
# =========================================================================

class Cliente(EntidadBase):
    """Gestiona la información personal de los clientes de Software FJ."""

    def __init__(self, nombre, identificacion, correo, telefono):
        nom_clean = str(nombre).strip()
        id_clean = str(identificacion).strip()
        correo_clean = str(correo).strip()
        tel_clean = str(telefono).strip()

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

        self.__nombre = nom_clean.title()
        self.__identificacion = id_clean
        self.__correo = correo_clean
        self.__telefono = tel_clean

        registrar_log(f"Cliente creado exitosamente: {self.__nombre} (ID: {self.__identificacion})")

    def obtener_nombre(self):
        return self.__nombre

    def obtener_identificacion(self):
        return self.__identificacion

    def obtener_correo(self):
        return self.__correo

    def obtener_telefono(self):
        return self.__telefono

    def obtener_informacion(self):
        return f"Cliente: {self.__nombre} | ID: {self.__identificacion} | Correo: {self.__correo} | Tel: {self.__telefono}"


# =========================================================================
# 5. CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS (POLIMORFISMO)
# =========================================================================

class Servicio(EntidadBase, ABC):
    """Clase abstracta Servicio para Software FJ con herencia y polimorfismo."""
    
    def __init__(self, codigo_servicio, nombre_servicio, costo_base):
        self._codigo = str(codigo_servicio).strip()
        self._nombre_servicio = str(nombre_servicio).strip()
        
        if costo_base < 0:
            err = f"El costo base no puede ser negativo: {costo_base}"
            registrar_log(err, "ERROR")
            raise ServicioNoDisponibleError(err)
            
        self._costo_base = float(costo_base)

    @property
    def codigo(self):
        return self._codigo

    @property
    def costo_base(self):
        return self._costo_base

    @abstractmethod
    def describir_servicio(self):
        pass

    def calcular_costo(self, descuento=0.0, impuesto=0.19):
        try:
            if descuento < 0 or impuesto < 0:
                raise ValueError("Descuentos o impuestos no pueden ser negativos.")
            subtotal = self._costo_base * (1 - descuento)
            total = subtotal * (1 + impuesto)
            return round(total, 2)
        except Exception as e:
            registrar_log(f"Error calculando costo para servicio {self._codigo}: {e}", "ERROR")
            raise


class ReservaSalas(Servicio):
    def __init__(self, codigo, costo_base, capacidad):
        super().__init__(codigo, "Reserva de Salas", costo_base)
        self.capacidad = int(capacidad)

    def describir_servicio(self):
        return f"[Sala] Código: {self.codigo} | Capacidad: {self.capacidad} personas | Costo Base: ${self.costo_base}"

    def obtener_informacion(self):
        return self.describir_servicio()


class AlquilerEquipos(Servicio):
    def __init__(self, codigo, costo_base, tipo_equipo):
        super().__init__(codigo, "Alquiler de Equipos", costo_base)
        self.tipo_equipo = str(tipo_equipo)

    def describir_servicio(self):
        return f"[Equipo] Código: {self.codigo} | Tipo: {self.tipo_equipo} | Costo Base: ${self.costo_base}"

    def obtener_informacion(self):
        return self.describir_servicio()


class AsesoriaEspecializada(Servicio):
    def __init__(self, codigo, costo_base, area):
        super().__init__(codigo, "Asesoría Especializada", costo_base)
        self.area = str(area)

    def describir_servicio(self):
        return f"[Asesoría] Código: {self.codigo} | Área: {self.area} | Costo Base: ${self.costo_base}"

    def obtener_informacion(self):
        return self.describir_servicio()


# =========================================================================
# 6. CLASE RESERVA CON MANEJO AVANZADO DE EXCEPCIONES
# =========================================================================

class Reserva(EntidadBase):
    def __init__(self, codigo_reserva, cliente, servicio, duracion_horas):
        self.codigo_reserva = str(codigo_reserva)
        self.cliente = cliente
        self.servicio = servicio
        
        if duracion_horas <= 0:
            err = f"Duración de reserva inválida: {duracion_horas} horas. Debe ser mayor a 0."
            registrar_log(err, "ERROR")
            raise ErrorReserva(err)
            
        self.duracion_horas = int(duracion_horas)
        self.estado = "Pendiente"

    def procesar_reserva(self, descuento=0.0):
        costo_total = 0.0
        try:
            registrar_log(f"Iniciando procesamiento de reserva {self.codigo_reserva}...")
            if not self.cliente or not self.servicio:
                raise ErrorReserva("Faltan datos del cliente o del servicio en la reserva.")
            
            costo_unitario = self.servicio.calcular_costo(descuento=descuento)
            costo_total = costo_unitario * self.duracion_horas
            
        except ZeroDivisionError as zde:
            registrar_log(f"Error aritmético en reserva {self.codigo_reserva}: {zde}", "ERROR")
            raise ErrorReserva("Error de cálculo por división en cero.") from zde
        except Exception as e:
            registrar_log(f"Falla crítica procesando reserva {self.codigo_reserva}: {e}", "ERROR")
            raise ErrorReserva(f"No se pudo procesar la reserva: {e}")
        else:
            self.estado = "Confirmada"
            registrar_log(f"Reserva {self.codigo_reserva} confirmada de forma exitosa. Total: ${costo_total}")
            return costo_total
        finally:
            print(f">>> [LOG TRANSACCIÓN]: Finalizó intento de procesamiento para la reserva {self.codigo_reserva} (Estado: {self.estado})")

    def obtener_informacion(self):
        return f"Reserva: {self.codigo_reserva} | Cliente: {self.cliente.obtener_nombre()} | Servicio: {self.servicio.codigo} | Estado: {self.estado}"


# =========================================================================
# 7. SIMULACIÓN DE LAS 10 OPERACIONES (EXIGIDO POR LA GUÍA)
# =========================================================================

def ejecutar_simulacion_10_operaciones():
    print("\n==================================================")
    print(" INICIO DE SIMULACIÓN DE 10 OPERACIONES (SOFTWARE FJ)")
    print("==================================================\n")

    clientes = []
    servicios = []
    reservas = []

    # Op 1: Registro válido de cliente
    try:
        c1 = Cliente("Ana María Pérez", "123456", "ana@correo.com", "3104567890")
        clientes.append(c1)
        print("[Op 1 - ÉXITO]: Cliente registrado correctamente.")
    except Exception as e:
        print(f"[Op 1 - ERROR]: {e}")

    # Op 2: Registro inválido de cliente (Excepción personalizada)
    try:
        print("[Op 2 - PRUEBA]: Intentando registrar cliente con identificación corta...")
        c_malo = Cliente("Carlos", "123", "carlos@correo.com", "320123456")
        clientes.append(c_malo)
    except ErrorDatoInvalido as e:
        print(f"[Op 2 - CAPTURADA]: Excepción controlada con éxito -> {e}")

    # Op 3: Creación válida de Servicio 1 (Sala)
    try:
        s1 = ReservaSalas("SLA-01", 100.0, 20)
        servicios.append(s1)
        print(f"[Op 3 - ÉXITO]: Servicio creado -> {s1.describir_servicio()}")
    except Exception as e:
        print(f"[Op 3 - ERROR]: {e}")

    # Op 4: Creación válida de Servicio 2 (Equipo)
    try:
        s2 = AlquilerEquipos("EQP-02", 50.0, "Servidor Cloud Core")
        servicios.append(s2)
        print(f"[Op 4 - ÉXITO]: Servicio creado -> {s2.describir_servicio()}")
    except Exception as e:
        print(f"[Op 4 - ERROR]: {e}")

    # Op 5: Creación válida de Servicio 3 (Asesoría)
    try:
        s3 = AsesoriaEspecializada("ASR-03", 180.0, "Arquitectura de Software")
        servicios.append(s3)
        print(f"[Op 5 - ÉXITO]: Servicio creado -> {s3.describir_servicio()}")
    except Exception as e:
        print(f"[Op 5 - ERROR]: {e}")

    # Op 6: Creación inválida de servicio (Costo negativo)
    try:
        print("[Op 6 - PRUEBA]: Intentando crear servicio con costo negativo...")
        s_malo = ReservaSalas("SLA-02", -200.0, 10)
        servicios.append(s_malo)
    except ServicioNoDisponibleError as e:
        print(f"[Op 6 - CAPTURADA]: Excepción de servicio controlada -> {e}")

    # Op 7: Reserva Exitosa 1 (Sala con descuento)
    try:
        res1 = Reserva("RES-101", clientes[0], servicios[0], duracion_horas=4)
        total = res1.procesar_reserva(descuento=0.10)
        reservas.append(res1)
        print(f"[Op 7 - ÉXITO]: Reserva procesada. Total a pagar: ${total}")
    except Exception as e:
        print(f"[Op 7 - ERROR]: {e}")

    # Op 8: Reserva Exitosa 2 (Equipo sin descuento)
    try:
        res2 = Reserva("RES-102", clientes[0], servicios[1], duracion_horas=6)
        total = res2.procesar_reserva()
        reservas.append(res2)
        print(f"[Op 8 - ÉXITO]: Reserva procesada. Total a pagar: ${total}")
    except Exception as e:
        print(f"[Op 8 - ERROR]: {e}")

    # Op 9: Reserva Fallida por duración en cero
    try:
        print("[Op 9 - PRUEBA]: Intentando crear reserva con duración de 0 horas...")
        res_falla = Reserva("RES-103", clientes[0], servicios[2], duracion_horas=0)
    except ErrorReserva as e:
        print(f"[Op 9 - CAPTURADA]: Excepción de reserva inválida capturada -> {e}")

    # Op 10: Validación y reporte final en consola de logs
    try:
        print("[Op 10 - ÉXITO]: Verificando estado de estabilidad y registro en 'sistema_log.txt'...")
        with open("sistema_log.txt", "r", encoding="utf-8") as archivo_log:
            lineas = archivo_log.readlines()
            print(f"Total de eventos y errores registrados en el log: {len(lineas)}")
    except Exception as e:
        print(f"[Op 10 - ERROR]: {e}")

    print("\n==================================================")
    print(" SIMULACIÓN DE 10 OPERACIONES FINALIZADA CON ÉXITO")
    print("==================================================\n")


# =========================================================================
# 8. INTERFAZ GRÁFICA (PRUEBA FUNCIONAL Y DE GESTIÓN)
# =========================================================================

class AplicacionSoftwareFJ:
    def __init__(self, ventana):
        self.clientes_registrados = []

        ventana.title("Software FJ - Sistema Integral de Gestión")
        ventana.geometry("520x620")

        marco = tk.Frame(ventana, padx=15, pady=15)
        marco.pack(fill="both", expand=True)

        tk.Label(marco, text="Software FJ - Gestión y Excepciones", font=("arial", 12, "bold"), fg="darkblue").grid(row=0, column=0, columnspan=2, pady=10)

        self.entradas = {}
        campos = ["Nombre Completo", "Identificación", "Correo Electrónico", "Teléfono"]
        
        for idx, texto in enumerate(campos, start=1):
            tk.Label(marco, text=texto + ":", font=("arial", 10)).grid(row=idx, column=0, sticky="w", pady=5)
            self.entradas[texto] = tk.Entry(marco, width=32)
            self.entradas[texto].grid(row=idx, column=1, pady=5)

        tk.Button(
            marco, text="Registrar Cliente (Validar)", command=self.registrar_cliente_gui, 
            bg="#28A745", fg="white", font=("arial", 10, "bold"), width=30
        ).grid(row=5, column=0, columnspan=2, pady=12)

        tk.Label(marco, text="Clientes Registrados en Memoria:", font=("arial", 9, "bold")).grid(row=6, column=0, columnspan=2, sticky="w", pady=2)
        self.lista_clientes = tk.Listbox(marco, width=58, height=6)
        self.lista_clientes.grid(row=7, column=0, columnspan=2, pady=5)

        tk.Label(marco, text="Consola de Eventos y Excepciones Capturadas:", font=("arial", 9, "bold")).grid(row=8, column=0, columnspan=2, sticky="w", pady=2)
        self.salida_texto = tk.Text(marco, width=58, height=7)
        self.salida_texto.grid(row=9, column=0, columnspan=2, pady=5)

    def registrar_cliente_gui(self):
        nombre = self.entradas["Nombre Completo"].get()
        identificacion = self.entradas["Identificación"].get()
        correo = self.entradas["Correo Electrónico"].get()
        telefono = self.entradas["Teléfono"].get()

        try:
            nuevo_cliente = Cliente(nombre, identificacion, correo, telefono)
            self.clientes_registrados.append(nuevo_cliente)
            self.lista_clientes.insert(tk.END, f"{nuevo_cliente.obtener_nombre()} - ID: {nuevo_cliente.obtener_identificacion()}")
            
            mensaje_exito = f"Éxito: Cliente {nuevo_cliente.obtener_nombre()} registrado correctamente."
            self.salida_texto.delete("1.0", tk.END)
            self.salida_texto.insert(tk.END, mensaje_exito)
            
            messagebox.showinfo("Registro Exitoso", mensaje_exito)
            
            for entry in self.entradas.values():
                entry.delete(0, tk.END)

        except ErrorDatoInvalido as e:
            error_msg = f"Excepción Controlada (Dato Inválido): {e}"
            self.salida_texto.delete("1.0", tk.END)
            self.salida_texto.insert(tk.END, error_msg)
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            error_msg = f"Error Inesperado: {e}"
            self.salida_texto.delete("1.0", tk.END)
            self.salida_texto.insert(tk.END, error_msg)
            messagebox.showerror("Error Crítico", str(e))


# =========================================================================
# 9. EJECUCIÓN PRINCIPAL
# =========================================================================

if __name__ == "__main__":
    # 1. Ejecutamos la simulación en consola de las 10 operaciones exigidas por la guía
    ejecutar_simulacion_10_operaciones()

    # 2. Iniciamos la interfaz gráfica colaborativa del grupo
    print("Iniciando aplicación gráfica Software FJ...")
    ventana = tk.Tk()
    app = AplicacionSoftwareFJ(ventana)
    ventana.mainloop()
