from tkinter import *
width = 640
height = 440
def main_app():
    window=Tk()
    window.title("Loading")
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2) #window致中
    window.geometry(geometry)
    window.resizable(False, False)
    canvas=Canvas(window, width=width, height=height)
    canvas.pack()
    img=PhotoImage(file="art/loading.gif")
    canvas.create_image(320, 220, image=img)
    window.mainloop()


if __name__ == "__main__":
    
    main_app()

