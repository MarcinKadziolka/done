import func
tm = func.TaskManager("./file.txt")
projects = tm.get_tasks_by_projects()
tags = tm.get_tasks_by_tags()
print("Tasks by projects:")
for k, v in projects.items():
    print(*k)
    print(*v, sep='\n')
    print()

print("Tasks by tags:")
for k, v in tags.items():
    print(*k)
    print(*v, sep='\n')
    print()

