import os
import pathlib
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

lock = threading.Lock()

### WSI ANON ###
import ctypes
import os
import threading
import platform

import ctypes
from enum import Enum

class Vendor(Enum):
    APERIO = 0
    HAMAMATSU = 1
    MIRAX = 2
    VENTANA = 3
    PHILIPS_ISYNTAX = 4
    PHILIPS_TIFF = 5
    UNKNOWN = 6
    INVALID = 7

class MetadataAttribute(ctypes.Structure):
    _fields_ = [("key", ctypes.c_char_p),
                ("value", ctypes.c_char_p)]

class Metadata(ctypes.Structure):
    _fields_ = [("metadataAttributes", ctypes.POINTER(MetadataAttribute)),
                ("length", ctypes.c_size_t)]

class WSIData(ctypes.Structure):
    _fields_ = [("format", ctypes.c_int8),
                ("filename", ctypes.c_char_p),
                #("label", ctypes.POINTER(AssociatedImageData)),
                #("macro", ctypes.POINTER(AssociatedImageData)),
                ("metadata", ctypes.POINTER(Metadata))]
    
lock = threading.Lock()

def _load_library():
    '''
    loads library depending on operating system. This is currently only implemented only Windows and Linux
    '''
    if platform.system() == 'Linux':
        try:
            return ctypes.cdll.LoadLibrary('libwsianon.so')
        except FileNotFoundError:
            raise ModuleNotFoundError(
                "Could not locate libwsianon.so. Please make sure that the shared library is created and placed under usr/lib/ by running make install."
            )
    elif platform.system() == 'Darwin':
        try:
            return ctypes.cdll.LoadLibrary('libwsianon.dylib')
        except FileNotFoundError:
            raise ModuleNotFoundError(
                "Could not locate libwsianon.so. Please make sure that the shared library is created and placed under usr/lib/ by running make install."
            )
    elif platform.system() == 'Windows':
        try:
            return ctypes.WinDLL("libwsianon.dll")
        except FileNotFoundError:
            raise ModuleNotFoundError(
                "Could not locate libwsianon.dll. Please make sure that the DLL is created and placed under C:\\Windows\\Systems32."
            )
    else:
        raise ModuleNotFoundError(
                "Could not locate shared library or DLL. Please make sure you are running under Linux or Windows."
            )

_wsi_anonymizer = _load_library()

def get_wsi_data(filename):
    '''
    gets all necessary WSI data from slide
    '''
    global _wsi_anonymizer
    _wsi_anonymizer.get_wsi_data.argtypes = [ctypes.c_char_p]
    _wsi_anonymizer.get_wsi_data.restype = ctypes.c_void_p

    c_filename = filename.encode('utf-8')

    wsi_data = WSIData.from_address(_wsi_anonymizer.get_wsi_data((ctypes.c_char_p(c_filename))))
    return wsi_data

def anonymize_wsi(filename, new_label_name, keep_macro_image=False, disable_unlinking=False, do_inplace=False):
    '''
    performs anonymization on slide
    '''
    global _wsi_anonymizer
    _wsi_anonymizer.anonymize_wsi.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
    _wsi_anonymizer.anonymize_wsi.restype = ctypes.c_void_p

    filename = str(filename).replace(" ", "\\ ") # escape whitespaces if exist
    c_filename = filename.encode('utf-8')
    c_new_label_name = new_label_name.encode('utf-8')

    result = -1
    with lock:
        result = _wsi_anonymizer.anonymize_wsi(
            c_filename, 
            c_new_label_name,
            keep_macro_image, 
            disable_unlinking, 
            do_inplace
        )

    return result
#######

def cleanup():
    temporary_files = []
    def add_filename(filename):
        temporary_files.append(filename)

    yield add_filename

    for filename in set(temporary_files):
        remove_file(filename=filename)

def remove_file(filename):
    with lock:
        if filename.endswith(".mrxs"):
            mrxs_path = filename[:len(filename)-5]
            shutil.rmtree(mrxs_path)
        os.remove(filename)

def anonymize_wsi_files(wsi_filepath, original_filename, new_anonymized_name, file_extension):
    result_filename = pathlib.Path(wsi_filepath).joinpath(f"{new_anonymized_name}.{file_extension}")
    if result_filename.exists():
        remove_file(str(result_filename.absolute()))

    wsi_filename = str(pathlib.Path(wsi_filepath).joinpath(f"{original_filename}.{file_extension}").absolute())
    result = anonymize_wsi(wsi_filename, new_anonymized_name)
    
    return result

class WSIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WSI Anonymizer")

        # Input fields
        self.wsi_filepath_label = tk.Label(root, text="WSI File Path:")
        self.wsi_filepath_label.grid(row=0, column=0, padx=10, pady=10)
        self.wsi_filepath_entry = tk.Entry(root, width=50)
        self.wsi_filepath_entry.grid(row=0, column=1, padx=10, pady=10)
        self.wsi_filepath_button = tk.Button(root, text="Browse", command=self.browse_wsi_filepath)
        self.wsi_filepath_button.grid(row=0, column=2, padx=10, pady=10)

        self.original_filename_label = tk.Label(root, text="Original Filename:")
        self.original_filename_label.grid(row=1, column=0, padx=10, pady=10)
        self.original_filename_entry = tk.Entry(root, width=50)
        self.original_filename_entry.grid(row=1, column=1, padx=10, pady=10)

        self.new_anonymized_name_label = tk.Label(root, text="New Anonymized Name:")
        self.new_anonymized_name_label.grid(row=2, column=0, padx=10, pady=10)
        self.new_anonymized_name_entry = tk.Entry(root, width=50)
        self.new_anonymized_name_entry.grid(row=2, column=1, padx=10, pady=10)

        self.file_extension_label = tk.Label(root, text="File Extension:")
        self.file_extension_label.grid(row=3, column=0, padx=10, pady=10)
        self.file_extension_entry = tk.Entry(root, width=50)
        self.file_extension_entry.grid(row=3, column=1, padx=10, pady=10)

        # Run button
        self.run_button = tk.Button(root, text="Run", command=self.run_anonymization)
        self.run_button.grid(row=4, column=1, padx=10, pady=20)

    def browse_wsi_filepath(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.wsi_filepath_entry.delete(0, tk.END)
            self.wsi_filepath_entry.insert(0, folder_path)

    def run_anonymization(self):
        wsi_filepath = self.wsi_filepath_entry.get()
        original_filename = self.original_filename_entry.get()
        new_anonymized_name = self.new_anonymized_name_entry.get()
        file_extension = self.file_extension_entry.get()

        if not all([wsi_filepath, original_filename, new_anonymized_name, file_extension]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            result = anonymize_wsi_files(wsi_filepath, original_filename, new_anonymized_name, file_extension)
            messagebox.showinfo("Success", f"Anonymization completed successfully!\nResult: {result}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WSIGUI(root)
    root.mainloop()