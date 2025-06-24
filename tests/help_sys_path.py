import sys

def sys_path_print():
    # print(sys.path)  # Print the directories in sys.path
    for i, path in enumerate(sys.path):
        print(f"{i}: {path}")
    print("")

def sys_path_add():
    sys.path.append("/path/to/new/directory")       # append dir to sys.path
    sys.path.insert(0, "/path/to/new/directory")    # insert dir @ beginning of sys.path

def sys_path_rem():
    directory = 'dfd'
    sys.path.remove(directory)

if __name__ == '__main__':
    sys_path_print()
