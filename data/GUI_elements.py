import tkinter as tk

def select_list(options, title="Select a List"):
    global selected_options
    root = tk.Tk()
    root.title(title)
    root.geometry('100x100')
    listbox = tk.Listbox(root, selectmode=tk.EXTENDED)          # Create a Listbox widget
    for option in options:
        listbox.insert(tk.END, option)                          # Fill list
    listbox.pack(padx=10, pady=10)

    def confirm_selection():                                    # Create button to confirm selection
        global selected_options
        selected_indices = listbox.curselection()
        if selected_indices:
            selected_options = [listbox.get(index) for index in selected_indices]
        root.destroy()
        return selected_options

    confirm_button = tk.Button(root, text="Confirm", command=confirm_selection)
    confirm_button.pack(pady=10)

    root.mainloop()
    return selected_options


if __name__ == '__main__':
    asdf = select_list(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])
    print(f'asdfasdf {selected_options}')
