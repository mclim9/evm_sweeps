import tkinter as tk
from tkinter import filedialog, messagebox


def select_file():
    root = tk.Tk()
    root.withdraw()  # Hides Tkinter window
    file_in = filedialog.askopenfilename(title="Select a file", filetypes=[("Text files", "*.txt")])
    return file_in

def yes_no():
    window = tk.Tk()
    window.withdraw() # Hides Tkinter window
    result = messagebox.askyesno("Confirmation", "Do you want to proceed Paul?")
    if result:
        print(f"User clicked {result}")
    else:
        print("User clicked No")
    # window.mainloop()

if __name__ == '__main__':
    # print(select_file())
    yes_no()
    print('done')
