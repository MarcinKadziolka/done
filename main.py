import func

tm = func.TaskManager("./file.txt")


def user_choice():
    print("1. Show all tasks")
    print("2. Show pending tasks")
    print("3. Show done tasks")
    print("4. Show tasks by project")
    print("5. Show tasks by tags")
    print("6. Search tasks")
    user_input = input("Choose an option: ")
    return user_input


while 1:
    user_input = user_choice()
    print()
    print()
    if user_input == "1":
        print(tm)
    elif user_input == "2":
        tm.print_tasks(tm.get_pending_tasks())
    elif user_input == "3":
        tm.print_tasks(tm.get_done_tasks())
    elif user_input == "4":
        pending = tm.get_pending_tasks()
        pending_by_project = tm.get_tasks_by_projects(pending)
        tm.print_tasks_in_dict(pending_by_project)
    elif user_input == "5":
        pending = tm.get_pending_tasks()
        pending_by_tags = tm.get_tasks_by_tags(pending)
        tm.print_tasks_in_dict(pending_by_tags)
    elif user_input == "6":
        search_phrase = input("Enter search phrase: ")
        tm.print_tasks(tm.search(search_phrase))
    print()
    print()
