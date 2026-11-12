# Software-FJ-Grupo-54
Sistema Integral de Gestión de Clientes, Servicios y Reservas realizado por el grupo de estudiantes 54 del curso de programación
Las reglas para las validaciones de la clase cliente del programa son las siguientes:
Validación de Nombre Completo:

Regla: El campo no puede estar vacío ni contener únicamente espacios en blanco.

Condición: if not nom_clean:

Mensaje de Error: "El nombre del cliente no puede estar vacío."

Validación de Identificación:

Regla: Debe ser un valor estrictamente numérico y tener una longitud mínima de 5 dígitos.

Condición: if not id_clean.isdigit() or len(id_clean) < 5:

Mensaje de Error: f"La identificación '{id_clean}' es inválida. Debe ser numérica y tener al menos 5 dígitos."

Validación de Correo Electrónico:

Regla: Debe contener obligatoriamente el carácter @ y un punto (.) para estructurar el dominio.

Condición: if "@" not in correo_clean or "." not in correo_clean:

Mensaje de Error: f"El correo electrónico '{correo_clean}' es inválido. Debe contener '@' y un dominio válido."

Validación de Teléfono:

Regla: Debe ser numérico y contener como mínimo 7 dígitos.

Condición: if not tel_clean.isdigit() or len(tel_clean) < 7:

Mensaje de Error: f"El teléfono '{tel_clean}' es inválido. Debe contener al menos 7 dígitos numéricos."

