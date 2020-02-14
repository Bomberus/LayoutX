import platform
import urllib.request
import io
import subprocess
import pathlib
import shutil
import hashlib
import time


def dnd_installed():
  try:
    import tkinter
    tk_root = tkinter.Tk()
    version = tk_root.tk.call('package', 'require', 'tkdnd')
    tk_root.tk.call('package', 'forget', 'tkdnd')
    tk_root.destroy()
    tk_root.tk = None
    tk_root = None
    
    return version
  except:
    return False

def dnd_install():
  urls = {
    "Windows" : "https://github.com/petasis/tkdnd/releases/download/tkdnd-release-test-v2.9.2/tkdnd-2.9.2-windows-x64.zip",
    "Linux"   : "https://github.com/petasis/tkdnd/releases/download/tkdnd-release-test-v2.9.2/tkdnd-2.9.2-linux-x64.tgz",
    "Darwin"  : "https://github.com/petasis/tkdnd/releases/download/tkdnd-release-test-v2.9.2/tkdnd-2.9.2-osx-x64.tgz"
  }

  hashes = {
    "Windows" : "d78007d93d8886629554422de2e89f64842ac9994d226eab7732cc4b59d1feea",
    "Linux"   : "f0e956e4b0d62d4c7e88dacde3a9857e7a303dc36406bdd4d33d6459029a2843",
    "Darwin"  : "0c604fb5776371e59f4c641de54ea65f24917b8e539a577484a94d2f66f6e31d"
  }

  print("Starting installation of tkDND")

  os = platform.system()

  if os not in ["Windows", "Linux", "Darwin"]:
    print(f"{os} not supported!")
    exit(0)

  result = None
  archive = None
  url = urls[os]
  download_hash = hashes[os]

  import tkinter
  root = tkinter.Tk()
  tcl_dir = pathlib.Path(root.tk.exprstring('$tcl_library'))

  for p in tcl_dir.glob("tkdnd*"):
    print("tkdnd already installed")
    shutil.rmtree(p)

  print("Download tkDnD libraries from github")

  data =urllib.request.urlopen(url).read()

  data_hash = hashlib.sha256(data).hexdigest()
  
  if (download_hash != data_hash):
    print(f"Got hash: {data_hash}")
    print(f"Expected hash: {download_hash}")
    print("Download incomplete or your security is compromised!!!") 
    exit(1)
  
  print("Extracting tkDnD to tcl extension folder")
  if os ==  "Windows":
    import zipfile
    archive = zipfile.ZipFile(io.BytesIO(data))
    archive.extractall(path=tcl_dir)
  elif os == "Linux" or os == "Darwin":
    import tarfile
    archive = tarfile.open(fileobj=io.BytesIO(data))
    archive.extractall(path=tcl_dir)

  print("tkdnd installed!")

if __name__ == "__main__":
  min_version = "2.9.2"
  version = dnd_installed()
  if not version or version < min_version:
    dnd_install()