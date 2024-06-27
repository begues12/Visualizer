
import os
from tkinter import Listbox, Entry
from tkinter import ttk

class Images:
    
    def __init__(self):
        pass
    
    def load_images(self):
        image_folder = os.path.join(os.path.dirname(__file__), "images")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        for file_name in os.listdir(image_folder):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.image_listbox.insert(END, file_name)
    
    def tab(self, parent):
        image_frame = ttk.Frame(parent)
        image_frame.pack(padx=10, pady=10, fill='both', expand=True)

        label = ttk.Label(image_frame, text="Available Images")
        label.grid(row=0, column=0, columnspan=2, pady=5, padx=5)  # Extender la etiqueta a dos columnas

        self.image_listbox = Listbox(image_frame, selectmode='single', width=50)
        self.image_listbox.bind("<<ListboxSelect>>", lambda event: self.load_image_size_entries())
        self.image_listbox.grid(row=1, column=0, columnspan=2, pady=5, padx=5)  # Extender el Listbox a dos columnas

        self.load_images()

        # Entrada para la anchura de la imagen
        ttk.Label(image_frame, text="Width:").grid(row=2, column=0, pady=5, padx=5)
        self.image_width_entry = Entry(image_frame)
        self.image_width_entry.grid(row=2, column=1, pady=5, padx=5)

        # Entrada para la altura de la imagen
        ttk.Label(image_frame, text="Height:").grid(row=3, column=0, pady=5, padx=5)
        self.image_height_entry = Entry(image_frame)
        self.image_height_entry.grid(row=3, column=1, pady=5, padx=5)

        # Entrada para el factor de escala
        ttk.Label(image_frame, text="Scale Factor:").grid(row=4, column=0, pady=5, padx=5)
        self.scale_factor_entry = Entry(image_frame)
        self.scale_factor_entry.insert(0, "1.0")
        self.scale_factor_entry.grid(row=4, column=1, pady=5, padx=5)

        # Botón para cambiar la imagen seleccionada
        button = ttk.Button(image_frame, text="Change Image", command=self.change_image)
        button.grid(row=5, column=0, columnspan=2, pady=5, padx=5)  # Extender el botón a dos columnas