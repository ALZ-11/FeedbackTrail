from tkinter import *
from tkinter import ttk

root = Tk()

frame = Frame(root)
frame.pack()

scroll = Scrollbar(frame, orient=VERTICAL)
scroll.pack(side=RIGHT, fill=Y)

text = Text(frame, wrap=NONE, yscrollcommand=scroll.set, cursor= "arrow")
text.pack(fill=BOTH)

scroll.config(command=text.yview)

for i in range(21):
    button = Button(text, text=f"button {i}")
    text.window_create("end", window=button)
    text.insert("end", "\n")

root.mainloop()