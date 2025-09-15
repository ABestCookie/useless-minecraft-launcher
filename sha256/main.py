import hashlib
from tkinter import filedialog as dialog
from tkinter import messagebox as msg
def check_hash():
    
    h = hashlib.new('sha256')
    filename=dialog.askopenfilename(title="choose a file")
    BufferSize=65536
    if not filename:
        msg.showerror("hash checker", "You don't choose any file")
        return None
    else:
        with open(filename, "rb") as f:
            while True:
                data=f.read(BufferSize)
                if not data:
                    break
                h.update(data)
            return h.hexdigest()
if __name__=="__main__":
    print(check_hash())