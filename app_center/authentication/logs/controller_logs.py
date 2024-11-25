from app_center import ERRORLOGDIR
from datetime import datetime
import os


def catat_log_error(nama_fungsi, e):
  """
  Fungsi untuk mencatat error dan dijadikan kedalam file logs.
  """
  tanggal = datetime.now()
  log_file_name = f"{tanggal.date()}.txt"
  log_file_path = os.path.join(ERRORLOGDIR, log_file_name)
  exists = os.path.exists(log_file_path)
  if not exists:
    mode = 'w+'
    filenames = os.listdir(ERRORLOGDIR)
    filenames.remove('.gitignore')
    if len(filenames) >= 30:
      filenames.sort(reverse=True)
      remove_log_name = filenames.pop()
      remove_log_file = os.path.join(ERRORLOGDIR, remove_log_name)
      if os.path.exists(remove_log_file):
        os.remove(remove_log_file)
    with open(log_file_path, mode) as f:
      f.write(f"{tanggal.strftime('%d-%B-%Y %H:%M:%S')} - {nama_fungsi} - {e}\n")
  else:
    mode = 'a'
    with open(log_file_path, mode) as f:
      f.write(f"{tanggal.strftime('%d-%B-%Y %H:%M:%S')} - {nama_fungsi} - {e}\n")