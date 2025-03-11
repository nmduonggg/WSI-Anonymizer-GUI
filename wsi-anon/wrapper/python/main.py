import os
import pathlib
import shutil
import threading
import time
import openslide

from wsianon import get_wsi_data, anonymize_wsi

lock = threading.Lock()

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

def test_anonymize_large_files_openslide(cleanup, wsi_filepath, original_filename, new_anonyimized_name, file_extension):
    result_filename = pathlib.Path(wsi_filepath).joinpath(f"{new_anonyimized_name}.{file_extension}")
    if result_filename.exists():
        remove_file(str(result_filename.absolute()))

    wsi_filename = str(pathlib.Path(wsi_filepath).joinpath(f"{original_filename}.{file_extension}").absolute())
    result = anonymize_wsi(wsi_filename, new_anonyimized_name)
    
    print(wsi_filename, result)
    cleanup(str(result_filename.absolute()))
    
    
if __name__=="__main__":
    wsi_filepath = "../pathcore-download-20240728-032030"
    original_filename = "slide-2024-04-04T11-40-39-R3-S2"
    file_extension = "mrxs"
    new_anonyimized_name = "_anonymized"
    
    test_anonymize_large_files_openslide(cleanup, wsi_filepath, original_filename, new_anonyimized_name, file_extension)