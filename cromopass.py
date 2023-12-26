import tkinter as tk
from tkinter import ttk
import peewee
import csv
import secrets
import string
from tkinter import simpledialog
from tkinter import messagebox as MessageBox
import re

# Crear una base de datos SQLite3
db = peewee.SqliteDatabase('S:/_TECNOLOGIA/base/contraseñas.db')

# Definir un modelo de datos para la tabla de contraseñas
class Contraseña(peewee.Model):
    usuario = peewee.CharField()
    contrasena = peewee.CharField()
    tipo = peewee.CharField()
    email = peewee.CharField()
    comentario = peewee.CharField()  # Nuevo campo para comentarios
    
    class Meta:
        database = db

# Crear la tabla en la base de datos si no existe
db.connect()
db.create_tables([Contraseña], safe=True)

# Variable de control para rastrear el estado del botón
mostrar_contrasena = False

def agregar_contraseña():
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()
    tipo = combo_tipo.get()  # Obtener el valor seleccionado del Combobox
    comentario = entry_comentario.get()  # Obtener el valor del campo de comentarios

    asteriscos = '*' * len(contrasena)

    # Almacenar la contraseña en la base de datos
    def validar_email():
        email = entry_email.get()
        # Patrón de regex para validar un correo electrónico
        patron_email = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if re.match(patron_email, email):
            # Simplemente asegúrate de que estás utilizando el nombre correcto del modelo en tu código (Contraseña)
            Contraseña.create(usuario=usuario, contrasena=contrasena, tipo=tipo, email=email, comentario=comentario)

            # Insertar en el Treeview
            tree.insert("", "end", values=(usuario, asteriscos, tipo, email, comentario))

            # Limpiar los campos del formulario
            entry_usuario.delete(0, 'end')
            entry_contrasena.delete(0, 'end')
            combo_tipo.set("")  # Limpiar el valor del Combobox
            entry_email.delete(0, 'end')
            entry_comentario.delete(0, 'end')  # Limpiar el campo de comentarios
        else:
            MessageBox.showerror("Error", "No es un email válido.")
    validar_email()


def alternar_revelar_contrasena():
    global mostrar_contrasena
    mostrar_contrasena = not mostrar_contrasena
    if mostrar_contrasena:
        boton_revelar_contraseñas.config(text="Ocultar Contraseña")
    else:
        boton_revelar_contraseñas.config(text="Revelar Contraseña")
    
    revelar_contraseña()

def revelar_contraseña():
    selected_item = tree.selection()
    if selected_item:
        usuario = tree.item(selected_item, "values")[0]
        contrasena = Contraseña.get(Contraseña.usuario == usuario).contrasena
        if mostrar_contrasena:
            tree.item(selected_item, values=(usuario, contrasena, *tree.item(selected_item, "values")[2:]))
        else:
            asteriscos = '*' * len(contrasena)
            tree.item(selected_item, values=(usuario, asteriscos, *tree.item(selected_item, "values")[2:]))           


def borrar_usuario():
    selected_item = tree.selection()
    if selected_item:
        usuario = tree.item(selected_item, "values")[0]
        Contraseña.get(Contraseña.usuario == usuario).delete_instance()
        tree.delete(selected_item)

def exportar_a_csv():
    with open('usuarios.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Usuario', 'Contraseña', 'Tipo', 'Email', 'Comentario'])
        
        for registro in Contraseña.select():
            csv_writer.writerow([registro.usuario, registro.contrasena, registro.tipo, registro.email, registro.comentario])

def generar_clave():
    longitud = 8  # Puedes ajustar la longitud de la contraseña según tus necesidades
    caracteres = string.ascii_letters + string.digits + string.punctuation
    nueva_contraseña = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    entry_nueva_contraseña.configure(state='normal')  # Habilitar el Entry para editar
    entry_nueva_contraseña.delete(0, 'end')
    entry_nueva_contraseña.insert(0, nueva_contraseña)
    entry_nueva_contraseña.configure(state='readonly')  # Deshabilitar el Entry después de actualizar   

    
