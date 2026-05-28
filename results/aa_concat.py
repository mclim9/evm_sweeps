import tkinter as tk
from tkinter import filedialog, messagebox

def select_file(title):
    return filedialog.askopenfilename(title=title)

def save_file():
    return filedialog.asksaveasfilename(
        title="Save combined file as",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )

def main():
    root = tk.Tk()
    root.withdraw()  # Hide main window

    # Select files
    file1_path = select_file("Select the FIRST file")
    if not file1_path:
        messagebox.showerror("Error", "No first file selected.")
        return

    file2_path = select_file("Select the SECOND file")
    if not file2_path:
        messagebox.showerror("Error", "No second file selected.")
        return

    try:
        # Read first file
        with open(file1_path, "r", encoding="utf-8") as f1:
            file1_content = f1.readlines()

        # Read second file
        with open(file2_path, "r", encoding="utf-8") as f2:
            file2_content = f2.readlines()

        # Remove first 4 lines from second file
        file2_trimmed = file2_content[4:]

        # Combine content
        combined_content = file1_content + file2_trimmed

        # Save output
        save_path = save_file()
        if not save_path:
            messagebox.showerror("Error", "No save location selected.")
            return

        with open(save_path, "w", encoding="utf-8") as out:
            out.writelines(combined_content)

        messagebox.showinfo("Success", f"File saved successfully:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    main()
