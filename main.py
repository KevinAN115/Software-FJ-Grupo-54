# =========================================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA (UNAD)
# ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA (ECBTI)
# CURSO: PROGRAMACIÓN - FASE 4 (COMPONENTE PRÁCTICO)
# SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS - SOFTWARE FJ
# =========================================================================

from abc import ABC, abstractmethod
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

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

    def __init__(self, codigo_servicio, nombre_servicio, costo_base, disponible=True):
        cod_clean = str(codigo_servicio).strip().upper()
        nom_clean = str(nombre_servicio).strip()

        if not cod_clean:
            err = "El código del servicio no puede estar vacío."
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err)

        if not nom_clean:
            err = "El nombre del servicio no puede estar vacío."
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err)

        try:
            costo_num = float(costo_base)
        except (TypeError, ValueError) as exc:
            err = f"Costo base inválido para el servicio {cod_clean}: {costo_base}"
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err) from exc

        if costo_num <= 0:
            err = f"El costo base del servicio {cod_clean} debe ser mayor a cero: {costo_num}"
            registrar_log(err, "ERROR")
            raise ServicioNoDisponibleError(err)

        self._codigo = cod_clean
        self._nombre_servicio = nom_clean
        self._costo_base = costo_num
        self._disponible = bool(disponible)
        self.validar_parametros()

    @property
    def codigo(self):
        return self._codigo

    @property
    def nombre_servicio(self):
        return self._nombre_servicio

    @property
    def costo_base(self):
        return self._costo_base

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        self._disponible = bool(estado)
        estado_txt = "Disponible" if self._disponible else "No disponible"
        registrar_log(f"Servicio {self._codigo} marcado como {estado_txt}.")

    @abstractmethod
    def validar_parametros(self):
        """Valida los parámetros específicos de cada servicio especializado."""
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    def calcular_costo(self, descuento=0.0, impuesto=0.19, recargo_extra=0.0):
        """Sobrecarga mediante parámetros opcionales para descuento, impuesto y recargo extra."""
        try:
            desc = float(descuento)
            imp = float(impuesto)
            rec = float(recargo_extra)

            if not (0.0 <= desc < 1.0):
                raise ErrorDatoInvalido("El descuento debe estar entre 0.0 y menor que 1.0.")
            if imp < 0.0 or rec < 0.0:
                raise ErrorDatoInvalido("Impuestos o recargos no pueden ser negativos.")

            subtotal = (self._costo_base + rec) * (1.0 - desc)
            total = subtotal * (1.0 + imp)
            return round(total, 2)
        except Exception as e:
            registrar_log(f"Error calculando costo para servicio {self._codigo}: {e}", "ERROR")
            raise


