import os
import zlib
import string

def get_text(filename):
    # чтение файла и восстановаление байтов
    with open(filename, 'rb') as file:
        text = file.read()
    return zlib.decompress(text)

def parse_commit(text, file_name):
    # парсинг текста в коммите
    # commit [size]\0tree [tree_name]\nparent [parent_name]\nauthor [author_name] <[author_email]> [time] [time]\ncommiter [commiter_name] <[commiter_email]> [time] [time]\n\n[commit_text]\n
    content_arr = text.split(b'\n')
    commit = {}
    commit["type"] = "commit"
    commit["name"] = file_name
    commit["parents"] = []
    for i in range(len(content_arr) - 3):
        line_arr = content_arr[i].split()
        if line_arr[0].decode("utf-8") == "commit":
            commit["tree"] = line_arr[-1].decode("utf-8")
        elif line_arr[0].decode("utf-8") == "parent":
            commit["parents"].append(line_arr[1].decode("utf-8"))
        elif line_arr[0].decode("utf-8") == "author":
            commit["authorName"] = line_arr[1].decode("utf-8")
            commit["authorEmail"] = line_arr[2].decode("utf-8")
        elif line_arr[0].decode("utf-8") == "committer":
            commit["committerName"] = line_arr[1].decode("utf-8")
            commit["committerEmail"] = line_arr[2].decode("utf-8")
            break
    # поиск текста коммита (в некоторых случаях расхождения с форматом)
    for i in range(len(content_arr) - 1, 0, -1):
        if len(content_arr[i]) > 0:
            commit["commitText"] = content_arr[i].decode("utf-8")
            break
    return commit

def parse_tree(text, file_name, project_path):
    # парсинг текста в tree
    # tree [size]\0[mode] [name]\0[SHA-1 in binary (20 bytes)][mode] [name]\0[SHA-1 in binary (20 bytes)]
    tree = {}
    tree["type"] = "tree"
    tree["name"] = file_name
    files = []
    zero_byte = text.find(b'\x00')
    type_size = text[0:zero_byte]
    text = text[zero_byte+1:]

    files = []

    while len(text):
        zero_byte = text.find(b'\x00')
        name_line = text[0:zero_byte].decode("utf-8").split()
        text = text[zero_byte+1:]
        file_path = text[0:20]
        files.append({
            "type": check_git_type(file_path.hex(), project_path),
            "mode": name_line[0],
            "name": name_line[1],
            "filePath": file_path.hex()
        })
        text = text[20:]
        tree["files"] = files
    return tree

def parse_blob(text, file_name):
    # парсинг текста в blob
    # blob [size]\0[text]
    blob = {}
    blob["type"] = "blob"
    blob["name"] = file_name
    space_ind = text.find(b' ')
    zero_byte = text.find(b'\x00')
    blob["size"] =text[space_ind+1:zero_byte].decode("utf-8")
    blob["content"] = text[zero_byte + 1:]
    return blob

def get_git_objects(project_path):
    # перебор всех объектов и разделение на коммиты, tree, blob
    git_objects_path = ".\.git\objects"
    objects_path = os.path.join(os.path.normpath(project_path), os.path.normpath(git_objects_path))
    objects_dir = os.walk(objects_path)

    commits = []
    trees = []
    blobs = []

    for object in objects_dir:
        path_arr = os.path.split(object[0])
        if len(path_arr[-1]) == 2:
            for i in range(len(object[2])):
                file_path = os.path.join(object[0], object[2][i])
                file_name = path_arr[-1] + object[2][i]
                text = get_text(file_path)
                type = text.split()[0].decode("utf-8")
                if type == "commit":
                    commit = parse_commit(text, file_name)
                    commits.append(commit)
                elif type == "tree":
                    tree = parse_tree(text, file_name, project_path)
                    trees.append(tree)
                elif type == "blob":
                    blob = parse_blob(text, file_name)
                    blobs.append(blob)
    return commits, trees, blobs

def check_git_type(file_path, project_path):
    # получение типа файла (commit, tree, blob)
    git_objects_path = ".\.git\objects"
    project_path = os.path.normpath(project_path)
    git_objects_path = os.path.normpath(git_objects_path)
    objects_path = os.path.join(project_path, git_objects_path, file_path[0:2], file_path[2:])
    return get_text(objects_path).split()[0].decode("utf-8")

def create_nodes(commits, trees, blobs):
    # организация вершин граФа
    arr = commits + trees + blobs
    nodes = []
    ascii_uppercase = list(string.ascii_uppercase)
    for i in range(len(arr)):
        node = {}
        name = ""
        # составление имени вершины
        if i >= len(ascii_uppercase):
            name += ascii_uppercase[(i%len(ascii_uppercase))-1] + str(i)
        else: name = ascii_uppercase[i]

        node["id"] = arr[i]["name"]
        node["name"] = name
        node["type"] = arr[i]["type"]
        node["parents"] = []
        if arr[i]["type"] == "commit":
            node["parents"] = arr[i]["parents"]
            node["text"] = "Commit: " + arr[i]["commitText"]
        elif arr[i]["type"] == "tree":
            tree_name = ""
            # нахождение верхних элементов
            for commit in commits:
                if commit["tree"] == arr[i]["name"]:
                    node["parents"].append(commit["name"])
            for tree in trees:
                for file in tree["files"]:
                    if file["filePath"] == arr[i]["name"]:
                        node["parents"].append(tree["name"])
                        tree_name = file["name"]
                        break
            # составление текста дерева (название папки)
            if tree_name != "":
                node["text"] = f"tree: {tree_name}"
            else: node["text"] = "tree"
        elif arr[i]["type"] == "blob":
            fileName = ""
            # нахождение верхних элементов
            for tree in trees:
                for file in tree["files"]:
                    if file["filePath"] == arr[i]["name"]:
                        node["parents"].append(tree["name"])
                        fileName = file["name"]
                        break
            node["text"] = fileName
        nodes.append(node)
    return nodes

def create_graph(nodes):
    # составление графа
    # digraph Git { A[label='sometext'] A -> B }
    graph = "digraph Git {\n"

    # объявление вершин и их заголовки
    for node in nodes:
        color = ""
        shape = ""
        style = "rounded,filled"
        if node["type"] == "commit": 
            color = "#2192FF"
            shape = "cylinder"
        elif node["type"] == "tree": 
            color = "#38E54D"
            shape = "folder"
        else: 
            color = "#9CFF2E"
            shape = "component"
        graph += f'  {node["name"]}[label="{node["text"]}", color="{color}", shape={shape}, style="{style}"]\n'

    # установление связей
    for node in nodes:
        parents = []
        # поиск главного модуля
        for i in range(len(node["parents"])):
            for n in nodes:
                if n["id"] == node["parents"][i]:
                    parents.append(n["name"])
        for i in range(len(parents)):
            graph += f'  {parents[i]} -> {node["name"]}\n'
    graph += "}"
    return graph

if __name__ == "__main__":
    project_path = os.getcwd()

    commits, trees, blobs = get_git_objects(project_path)
    nodes = create_nodes(commits, trees, blobs)
    graph = create_graph(nodes)

    print(graph)