def copiar_contrasena(event):
    selected_item = tree.selection()
    if selected_item:
        contrasena = tree.item(selected_item, "values")[1]
        ventana.clipboard_clear()
        ventana.clipboard_append(contrasena)
        ventana.update()
        
def cargar_usuarios_desde_db():
    # Limpiar el Treeview antes de cargar nuevos registros
    for item in tree.get_children():
        tree.delete(item)

    for registro in Contraseña.select():
        tree.insert("", "end", values=(registro.usuario, '*' * len(registro.contrasena), registro.tipo, registro.email, registro.comentario))
        
def actualizar_contraseña():
    selected_item = tree.selection()
    if selected_item:
        usuario = entry_usuario.get()
        contrasena = entry_contrasena.get()
        tipo = combo_tipo.get()
        email = entry_email.get()
        comentario = entry_comentario.get()

        # Actualizar la contraseña en la base de datos
        registro = Contraseña.get(Contraseña.usuario == usuario)
        registro.contrasena = contrasena
        registro.tipo = tipo
        registro.email = email
        registro.comentario = comentario
        registro.save()

        # Actualizar la entrada en el Treeview
        asteriscos = '*' * len(contrasena)
        tree.item(selected_item, values=(usuario, asteriscos, tipo, email, comentario))

        # Limpiar los campos del formulario
        entry_usuario.delete(0, 'end')
        entry_contrasena.delete(0, 'end')
        combo_tipo.set("")
        entry_email.delete(0, 'end')
        entry_comentario.delete(0, 'end')

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Gestor de Contraseñas")
ventana.config(bg="#f0a38d")
#ventana.resizable(False, False)
#ventana.geometry("1200x800")

etiqueta_mensaje_error = tk.Label(ventana, text="", fg="red")


# Crear un Combobox para el campo "tipo"
opciones_tipo = ["Correo Especial", "Correo Personal", "Correo de Sector", "Usuario de Windows", "Colectoras", "VPN"]
combo_tipo = ttk.Combobox(ventana, values=opciones_tipo, text="Tipo")


# Crear un Treeview
tree = ttk.Treeview(ventana, columns=("usuario", "contrasena", "tipo", "email", "comentario"),height=25 )
tree.column("#0", width=0, stretch=tk.NO)
tree.column("#1",width=180 )
tree.column("#2",width=180 )
tree.column("#3",width=250 )
tree.column("#4",width=180 )
tree.column("#5",width=180 )

tree.heading("#0", text="", anchor=tk.W)
tree.heading("#1", text="Usuario", command=lambda: ordenar_columna("usuario"))
tree.heading("#2", text="Contraseña")
tree.heading("#3", text="Tipo")
tree.heading("#4", text="Email")
tree.heading("#5", text="Comentario")  # Nueva columna para comentarios

def seleccionar_elemento(event):
    selected_item = tree.selection()
    if selected_item:
        values = tree.item(selected_item, "values")
        entry_usuario.delete(0, 'end')
        entry_usuario.insert(0, values[0])
        entry_contrasena.delete(0, 'end')
        entry_contrasena.insert(0, values[1])
        combo_tipo.set(values[2])
        entry_email.delete(0, 'end')
        entry_email.insert(0, values[3])
        entry_comentario.delete(0, 'end')
        entry_comentario.insert(0, values[4])
        
def validar_email():
    email = entry_email.get()

    # Patrón de regex para validar un correo electrónico
    patron_email = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if re.match(patron_email, email):pass

    else:
        MessageBox.showerror("Error", "No es un email Valido.")

# Configurar variable para rastrear el estado de ordenamiento
ordenamiento_ascending = tk.BooleanVar()
ordenamiento_ascending.set(True)  # Inicialmente, ordenar de forma ascendente
        
