import os
import json
from md.backend.data.db import MathDataBase
import glob

def init_mdb(mdb_path,mdb_name,mdb_definition):
    mdb = MathDataBase(mdb_path,mdb_name,mdb_definition)

    if not mdb.already_exists:
        #   Initialize the mdb with data from local
        for ds_filename in glob.glob(os.path.join(mdb_path,"local", "datastructures","*.def")):
            with open(os.path.join(mdb_path,"local", "datastructures",ds_filename)) as def_file:
                datastructure = def_file.read()
                mdb.add_datastructure(datastructure,"Example Datastructure")
                pending=mdb.pending_datastructures()
                mdb.approve_datastructure(pending[0],"Imported from local/datastructures")

    return mdb
