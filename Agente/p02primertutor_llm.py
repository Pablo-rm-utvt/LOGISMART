# ============================================================
# PRACTICA 2: TUTOR INTELIGENTE CON LLM
# ============================================================

# 1. IMPORTAR LAS BIBLIOTECAS
import tkinter as tk
import ollama


# 2. CONFIGURACIÓN DEL MODELO
MODELO = "llama3.2"


# 3. CONFIGURACIÓN DEL SISTEMA
mensaje_sistema = """
Eres un profesor especializado en gramática y lingüística.

Tu función es ayudar a estudiantes universitarios.

Debes:
1. Explicar los conceptos de manera clara.
2. Utilizar ejemplos sencillos.
3. Explicar los conceptos gramaticales.
4. Evitar respuestas excesivamente técnicas para principiantes.
5. Explicar cómo corregir los errores.
6. Explicar el razonamiento, no solo dar la respuesta final.
7. Usar emojis ocasionalmente para hacer la conversación más amena.
"""


# 4. CREAR HISTORIAL
mensajes = [{"role": "system", "content": mensaje_sistema}]


# 5. FUNCIONES DE LA INTERFAZ
def agregar_mensaje(autor, texto):
	area_chat.configure(state="normal")
	area_chat.insert("end", f"{autor}:\n{texto}\n\n")
	area_chat.see("end")
	area_chat.configure(state="disabled")


def enviar_pregunta(evento=None):
	pregunta = campo_pregunta.get().strip()
	if not pregunta:
		return

	campo_pregunta.delete(0, "end")
	mensajes.append({"role": "user", "content": pregunta})
	agregar_mensaje("Estudiante", pregunta)
	ventana.update_idletasks()

	try:
		respuesta = ollama.chat(model=MODELO, messages=mensajes)
		contenido = respuesta["message"]["content"]
		mensajes.append({"role": "assistant", "content": contenido})
		agregar_mensaje("Don Beto", contenido)
		estado.configure(text="Listo para otra pregunta")
	except Exception as error:
		mensajes.pop()
		agregar_mensaje("Error", f"No se pudo conectar con Ollama: {error}")
		estado.configure(text="Revisa que Ollama esté iniciado y que llama3.2 esté instalado")

	campo_pregunta.focus_set()


def mostrar_resumen():
	conversacion = [mensaje for mensaje in mensajes if mensaje["role"] != "system"]
	if not conversacion:
		agregar_mensaje("Resumen", "Todavía no hay mensajes para resumir.")
		return

	transcripcion = "\n\n".join(
		f"{'Estudiante' if mensaje['role'] == 'user' else 'Tutor'}: {mensaje['content']}"
		for mensaje in conversacion
	)
	peticion_resumen = [
		{
			"role": "system",
			"content": (
				"Resume en español toda la conversación del mensaje siguiente, "
				"desde el primer turno hasta el último. Incluye los temas y "
				"aprendizajes importantes. No inventes información."
			),
		},
		{"role": "user", "content": f"Conversación completa:\n\n{transcripcion}"},
	]

	boton_resumen.configure(state="disabled", text="Preparando...")
	estado.configure(text="Preparando el resumen de toda la conversación...")
	ventana.update_idletasks()
	try:
		respuesta = ollama.chat(model=MODELO, messages=peticion_resumen)
		agregar_mensaje("Resumen de la conversación", respuesta["message"]["content"])
		estado.configure(text="Resumen listo")
	except Exception as error:
		agregar_mensaje("Error", f"No se pudo generar el resumen: {error}")
		estado.configure(text="Revisa que Ollama esté iniciado")
	finally:
		boton_resumen.configure(state="normal", text="Mostrar resumen")


# 6. CREAR LA INTERFAZ GRÁFICA
ventana = tk.Tk()
ventana.title("Don Beto GPT - Tutor de gramática")
ventana.geometry("850x620")
ventana.minsize(600, 450)
ventana.configure(bg="#F3F2EC")

barra_titulo = tk.Frame(ventana, bg="#173B36", padx=20, pady=15)
barra_titulo.pack(fill="x")
tk.Label(
	barra_titulo,
	text="Don Beto GPT",
	font=("TkDefaultFont", 16, "bold"),
	fg="white",
	bg="#173B36",
).pack(anchor="w")
tk.Label(
	barra_titulo,
	text=f"Tutor de gramática y lingüística · {MODELO}",
	font=("TkDefaultFont", 10),
	fg="#D2DFD2",
	bg="#173B36",
).pack(anchor="w", pady=(4, 0))

contenido = tk.Frame(ventana, bg="#F3F2EC", padx=20, pady=16)
contenido.pack(fill="both", expand=True)
contenido.rowconfigure(1, weight=1)
contenido.columnconfigure(0, weight=1)

tk.Label(
	contenido,
	text="Escribe una pregunta sobre gramática o lingüística.",
	font=("TkDefaultFont", 10),
	fg="#53625C",
	bg="#F3F2EC",
).grid(row=0, column=0, sticky="w", pady=(0, 10))

area_chat_frame = tk.Frame(contenido, bg="white")
area_chat_frame.grid(row=1, column=0, sticky="nsew")
area_chat_frame.rowconfigure(0, weight=1)
area_chat_frame.columnconfigure(0, weight=1)

area_chat = tk.Text(
	area_chat_frame,
	wrap="word",
	state="disabled",
	font=("TkDefaultFont", 10),
	fg="#20352F",
	bg="white",
	relief="flat",
	padx=14,
	pady=12,
)
area_chat.grid(row=0, column=0, sticky="nsew")
barra_desplazamiento = tk.Scrollbar(area_chat_frame, command=area_chat.yview)
barra_desplazamiento.grid(row=0, column=1, sticky="ns")
area_chat.configure(yscrollcommand=barra_desplazamiento.set)

compositor = tk.Frame(contenido, bg="white", padx=8, pady=8)
compositor.grid(row=2, column=0, sticky="ew", pady=(10, 0))
compositor.columnconfigure(0, weight=1)

campo_pregunta = tk.Entry(
	compositor,
	font=("TkDefaultFont", 10),
	fg="#20352F",
	bg="white",
	relief="flat",
)
campo_pregunta.grid(row=0, column=0, sticky="ew", padx=8, ipady=8)
campo_pregunta.bind("<Return>", enviar_pregunta)

boton_enviar = tk.Button(
	compositor,
	text="Enviar",
	command=enviar_pregunta,
	font=("TkDefaultFont", 10, "bold"),
	fg="#173B36",
	bg="#D5EA67",
	relief="flat",
	padx=15,
	pady=8,
)
boton_enviar.grid(row=0, column=1, padx=(5, 0))

boton_resumen = tk.Button(
	contenido,
	text="Mostrar resumen",
	command=mostrar_resumen,
	font=("TkDefaultFont", 10, "bold"),
	fg="white",
	bg="#E86B4A",
	relief="flat",
	padx=15,
	pady=8,
)
boton_resumen.grid(row=3, column=0, sticky="e", pady=(10, 0))

estado = tk.Label(
	contenido,
	text="Listo para ayudarte",
	font=("TkDefaultFont", 9),
	fg="#71807A",
	bg="#F3F2EC",
)
estado.grid(row=4, column=0, sticky="w", pady=(7, 0))

agregar_mensaje("Don Beto", "¡Hola! ¿Qué tema de gramática quieres aprender hoy?")
campo_pregunta.focus_set()
ventana.mainloop()