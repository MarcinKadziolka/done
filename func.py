from functools import wraps
from time import time
from dataclasses import dataclass
import datetime
import os
import re
from collections import namedtuple

task_tuple = namedtuple('task_tuple', ['description', 'tags',
                                       'projects', 'priority'])


class TaskParser():

    @staticmethod
    def parse_priority(task: str):
        return re.search(r"\((\w{1})\)", task).group(1)

    @staticmethod
    def parse_tags(task: str):
        return re.findall(r"@(\w+)", task)

    @staticmethod
    def parse_projects(task: str):
        return re.findall(r"\+(\w+)", task)

    # @staticmethod
    # def parse_description(task: str):
    #     return re.findall(r"\+(\w+)", task)

    @staticmethod
    def parse_task(task: str):
        tags = set()
        projects = set()
        priority = ""
        description = ""

        for word in task:
            first_char = word[0]
            if first_char == "@":
                tags.add(word[1:])
            elif first_char == "+":
                projects.add(word[1:])
            elif first_char == "(" and len(word) == 3 and word[2] == ")":
                priority += word[1]
            else:
                description += word

        return task_tuple(description=description, tags=tags,
                          projects=projects, priority=priority)

        # return description, tags, projects, priority


class TaskManager():
    def __init__(self, file_path=None) -> None:
        if not file_path:
            return
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.task_list_raw = []
        self.task_list_obj = []
        self.read_file()
        self.parser = TaskParser()
        # Process tags and projects
        # Dicts?
        self.tags = None
        self.projects = None

    @staticmethod
    def check_exact_match(to_match, string):
        return re.search(rf"(?:^|\W){to_match}(?:$|\W)", string)

    @staticmethod
    def print_tasks(task_list: list[str]):
        print(*task_list, sep="\n")

    def filter_tasks(self, to_match: str) -> list:
        return list(filter(lambda task: self.check_exact_match(to_match, task),
                           self.task_list))

    def read_file(self):
        with open(self.file_path, encoding="utf-8") as file:
            self.task_list = file.read().splitlines()

    def add_task(self, task: str) -> None:
        # Append task to list
        if task in self.task_list:
            print("Task already exists!")
            return False
        self.task_list.append(task)
        return True

    def delete_task(self, task: str) -> bool:
        # Delete task from list
        try:
            self.task_list.remove(task)
            return True
        except ValueError as err:
            print("Can't delete, task doesn't exist.")
            print(f"Error message: {err=}")
            return False

    def edit_task(self, task: str, new_task: str) -> bool:
        # Edit task from list
        try:
            idx = self.task_list.index(task)
        except ValueError:
            print("Can't edit, task doesn't exist.")
            return False
        self.task_list[idx] = new_task
        return True

    def write_file(self) -> None:
        """
        Writes local changes to temporary files
        and then renames it to it's original name
        """
        with open("tmp.txt", encoding="utf-8", mode="w") as file:
            file.write("\n".join(self.task_list))
        os.rename('tmp.txt', f'{self.file_name}')

    def __str__(self) -> str:
        return "\n".join(self.task_list)


@dataclass
class Task():
    desc: str
    tags: list[str]
    projects: list[str]
    priority: str
    date: datetime.datetime = datetime.datetime.now()


def timing(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print(f"{f.__name__=}, {args=}, {kwargs=} took: {te - ts:.3f} seconds")
        return result

    return wrap
