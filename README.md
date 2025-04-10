# WSI Anon

## Description

A C library to anonymize Whole Slide Images in proprietary file formats. The library removes all sensitive data within the file structure including the filename itself, associated image data (as label and macro image) and metadata that is related to the slide acquisition and/or tissue. Associated image data is overwritten with either blank or white image data and subsequently unlinked from the file structure if possible. Unlinking can be disabled by a CLI / method parameter (for later pseudonymization). The related metadata is always removed from the file, usually containing identifiers or acquisition-related information as serial numbers, date and time, users, etc. A wrapper for JavaScript (WebAssembly) and python is provided.

Currently supported formats:

| Vendor | Scanner types (tested) | File extension | Comment |
|---|---|---|---|
| Leica Aperio | AT20, GT450 | `*.svs` `*.tif` | - |
| KFBIO | KF-PRO-400 | `*.svs` | - |
| Motic | Pro6 | `*.svs` | - |
| Hamamatsu | NanoZoomer XR, XT2, S210, S360 | `*.ndpi` | - |
| 3DHistech Mirax | Pannoramic P150, P250, P1000 | `*.mrxs` | - |
| Roche Ventana | VS200, iScan Coreo, DP 600 | `*.bif` `*.tif`| - |
| Philips | IntelliSite Ultra Fast Scanner | `*.isyntax` `*.tiff`  | - |

**The library is implemented and tested under Linux (Ubuntu 20.04) and currently only experimental under Windows.**

> **As of version 0.4.25: experimental support for MacOS has been added.**
Test on MacOS Sonoma 14.1.

## Publications

The design and implementation is also described in a technical note in [Anonymization of Whole Slide Images in Histopathology for Research and Education](https://journals.sagepub.com/doi/10.1177/20552076231171475)

## Requirements

* install `build-essential`
* install `MinGW-w64`, e.g. from [Winlibs](https://winlibs.com/) (only required when running under windows)

WebAssembly:
* install `emscripten`, e.g. from [Emscripten](https://emscripten.org/docs/getting_started/downloads.html) (at least v. 1.39.15, only required for Web Assembly target)

Development (Testing and code checks):
* install `clang-format-10`
* install `libcunit1-dev`
* install `docker` and `docker-compose`

## Build

### Native Target

#### Under Linux

To build the shared library with command line interface simply run

```bash
make
```

and run with `bin/wsi-anon.out /path/to/wsi.svs` afterwards.

This will build the object files and subsequently a static and a shared library. Also the console application will be build as .out file. These files are stored under `bin/`. Note that this will use the default Makefile.

To build the console application in debug mode type

```bash
make console-app-debug
```

and run with `gdb -args bin/wsi-anon-dbg.out /path/to/wsi.svs` afterwards.

#### Under MacOS

On MacOS, the same instructions for Linux can ne followed, just make sure you have a working C toolchain. E.g. gcc, clang, etc.
This can be achieved by installing the Apple Command Line Tools with `xcode-select --install`.

To build the shared library with command line interface simply run.

```bash
make
```

And run with `bin/wsi-anon.out /path/to/wsi.svs` afterwards.

#### Under Windows

To build an executable file under windows make sure `MinGW-w64` is installed and run

```bash
# if not yet done, set path for mingw after installation, e.g.:
set PATH=C:\mingw\bin;%PATH%

# compile
mingw32-make -f MakefileWin.mk
```

and run with `exe\wsi-anon.exe \path\to\wsi.svs` afterwards.

### Web Assembly Target

The library also has a Web Assembly (WASM) target in order to enable client-side anonymization of supported file formats from the browser. In this case the file I/O system calls are redirected to JavaScript and evaluated there for chunk reading and writing. To produce the ES6 module `./bin/wsi-anon.js` with embedded, base64 encoded WASM binary that facilitates usage in arbitrary web applications, run the following command:

#### Under Linux

```bash
make wasm
```

## Run

### Console Application

Check for slide vendor and view all found metadata in WSI:

```bash
./wsi-anon.out "/path/to/wsi.svs" -c
```

Anonymize slide:

```bash
./wsi-anon.out "/path/to/wsi.svs" [-OPTIONS]
```

Type `-h` or `--help` for help. Further CLI parameters are:

* `-n "label-name"`: File will be renamed to the given label name
* `-u` : Disables the unlinking of associated image data (default: associated image will be unlinked)
* `-i` : Enable in-place anonymization (default: copy of the file will be created)



### Python Wrapper Usage (EXPERIMENTAL)

#### Under Ubuntu

The Python Wrapper makes use of the shared library `libwsianon.so` that needs to be created prior to running the script. This is simply done by building the Native Target under Linux as described above. In order to locate and load the library (indendepent of the current working directory), the file needs to be copied to "/usr/lib/". This can simply be done by running the following command:

```bash
make install
```

If permission is denied run this command again with `sudo` at the beginning.

#### Under Windows

Analogous to Ubuntu, Windows will need the corresponding `libwsianon.dll`. This needs to be placed in the `C:\Windows\System32` folder, that is automatically done when building the Native Target under Windows.

If permission is denied run the command again after opening the command prompt/PowerShell as an administrator.

```
mingw32-make -f MakefileWin_local.mk
```
Running this local file avoids permission requirement. You should copy `.dll` file located in `exe` folder to `wrapper/python` before building the executable tool.

## Executable GUI
- First obtain the `libwsianon.dll` library following Windows instruction above. 
- Compile the python file into Windows executable file:
```
pyinstaller --onefile --windowed --name WSI_Anonymizer wrapper/python/main_gui.py
```