def ordenar_columna(columna):
    # Obtener todos los elementos en la columna
    datos = [(tree.set(item, columna), item) for item in tree.get_children('')]

    # Determinar si se debe ordenar de forma ascendente o descendente
    orden_ascending = ordenamiento_ascending.get()
    datos.sort(reverse=orden_ascending)

    for i, (valor, item) in enumerate(datos):
        tree.move(item, '', i)

    # Cambiar el estado de ordenamiento
    ordenamiento_ascending.set(not orden_ascending)
    
def buscar():
    # Limpiar resultados anteriores
    limpiar_resultados()

    # Obtener el texto de búsqueda
    texto_busqueda = entry_busqueda.get().lower()

    # Buscar en el Treeview
    for item in tree.get_children():
        valores = tree.item(item, 'values')
        if texto_busqueda in [str(valor).lower() for valor in valores]:
            tree.selection_add(item)

def limpiar_resultados():
    # Limpiar la selección actual en el Treeview
    for item in tree.selection():
        tree.selection_remove(item)


# Asociar la función a la selección en el Treeview
tree.bind("<ButtonRelease-1>", seleccionar_elemento)

# Crear etiquetas (labels) para cada campo de entrada
label_usuario = tk.Label(ventana, text="Usuario:")
label_contrasena = tk.Label(ventana, text="Contraseña:")
label_tipo = tk.Label(ventana, text="Tipo:")
label_email = tk.Label(ventana, text="Email:")
label_comentario = tk.Label(ventana, text="Comentario:")  # Nueva etiqueta para comentarios
label_nueva_contraseña = tk.Label(ventana, text="Nueva Contraseña:")  # Nueva etiqueta para la contraseña generada
label_buscar = tk.Label(ventana, text="Buscar")  # Nueva etiqueta para buscar



# Crear un Entry para ingresar el nombre de usuario
entry_usuario = ttk.Entry(ventana, text="Nombre de Usuario")
entry_usuario.insert(0, "Usuario1")

# Crear un Entry para ingresar la contraseña
entry_contrasena = ttk.Entry(ventana, text="Contraseña", show="*")

# Crear un Entry para ingresar el tipo
entry_tipo = ttk.Entry(ventana, text="Tipo")

# Crear un Entry para ingresar el email
entry_email = ttk.Entry(ventana, text="Email")

# Crear un Entry para ingresar el comentario
entry_comentario = ttk.Entry(ventana, text="Comentario")

# Crear un Entry para mostrar la nueva contraseña generada
entry_nueva_contraseña = ttk.Entry(ventana, state='readonly', width=20)

# Crear un botón para agregar la contraseña
agregar_contraseña_button = tk.Button(ventana, text="Agregar Contraseña", command=agregar_contraseña)


# Crear un botón para borrar usuarios
borrar_usuario_button = tk.Button(ventana, text="Borrar Usuario", command=borrar_usuario)

# Crear un botón para exportar a CSV
boton_exportar_csv = tk.Button(ventana, text="Exportar a CSV", command=exportar_a_csv)

# Crear un botón y función para generar una nueva contraseña
boton_generar_clave = tk.Button(ventana, text="Generar Clave", command=generar_clave)

actualizar_contraseña_button = tk.Button(ventana, text="Actualizar Contraseña", command=actualizar_contraseña)

# Enlazar el evento de clic del mouse para copiar contraseña
tree.bind("<Button-1>", copiar_contrasena)

# Botón para revelar las contraseñas
boton_revelar_contraseñas = tk.Button(ventana, text="Revelar Contraseñas", command=alternar_revelar_contrasena)


# Llamar a cargar_usuarios_desde_db automáticamente al abrir el programa
cargar_usuarios_desde_db()

# Empacar los elementos en la ventana utilizando grid
label_usuario.grid(row=0, column=0, sticky=tk.E,padx=15,pady=15 )
entry_usuario.grid(row=0, column=1,padx=15,pady=15)
label_usuario.config(background="#f0a38d",font=('roboto', 10, 'bold'))

