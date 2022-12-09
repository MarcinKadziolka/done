from functools import wraps
from time import time
from dataclasses import dataclass, field
import datetime
import os
import re


@dataclass
class Task():
    raw_task: str
    description: str = field(default="", init=False)
    tags: set[str] = field(default_factory=set, init=False)
    projects: set[str] = field(default_factory=set, init=False)
    priority: str = field(default="", init=False)
    done: bool = field(default=False, init=False)
    date: datetime.datetime = datetime.datetime.now()

    def __post_init__(self) -> None:
        # Change done to done if first char is x
        if self.raw_task[0] == 'x' and self.raw_task[1] == " ":
            self.done = True
            self.description = self.raw_task[1:]
        else:
            self.description = self.raw_task

        # Get description without words that star with @ or + or (A)
        self.description = re.sub(r"\B@\w+|\B\+\w+|\(\w\)", "",
                                  self.description)

        # Delete trailing whitespace
        self.description = self.description.strip()

        for word in self.raw_task.split():
            first_char = word[0]
            if first_char == "@":
                self.tags.add(word[1:])
            elif first_char == "+":
                self.projects.add(word[1:])
            elif first_char == "(" and len(word) == 3 and word[2] == ")":
                self.priority += word[1]


class TaskParser():
    @staticmethod
    def check_exact_match(to_match, string):
        return re.search(rf"(?:^|\W){to_match}(?:$|\W)", string)


class TaskManager():
    def __init__(self, file_path=None) -> None:
        if not file_path:
            return
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.tasks = []
        self.parser = TaskParser()
        self.read_file()
        # Process tags and projects
        # Dicts?
        self.tags = None
        self.projects = None

    @staticmethod
    def print_tasks(tasks: list[str]):
        print(*tasks, sep="\n")

    def filter_tasks(self, to_match: str) -> list:
        return list(filter(lambda task:
                           self.parser.check_exact_match(to_match, task),
                           self.tasks_raw_task))

    def read_file(self):
        with open(self.file_path, encoding="utf-8") as file:
            for task in file.read().splitlines():
                self.tasks.append(Task(task))

    def write_file(self) -> None:
        raw_tasks = [task.raw_task for task in self.tasks]
        with open(self.file_name, encoding="utf-8", mode="w") as file:
            file.write("\n".join(raw_tasks))
        # os.rename('tmp.txt', f'{self.file_name}')

    def add_task(self, task: Task) -> None:
        # Append task to list
        self.tasks.append(task)

    def delete_task(self, task: Task):
        # Delete task from list
        if task in self.tasks:
            self.tasks.remove(task)
        else:
            print("Cannot delete, task doesn't exist")

    def edit_task(self, old_task: Task, new_task: Task) -> None:
        # Check if the old task is in the list
        if old_task in self.tasks:
            # If it's in the list, find its index
            index = self.tasks.index(old_task)

            # Replace the old task with the new task
            self.tasks[index] = new_task
        else:
            print("Cannot edit, task doesn't exist")

    def __str__(self) -> str:
        raw_tasks = [task.raw_task for task in self.tasks]
        return "\n".join(raw_tasks)


def timing(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print(f"{f.__name__=}, {args=}, {kwargs=} took: {te - ts:.3f} seconds")
        return result

    return wrap