class ReservaSalas(Servicio):
    def __init__(self, codigo, costo_base, capacidad, disponible=True):
        try:
            self.capacidad = int(capacidad)
        except (TypeError, ValueError) as exc:
            err = f"Capacidad de sala inválida: {capacidad}"
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err) from exc

        super().__init__(codigo, "Reserva de Salas", costo_base, disponible=disponible)
        registrar_log(f"Servicio de sala creado: {self.codigo} (Capacidad: {self.capacidad})")

    def validar_parametros(self):
        if self.capacidad <= 0:
            err = f"La capacidad de la sala {self.codigo} debe ser mayor a 0."
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err)

    def calcular_costo(self, descuento=0.0, impuesto=0.19, recargo_extra=0.0):
        # Polimorfismo: salas grandes (>25 personas) aplican un recargo operativo del 15% sobre base
        recargo_capacidad = self._costo_base * 0.15 if self.capacidad > 25 else 0.0
        return super().calcular_costo(
            descuento=descuento,
            impuesto=impuesto,
            recargo_extra=recargo_extra + recargo_capacidad
        )

    def describir_servicio(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"[Sala] Código: {self.codigo} | Capacidad: {self.capacidad} personas | Costo Base: ${self.costo_base:,.2f} | {estado}"

    def obtener_informacion(self):
        return self.describir_servicio()


class AlquilerEquipos(Servicio):
    def __init__(self, codigo, costo_base, tipo_equipo, disponible=True):
        self.tipo_equipo = str(tipo_equipo).strip()
        super().__init__(codigo, "Alquiler de Equipos", costo_base, disponible=disponible)
        registrar_log(f"Servicio de equipo creado: {self.codigo} ({self.tipo_equipo})")

    def validar_parametros(self):
        if not self.tipo_equipo:
            err = f"El tipo de equipo para el servicio {self.codigo} no puede estar vacío."
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err)

    def calcular_costo(self, descuento=0.0, impuesto=0.19, recargo_extra=0.0):
        # Polimorfismo: alquiler de equipos incluye un recargo fijo de mantenimiento/soporte de $15.0
        return super().calcular_costo(
            descuento=descuento,
            impuesto=impuesto,
            recargo_extra=recargo_extra + 15.0
        )

    def describir_servicio(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"[Equipo] Código: {self.codigo} | Tipo: {self.tipo_equipo} | Costo Base: ${self.costo_base:,.2f} | {estado}"

    def obtener_informacion(self):
        return self.describir_servicio()


class AsesoriaEspecializada(Servicio):
    def __init__(self, codigo, costo_base, area, disponible=True):
        self.area = str(area).strip()
        super().__init__(codigo, "Asesoría Especializada", costo_base, disponible=disponible)
        registrar_log(f"Servicio de asesoría creado: {self.codigo} ({self.area})")

    def validar_parametros(self):
        if not self.area:
            err = f"El área de la asesoría para el servicio {self.codigo} no puede estar vacía."
            registrar_log(err, "ERROR")
            raise ErrorDatoInvalido(err)

    def calcular_costo(self, descuento=0.0, impuesto=0.19, recargo_extra=0.0):
        # Polimorfismo: asesorías especializadas aplican tarifa directa sin recargo fijo adicional
        return super().calcular_costo(
            descuento=descuento,
            impuesto=impuesto,
            recargo_extra=recargo_extra
        )

    def describir_servicio(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"[Asesoría] Código: {self.codigo} | Área: {self.area} | Costo Base: ${self.costo_base:,.2f} | {estado}"

    def obtener_informacion(self):
        return self.describir_servicio()


# =========================================================================
# 6. CLASE RESERVA CON MANEJO AVANZADO DE EXCEPCIONES
# =========================================================================

class Reserva(EntidadBase):
    def __init__(self, codigo_reserva, cliente, servicio, duracion_horas):
        cod_clean = str(codigo_reserva).strip().upper()
        if not cod_clean:
            err = "El código de la reserva no puede estar vacío."
            registrar_log(err, "ERROR")
            raise ErrorReserva(err)

        if not isinstance(cliente, Cliente):
            err = f"Reserva {cod_clean}: cliente inválido o faltante."
            registrar_log(err, "ERROR")
            raise ErrorReserva(err)

        if not isinstance(servicio, Servicio):
            err = f"Reserva {cod_clean}: servicio inválido o faltante."
            registrar_log(err, "ERROR")
            raise ErrorReserva(err)

        if not servicio.disponible:
            err = f"Reserva {cod_clean}: el servicio {servicio.codigo} no está disponible."
            registrar_log(err, "ERROR")
            raise ServicioNoDisponibleError(err)

        try:
            horas_int = int(duracion_horas)
        except (TypeError, ValueError) as exc:
            err = f"Duración de reserva inválida en {cod_clean}: {duracion_horas}"
            registrar_log(err, "ERROR")
            raise ErrorReserva(err) from exc

        if horas_int <= 0:
            err = f"Duración de reserva inválida: {horas_int} horas. Debe ser mayor a 0."
            registrar_log(err, "ERROR")
            raise ErrorReserva(err)

        self.codigo_reserva = cod_clean
        self.cliente = cliente
        self.servicio = servicio
        self.duracion_horas = horas_int
        self.estado = "Pendiente"
        self.costo_calculado = 0.0
        registrar_log(f"Reserva {self.codigo_reserva} creada en estado Pendiente para {self.cliente.obtener_nombre()}.")

    def confirmar_reserva(self):
        try:
            if self.estado == "Cancelada":
                raise ErrorReserva(f"No se puede confirmar la reserva {self.codigo_reserva} porque está cancelada.")
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio {self.servicio.codigo} dejó de estar disponible.")
            self.estado = "Confirmada"
        except Exception as e:
            registrar_log(f"Error al confirmar reserva {self.codigo_reserva}: {e}", "ERROR")
            raise
        else:
            registrar_log(f"Reserva {self.codigo_reserva} confirmada.")
            return self.estado
        finally:
            pass

    def cancelar_reserva(self, motivo="Cancelación solicitada por el usuario"):
        try:
            if self.estado == "Cancelada":
                raise ErrorReserva(f"La reserva {self.codigo_reserva} ya se encuentra cancelada.")
            self.estado = "Cancelada"
        except Exception as e:
            registrar_log(f"Error al cancelar reserva {self.codigo_reserva}: {e}", "ERROR")
            raise
        else:
            registrar_log(f"Reserva {self.codigo_reserva} cancelada. Motivo: {motivo}")
            return self.estado
        finally:
            pass

    def procesar_reserva(self, descuento=0.0, impuesto=0.19):
        costo_total = 0.0
        try:
            registrar_log(f"Iniciando procesamiento de reserva {self.codigo_reserva}...")
            if self.estado == "Cancelada":
                raise ErrorReserva(f"No se puede procesar una reserva cancelada ({self.codigo_reserva}).")
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"Servicio {self.servicio.codigo} no disponible al procesar.")

            costo_unitario = self.servicio.calcular_costo(descuento=descuento, impuesto=impuesto)
            costo_total = round(costo_unitario * self.duracion_horas, 2)
            self.costo_calculado = costo_total

        except ZeroDivisionError as zde:
            registrar_log(f"Error aritmético en reserva {self.codigo_reserva}: {zde}", "ERROR")
            raise ErrorReserva("Error de cálculo por división en cero.") from zde
        except ServicioNoDisponibleError:
            raise
        except Exception as e:
            registrar_log(f"Falla crítica procesando reserva {self.codigo_reserva}: {e}", "ERROR")
            raise ErrorReserva(f"No se pudo procesar la reserva: {e}") from e
        else:
            self.estado = "Confirmada"
            registrar_log(f"Reserva {self.codigo_reserva} confirmada de forma exitosa. Total: ${costo_total:,.2f}")
            return costo_total
        finally:
            print(f">>> [LOG TRANSACCIÓN]: Finalizó intento de procesamiento para la reserva {self.codigo_reserva} (Estado: {self.estado})")

    def obtener_informacion(self):
        return (
            f"Reserva: {self.codigo_reserva} | Cliente: {self.cliente.obtener_nombre()} | "
            f"Servicio: {self.servicio.codigo} | Duración: {self.duracion_horas}h | "
            f"Total: ${self.costo_calculado:,.2f} | Estado: {self.estado}"
        )


# =========================================================================
# 7. SIMULACIÓN DE LAS 10 OPERACIONES (EXIGIDO POR LA GUÍA)
# =========================================================================

def ejecutar_simulacion_10_operaciones():
    reporte = []
    reporte.append("==================================================")
    reporte.append(" INICIO DE SIMULACIÓN DE 10 OPERACIONES (SOFTWARE FJ)")
    reporte.append("==================================================\n")

    clientes = []
    servicios = []
    reservas = []

    # Op 1: Registro válido de cliente
    try:
        c1 = Cliente("Ana María Pérez", "123456", "ana@correo.com", "3104567890")
        clientes.append(c1)
        reporte.append("[Op 1 - ÉXITO]: Cliente registrado correctamente.")
    except Exception as e:
        reporte.append(f"[Op 1 - ERROR]: {e}")

    # Op 2: Registro inválido de cliente (Excepción personalizada)
    try:
        c_malo = Cliente("Carlos", "123", "carlos@correo.com", "320123456")
        clientes.append(c_malo)
    except ErrorDatoInvalido as e:
        reporte.append(f"[Op 2 - CAPTURADA]: Excepción controlada con éxito -> {e}")

    # Op 3: Creación válida de Servicio 1 (Sala)
    try:
        s1 = ReservaSalas("SLA-01", 100.0, 20)
        servicios.append(s1)
        reporte.append(f"[Op 3 - ÉXITO]: Servicio creado -> {s1.describir_servicio()}")
    except Exception as e:
        reporte.append(f"[Op 3 - ERROR]: {e}")

    # Op 4: Creación válida de Servicio 2 (Equipo)
    try:
        s2 = AlquilerEquipos("EQP-02", 50.0, "Servidor Cloud Core")
        servicios.append(s2)
        reporte.append(f"[Op 4 - ÉXITO]: Servicio creado -> {s2.describir_servicio()}")
    except Exception as e:
        reporte.append(f"[Op 4 - ERROR]: {e}")

    # Op 5: Creación válida de Servicio 3 (Asesoría)
    try:
        s3 = AsesoriaEspecializada("ASR-03", 180.0, "Arquitectura de Software")
        servicios.append(s3)
        reporte.append(f"[Op 5 - ÉXITO]: Servicio creado -> {s3.describir_servicio()}")
    except Exception as e:
        reporte.append(f"[Op 5 - ERROR]: {e}")

    # Op 6: Creación inválida de servicio (Costo negativo / No disponible)
    try:
        s_malo = ReservaSalas("SLA-02", -200.0, 10)
        servicios.append(s_malo)
    except ServicioNoDisponibleError as e:
        reporte.append(f"[Op 6 - CAPTURADA]: Excepción de servicio controlada -> {e}")

    # Op 7: Reserva Exitosa 1 (Sala con descuento)
    try:
        res1 = Reserva("RES-101", clientes[0], servicios[0], duracion_horas=4)
        total = res1.procesar_reserva(descuento=0.10)
        reservas.append(res1)
        reporte.append(f"[Op 7 - ÉXITO]: Reserva procesada. Total a pagar: ${total:,.2f}")
    except Exception as e:
        reporte.append(f"[Op 7 - ERROR]: {e}")

    # Op 8: Reserva Exitosa 2 (Equipo sin descuento)
    try:
        res2 = Reserva("RES-102", clientes[0], servicios[1], duracion_horas=6)
        total = res2.procesar_reserva()
        reservas.append(res2)
        reporte.append(f"[Op 8 - ÉXITO]: Reserva procesada. Total a pagar: ${total:,.2f}")
    except Exception as e:
        reporte.append(f"[Op 8 - ERROR]: {e}")

    # Op 9: Reserva Fallida por duración en cero
    try:
        res_falla = Reserva("RES-103", clientes[0], servicios[2], duracion_horas=0)
        reservas.append(res_falla)
    except ErrorReserva as e:
        reporte.append(f"[Op 9 - CAPTURADA]: Excepción de reserva inválida capturada -> {e}")

    # Op 10: Cancelación válida de reserva y validación de doble cancelación fallida
    try:
        if reservas:
            reservas[-1].cancelar_reserva("Cambio de cronograma")
            try:
                reservas[-1].cancelar_reserva("Intento duplicado")
            except ErrorReserva as err_dup:
                reporte.append(f"[Op 10 - ÉXITO Y CONTROL]: Reserva cancelada; duplicado bloqueado -> {err_dup}")
        else:
            reporte.append("[Op 10 - AVISO]: No había reservas activas para cancelar.")
    except Exception as e:
        reporte.append(f"[Op 10 - ERROR]: {e}")

    reporte.append("\n==================================================")
    reporte.append(" SIMULACIÓN DE 10 OPERACIONES FINALIZADA CON ÉXITO")
    reporte.append("==================================================")

    texto_final = "\n".join(reporte)
    print("\n" + texto_final + "\n")
    return texto_final, clientes, servicios, reservas


# =========================================================================
# 8. INTERFAZ GRÁFICA (PRUEBA FUNCIONAL Y DE GESTIÓN INTEGRAL)
# =========================================================================

class AplicacionSoftwareFJ:
    def __init__(self, ventana):
        self.clientes_registrados = []
        self.servicios_registrados = []
        self.reservas_registradas = []

        ventana.title("Software FJ - Sistema Integral de Gestión")
        ventana.geometry("760x720")

        marco_principal = tk.Frame(ventana, padx=12, pady=12)
        marco_principal.pack(fill="both", expand=True)

        tk.Label(
            marco_principal,
            text="Software FJ - Gestión de Clientes, Servicios y Reservas",
            font=("arial", 13, "bold"),
            fg="darkblue"
        ).pack(pady=(0, 8))

        notebook = ttk.Notebook(marco_principal)
        notebook.pack(fill="both", expand=True)

        # Pestaña 1: Clientes
        tab_clientes = tk.Frame(notebook, padx=10, pady=10)
        notebook.add(tab_clientes, text="Clientes")
        self._construir_tab_clientes(tab_clientes)

        # Pestaña 2: Servicios
        tab_servicios = tk.Frame(notebook, padx=10, pady=10)
        notebook.add(tab_servicios, text="Servicios")
        self._construir_tab_servicios(tab_servicios)

        # Pestaña 3: Reservas y Simulación
        tab_reservas = tk.Frame(notebook, padx=10, pady=10)
        notebook.add(tab_reservas, text="Reservas y Simulación")
        self._construir_tab_reservas(tab_reservas)

        # Consola inferior compartida de eventos y resultados
        tk.Label(
            marco_principal,
            text="Consola de Eventos, Resultados y Excepciones Capturadas:",
            font=("arial", 9, "bold")
        ).pack(anchor="w", pady=(8, 2))

        self.salida_texto = tk.Text(marco_principal, width=85, height=9)
        self.salida_texto.pack(fill="x")

    def escribir_salida(self, texto):
        self.salida_texto.delete("1.0", tk.END)
        self.salida_texto.insert(tk.END, texto)

    def _refrescar_combos_reservas(self):
        nombres_clientes = [
            f"{c.obtener_identificacion()} - {c.obtener_nombre()}"
            for c in self.clientes_registrados
        ]
        codigos_servicios = [
            f"{s.codigo} - {s.nombre_servicio}"
            for s in self.servicios_registrados
        ]
        self.combo_cliente["values"] = nombres_clientes
        self.combo_servicio["values"] = codigos_servicios
        if nombres_clientes and not self.combo_cliente.get():
            self.combo_cliente.current(0)
        if codigos_servicios and not self.combo_servicio.get():
            self.combo_servicio.current(0)

    def _refrescar_lista_reservas(self):
        self.lista_reservas.delete(0, tk.END)
        for r in self.reservas_registradas:
            self.lista_reservas.insert(tk.END, r.obtener_informacion())

    # --- PESTAÑA CLIENTES ---
    def _construir_tab_clientes(self, parent):
        self.entradas_cliente = {}
        campos = ["Nombre Completo", "Identificación", "Correo Electrónico", "Teléfono"]

        for idx, texto in enumerate(campos):
            tk.Label(parent, text=texto + ":", font=("arial", 10)).grid(row=idx, column=0, sticky="w", pady=4)
            entry = tk.Entry(parent, width=36)
            entry.grid(row=idx, column=1, pady=4, padx=6)
            self.entradas_cliente[texto] = entry

        tk.Button(
            parent, text="Registrar Cliente (Validar)", command=self.registrar_cliente_gui,
            bg="#28A745", fg="white", font=("arial", 10, "bold"), width=28
        ).grid(row=len(campos), column=0, columnspan=2, pady=10)

        tk.Label(parent, text="Clientes Registrados en Memoria:", font=("arial", 9, "bold")).grid(
            row=len(campos) + 1, column=0, columnspan=2, sticky="w"
        )
        self.lista_clientes = tk.Listbox(parent, width=82, height=7)
        self.lista_clientes.grid(row=len(campos) + 2, column=0, columnspan=2, pady=4)

    def registrar_cliente_gui(self):
        nombre = self.entradas_cliente["Nombre Completo"].get()
        identificacion = self.entradas_cliente["Identificación"].get()
        correo = self.entradas_cliente["Correo Electrónico"].get()
        telefono = self.entradas_cliente["Teléfono"].get()

        try:
            nuevo_cliente = Cliente(nombre, identificacion, correo, telefono)
            self.clientes_registrados.append(nuevo_cliente)
            self.lista_clientes.insert(tk.END, nuevo_cliente.obtener_informacion())
            self._refrescar_combos_reservas()

            msg = f"Éxito: {nuevo_cliente.obtener_informacion()}"
            self.escribir_salida(msg)
            messagebox.showinfo("Registro Exitoso", "Cliente registrado correctamente.")

            for entry in self.entradas_cliente.values():
                entry.delete(0, tk.END)
        except ErrorDatoInvalido as e:
            self.escribir_salida(f"Excepción Controlada (Dato Inválido): {e}")
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            self.escribir_salida(f"Error Inesperado: {e}")
            messagebox.showerror("Error Crítico", str(e))

    # --- PESTAÑA SERVICIOS ---
    def _construir_tab_servicios(self, parent):
        tk.Label(parent, text="Tipo de Servicio:", font=("arial", 10)).grid(row=0, column=0, sticky="w", pady=4)
        self.combo_tipo_servicio = ttk.Combobox(
            parent,
            values=["Reserva de Salas", "Alquiler de Equipos", "Asesoría Especializada"],
            state="readonly",
            width=33
        )
        self.combo_tipo_servicio.current(0)
        self.combo_tipo_servicio.grid(row=0, column=1, pady=4, padx=6)
        self.combo_tipo_servicio.bind("<<ComboboxSelected>>", self._actualizar_campo_servicio)

        tk.Label(parent, text="Código Servicio:", font=("arial", 10)).grid(row=1, column=0, sticky="w", pady=4)
        self.entry_cod_servicio = tk.Entry(parent, width=36)
        self.entry_cod_servicio.grid(row=1, column=1, pady=4, padx=6)

        tk.Label(parent, text="Costo Base:", font=("arial", 10)).grid(row=2, column=0, sticky="w", pady=4)
        self.entry_costo_base = tk.Entry(parent, width=36)
        self.entry_costo_base.grid(row=2, column=1, pady=4, padx=6)

        self.lbl_param_extra = tk.Label(parent, text="Capacidad (personas):", font=("arial", 10))
        self.lbl_param_extra.grid(row=3, column=0, sticky="w", pady=4)
        self.entry_param_extra = tk.Entry(parent, width=36)
        self.entry_param_extra.grid(row=3, column=1, pady=4, padx=6)

        self.var_disponible = tk.BooleanVar(value=True)
        tk.Checkbutton(parent, text="Servicio disponible para reservas", variable=self.var_disponible).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=4
        )

        tk.Button(
            parent, text="Registrar Servicio", command=self.registrar_servicio_gui,
            bg="#007ACC", fg="white", font=("arial", 10, "bold"), width=24
        ).grid(row=5, column=0, pady=8)

        tk.Button(
            parent, text="Alternar Disponibilidad", command=self.alternar_disponibilidad_gui,
            font=("arial", 9, "bold"), width=24
        ).grid(row=5, column=1, pady=8)

        self.lista_servicios = tk.Listbox(parent, width=82, height=6)
        self.lista_servicios.grid(row=6, column=0, columnspan=2, pady=4)

    def _actualizar_campo_servicio(self, _event=None):
        tipo = self.combo_tipo_servicio.get()
        if tipo == "Reserva de Salas":
            self.lbl_param_extra.config(text="Capacidad (personas):")
        elif tipo == "Alquiler de Equipos":
            self.lbl_param_extra.config(text="Tipo de Equipo:")
        else:
            self.lbl_param_extra.config(text="Área Especializada:")

    def _refrescar_lista_servicios(self):
        self.lista_servicios.delete(0, tk.END)
        for s in self.servicios_registrados:
            self.lista_servicios.insert(tk.END, s.describir_servicio())
        self._refrescar_combos_reservas()

    def registrar_servicio_gui(self):
        tipo = self.combo_tipo_servicio.get()
        codigo = self.entry_cod_servicio.get()
        costo_str = self.entry_costo_base.get()
        extra = self.entry_param_extra.get()
        disp = self.var_disponible.get()

        try:
            try:
                costo_val = float(costo_str)
            except ValueError as exc:
                raise ErrorDatoInvalido(f"Costo base no numérico: '{costo_str}'") from exc

            if tipo == "Reserva de Salas":
                servicio = ReservaSalas(codigo, costo_val, extra, disponible=disp)
            elif tipo == "Alquiler de Equipos":
                servicio = AlquilerEquipos(codigo, costo_val, extra, disponible=disp)
            else:
                servicio = AsesoriaEspecializada(codigo, costo_val, extra, disponible=disp)

            self.servicios_registrados.append(servicio)
            self._refrescar_lista_servicios()
            self.escribir_salida(f"Servicio registrado: {servicio.describir_servicio()}")
            messagebox.showinfo("Servicio Creado", "Servicio registrado correctamente.")

            self.entry_cod_servicio.delete(0, tk.END)
            self.entry_costo_base.delete(0, tk.END)
            self.entry_param_extra.delete(0, tk.END)
        except (ErrorDatoInvalido, ServicioNoDisponibleError) as e:
            self.escribir_salida(f"Excepción Controlada en Servicio: {e}")
            messagebox.showerror("Error de Servicio", str(e))
        except Exception as e:
            self.escribir_salida(f"Error Inesperado en Servicio: {e}")
            messagebox.showerror("Error Crítico", str(e))

    def alternar_disponibilidad_gui(self):
        sel = self.lista_servicios.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un servicio en la lista.")
            return
        servicio = self.servicios_registrados[sel[0]]
        servicio.cambiar_disponibilidad(not servicio.disponible)
        self._refrescar_lista_servicios()
        self.escribir_salida(f"Disponibilidad actualizada -> {servicio.describir_servicio()}")

    # --- PESTAÑA RESERVAS Y SIMULACIÓN ---
    def _construir_tab_reservas(self, parent):
        tk.Label(parent, text="Código Reserva:", font=("arial", 9)).grid(row=0, column=0, sticky="w", pady=2)
        self.entry_cod_reserva = tk.Entry(parent, width=22)
        self.entry_cod_reserva.grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(parent, text="Duración (horas):", font=("arial", 9)).grid(row=0, column=2, sticky="w", pady=2)
        self.entry_duracion = tk.Entry(parent, width=12)
        self.entry_duracion.insert(0, "2")
        self.entry_duracion.grid(row=0, column=3, sticky="w", pady=2)

        tk.Label(parent, text="Cliente:", font=("arial", 9)).grid(row=1, column=0, sticky="w", pady=2)
        self.combo_cliente = ttk.Combobox(parent, state="readonly", width=28)
        self.combo_cliente.grid(row=1, column=1, columnspan=2, sticky="w", pady=2)

        tk.Label(parent, text="Servicio:", font=("arial", 9)).grid(row=2, column=0, sticky="w", pady=2)
        self.combo_servicio = ttk.Combobox(parent, state="readonly", width=28)
        self.combo_servicio.grid(row=2, column=1, columnspan=2, sticky="w", pady=2)

        tk.Label(parent, text="Descuento (0.0 - 0.9):", font=("arial", 9)).grid(row=2, column=2, sticky="w", pady=2)
        self.entry_descuento = tk.Entry(parent, width=12)
        self.entry_descuento.insert(0, "0.0")
        self.entry_descuento.grid(row=2, column=3, sticky="w", pady=2)

        btn_frame = tk.Frame(parent)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=6)

        tk.Button(btn_frame, text="Crear y Procesar", command=self.crear_procesar_reserva_gui, bg="#28A745", fg="white").pack(side="left", padx=3)
        tk.Button(btn_frame, text="Confirmar", command=self.confirmar_reserva_gui, bg="#007ACC", fg="white").pack(side="left", padx=3)
        tk.Button(btn_frame, text="Cancelar", command=self.cancelar_reserva_gui, bg="#DC3545", fg="white").pack(side="left", padx=3)
        tk.Button(btn_frame, text="Simular 10 Operaciones", command=self.correr_simulacion_gui, bg="#6F42C1", fg="white").pack(side="left", padx=3)

        self.lista_reservas = tk.Listbox(parent, width=82, height=6)
        self.lista_reservas.grid(row=4, column=0, columnspan=4, pady=4)

    def _obtener_reserva_seleccionada(self):
        sel = self.lista_reservas.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una reserva de la lista.")
            return None
        return self.reservas_registradas[sel[0]]

    def crear_procesar_reserva_gui(self):
        idx_c = self.combo_cliente.current()
        idx_s = self.combo_servicio.current()
        cod = self.entry_cod_reserva.get()
        dur = self.entry_duracion.get()
        desc_str = self.entry_descuento.get()

        try:
            if idx_c < 0 or idx_s < 0:
                raise ErrorReserva("Debe seleccionar un cliente y un servicio registrados.")
            try:
                desc_val = float(desc_str)
            except ValueError as exc:
                raise ErrorDatoInvalido(f"Descuento no numérico: '{desc_str}'") from exc

            cliente = self.clientes_registrados[idx_c]
            servicio = self.servicios_registrados[idx_s]
            reserva = Reserva(cod, cliente, servicio, dur)
            total = reserva.procesar_reserva(descuento=desc_val)

            self.reservas_registradas.append(reserva)
            self._refrescar_lista_reservas()
            msg = f"Reserva {reserva.codigo_reserva} confirmada. Total a pagar: ${total:,.2f}"
            self.escribir_salida(msg)
            messagebox.showinfo("Reserva Procesada", msg)
            self.entry_cod_reserva.delete(0, tk.END)
        except (ErrorReserva, ServicioNoDisponibleError, ErrorDatoInvalido) as e:
            self.escribir_salida(f"Excepción Controlada en Reserva: {e}")
            messagebox.showerror("Error en Reserva", str(e))
        except Exception as e:
            self.escribir_salida(f"Error Inesperado en Reserva: {e}")
            messagebox.showerror("Error Crítico", str(e))

    def confirmar_reserva_gui(self):
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return
        try:
            estado = reserva.confirmar_reserva()
            self._refrescar_lista_reservas()
            self.escribir_salida(f"Reserva {reserva.codigo_reserva} estado: {estado}")
        except (ErrorReserva, ServicioNoDisponibleError) as e:
            self.escribir_salida(f"Error al confirmar: {e}")
            messagebox.showerror("Error", str(e))

    def cancelar_reserva_gui(self):
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return
        try:
            estado = reserva.cancelar_reserva("Cancelada desde interfaz gráfica")
            self._refrescar_lista_reservas()
            self.escribir_salida(f"Reserva {reserva.codigo_reserva} estado: {estado}")
        except ErrorReserva as e:
            self.escribir_salida(f"Error al cancelar: {e}")
            messagebox.showerror("Error", str(e))

    def correr_simulacion_gui(self):
        texto_sim, cli, serv, res = ejecutar_simulacion_10_operaciones()
        self.clientes_registrados.extend(cli)
        self.servicios_registrados.extend(serv)
        self.reservas_registradas.extend(res)

        self.lista_clientes.delete(0, tk.END)
        for c in self.clientes_registrados:
            self.lista_clientes.insert(tk.END, c.obtener_informacion())

        self._refrescar_lista_servicios()
        self._refrescar_lista_reservas()
        self.escribir_salida(texto_sim)
        messagebox.showinfo("Simulación Completada", "Se ejecutaron las 10 operaciones y se registraron en sistema_log.txt.")


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