from os import wait
import func
tm = func.TaskManager("./file.txt")
projects = tm.get_tasks_by_projects()
tags, done = tm.get_tasks_by_tags()
tm.print_tasks_by_tags(tags)
tm.print_tasks(done)
# tm.print_tasks_by_projects(projects)
print()
result = tm.search("@home")
print("Search fraze: @home")
tm.print_tasks(result)

