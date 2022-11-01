import zipfile
import argparse
import os

class Terminal:
    def __init__(self, file_name):
        self.file_name = file_name
        self.current_path = "/"
        self.home_path = os.getcwd()
        self.home_path = os.path.join(self.home_path, os.path.normpath(self.file_name))
        self.directory = zipfile.ZipFile(self.file_name, 'r')

    def ls(self, new_path=""):
        path = self.current_path
        if new_path != "":
            path = new_path
        files_list = self.get_zip_listdir(path)
        for file in files_list: print(file)

    def get_zip_listdir(self, path):
        file_names = self.directory.namelist()
        if not path.endswith("/"):
            path += "/"
        if path == "/" or path == "./":
            path = ""
        if path.startswith("/") or path.startswith("./"):
            path = path[1:]
        result = []
        for file_name in file_names:
            if file_name.startswith(path):
                file_name = file_name.replace(path, "")
                if len(file_name.split("/")) == 1 or (len(file_name.split("/")) == 2 and file_name.endswith("/")):
                    if file_name != "": result.append(file_name)
        return result

    def is_file(self, path):
        if path.startswith("/"):
            path = path[1:]
        p = "/".join(path.split("/")[:-1])
        file = path.split("/")[-1]
        file_names = self.directory.namelist()
        if p == "/":
            p = ""
        f = True
        for file_name in file_names:
            if file_name.startswith(path):
                file_name_s = file_name.replace(path, "")
                if file_name_s != "" and file in file_name and file_name_s[-1] == "/":
                    f = False
                    break
        return f

    def is_exist(self, path):
        file_names = self.directory.namelist()
        if not path.endswith("/") and not(self.is_file(path)):
            path += "/"
        if path.startswith("/"):
            path = path[1:]
        f = False
        for file_name in file_names:
            if file_name == path:
                f = True
                break
        return f

    def cd(self, new_path):
        p = self.current_path
        if new_path == "~": p = "/"
        else:
            if new_path == "-": new_path = ".."
            if new_path.startswith("/") and len(new_path.split("/")) > 1 and new_path != "/":
                new_path = new_path[1:]
            p = os.path.normpath(os.path.join(self.current_path, new_path))
            p = p.replace("\\", "/")
            if not(self.is_exist(p)) and p != "/":
                print(f"No such directory: {new_path}")
                p = self.current_path
            elif self.is_file(p):
                print(f"can't cd to {new_path}")
                p = self.current_path
        return p

    def cat(self, path):
        path = os.path.normpath(os.path.join(self.current_path, path))
        path = path.replace("\\", "/")
        if not(self.is_exist(path)):
            print(f"No such file: {path}")
        elif not(self.is_file(path)):
            print(f"File is not a file: {path}")
        else:
            if path.startswith("/"): path = path[1:]
            with self.directory.open(path) as file:
                lines = [x.decode('utf8').strip() for x in file.readlines()]
                for line in lines:
                    print(line)

    def pwd(self):
        if self.current_path == "/": print(self.current_path)
        else: print(self.current_path + "/")

    def input_command(self):
        p = self.current_path
        if p == ".": p = os.sep
        command = input(f"{p}>")
        return command
        
    def run(self):
        command = ["", ""]
        while command[0] != "exit":
            command = self.input_command().split()
            if command[0] == "ls":
                if len(command) > 1: self.ls(command[1])
                else: self.ls()
            elif command[0] == "cd":
                self.current_path = self.cd(command[1])
            elif command[0] == "cat":
                self.cat(command[1])
            elif command[0] == "pwd":
                self.pwd()
            elif command[0] == "exit":
                break
            else:
                print(f"Command: {command[0]} not found")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    file_name = args.file

    terminal = Terminal(file_name)
    terminal.run()

if __name__ == "__main__":
    main()