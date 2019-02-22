from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from sqlalchemy import create_engine, MetaData
from pathlib import Path
# connect to database
"""
host = Path.cwd().parent / "db" / "nfe.db"
engine = create_engine(f"sqlite:///{host}")
metadata = MetaData(engine)
conn = engine.connect()
"""
# https://stackoverflow.com/a/33426759
gauth = GoogleAuth()
# Try to load saved client credentials
credentials = Path.cwd() / "mycreds.txt"
gauth.LoadCredentialsFile(credentials)
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile(credentials)
drive = GoogleDrive(gauth)

folder = "1s8HXOk0B0_WfCLW_muaIj2bS-hcifWTf"
file_list = drive.ListFile({"q": f"'{folder}' in parents and trashed=false"}).GetList()

already_downloaded = [f.name for f in Path("../data/").rglob("*.txt")]
for f in file_list:
    id_file = f['id']
    create_file = drive.CreateFile({"id": id_file})
    if create_file['title'] not in already_downloaded:
        print(f"Iniciando download do arquivo {create_file['title']}.\n")
        create_file.GetContentFile(Path.cwd().parent / f"data/nfe-url/{create_file['title']}")
