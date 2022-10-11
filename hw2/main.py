import requests
import argparse
import string

def get_requires_dist(module_name):
    # запрос на сайт для получения зависимостей
    base_url = f"https://pypi.org/pypi/{module_name}/json"

    r = requests.get(base_url)
    data = r.json()

    if data.get("message") and data["message"] == "Not Found":
        print("Модуль не найден")
        return []

    requires_dist = data["info"]["requires_dist"]

    # выделение названий зависимостей
    dependencies = [module_name]

    if requires_dist:
        for dep in requires_dist:
            dep = dep.split(" ")[0]
            dependencies.append(dep)
    
    return dependencies

def create_nodes(dependencies, module_name):
    # организация вершин графа
    ascii_uppercase = list(string.ascii_uppercase)
    nodes = []

    for i in range(len(dependencies)):
        name = ""
        # если превышен лимит букв, то прибавляется число
        if i > len(ascii_uppercase):
            name += ascii_uppercase[(i%len(ascii_uppercase))-1] + str(i%len(ascii_uppercase))
        name = ascii_uppercase[i]

        # [название вершины, название зависимости, название головного модуля]
        nodes.append([name, dependencies[i], module_name])
    return nodes

def create_graph(nodes):
    # digraph Module { A[label='django'] A -> B }
    graph = "digraph Module {\n"

    # объявление вершин и их заголовки
    for node in nodes:
        graph += f'  {node[0]}[label="{node[1]}"]\n'

    # установление связей
    for node in nodes:
        module = []
        # исключение первого элемента
        if node[1] != node[2]:
            # поиск главного модуля
            for i in range(len(nodes)):
                if nodes[i][1] == node[2]:
                    module = nodes[i]
            graph += f"  {module[0]} -> {node[0]}\n"
    graph += "}"
    return graph

if __name__ == "__main__":
    # получение названия модуля из командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument("module")
    args = parser.parse_args()
    module_name = args.module

    dependencies = get_requires_dist(module_name)
    nodes = create_nodes(dependencies, module_name)
    graph = create_graph(nodes)

    print(graph)