label_contrasena.grid(row=0, column=2, sticky=tk.E,padx=15,pady=15)
entry_contrasena.grid(row=0, column=3,padx=15,pady=15)
label_contrasena.config(background="#f0a38d",font=('roboto', 10, 'bold'))

label_tipo.grid(row=0, column=4, sticky=tk.E,padx=15,pady=15)
combo_tipo.grid(row=0, column=5,padx=15,pady=15)
label_tipo.config(background="#f0a38d",font=('roboto', 10, 'bold'))

label_email.grid(row=0, column=6, sticky=tk.E,padx=15,pady=15)
entry_email.grid(row=0, column=7,padx=15,pady=15)
label_email.config(background="#f0a38d",font=('roboto', 10, 'bold'))

label_comentario.grid(row=0, column=8, sticky=tk.E,padx=15,pady=15)
entry_comentario.grid(row=0, column=9,padx=15,pady=15)
label_comentario.config(background="#f0a38d",font=('roboto', 10, 'bold'))

label_nueva_contraseña.grid(row=0, column=10, sticky=tk.E,padx=15,pady=15)
entry_nueva_contraseña.grid(row=0, column=11,padx=15,pady=5)
label_nueva_contraseña.config(background="#f0a38d",font=('roboto', 10, 'bold'))

# Empacar los botones en la ventana utilizando grid
agregar_contraseña_button.grid(row=1, column=0, columnspan=2,padx=15,pady=5)
agregar_contraseña_button.config(bg="#9f9ece", width=15)

boton_revelar_contraseñas.grid(row=1, column=2,columnspan=2, padx=15, pady=10)
boton_revelar_contraseñas.config(bg="#9f9ece", width=15)

borrar_usuario_button.grid(row=1, column=4, columnspan=2,padx=15,pady=5)
borrar_usuario_button.config(bg="#9f9ece", width=15)

boton_exportar_csv.grid(row=1, column=6, columnspan=2,padx=15,pady=5)
boton_exportar_csv.config(bg="#9f9ece", width=15)

boton_generar_clave.grid(row=1, column=8, columnspan=2,padx=15,pady=5)
boton_generar_clave.config(bg="#9f9ece", width=15)

actualizar_contraseña_button.grid(row=1, column=10,columnspan=2, padx=15, pady=10)
actualizar_contraseña_button.config(bg="#9f9ece", width=20)

# Entry y botón de búsqueda
entry_busqueda = tk.Entry(ventana)
entry_busqueda.grid(row=4, column=5)

label_buscar.grid(row=4, column=4, sticky=tk.E,)
label_buscar.config(background="#f0a38d",font=('roboto', 10, 'bold'))

boton_buscar = tk.Button(ventana, text="Buscar", command=buscar)
boton_buscar.grid(row=4, column=6,pady=5, sticky="e" )
boton_buscar.config(bg="#9f9ece", width=15)

# Botón para limpiar resultados
boton_limpiar = tk.Button(ventana, text="Limpiar Resultados",  command=limpiar_resultados)
boton_limpiar.grid(row=4, column=7,padx=15,pady=5)
boton_limpiar.config(bg="#9f9ece", width=15 )

# Crear un Scrollbar
scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)

# Configurar la relación entre el Treeview y el Scrollbar
tree.configure(yscrollcommand=scrollbar.set)

# Ubicar el Scrollbar a la derecha del Treeview
scrollbar.grid(row=5, column=10, sticky="ns")


style = ttk.Style()
style.configure(
    "Treeview.Heading",
    foreground="blue",
    fieldbackground="black",
    font=("Georgia", 12, "bold"),
        )
style.configure(
    "Treeview",
    background="#C8E0E0",
    foreground="black",
    fieldbackground="silver",
    font=("Arial", 10, "bold"),
        )    

tree.grid(row=5, column=1, columnspan=10 )

ventana.mainloop()
