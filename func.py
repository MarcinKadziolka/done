from functools import wraps
from time import time
from dataclasses import dataclass, field
import datetime
import os
import re
import itertools


@dataclass
class Task:
    raw_text: str
    description: str = field(default="", init=False)
    tags: list[str] = field(default_factory=lambda: [], init=False)
    projects: list[str] = field(default_factory=lambda: [], init=False)
    priority: str = field(default="", init=False)
    done: bool = field(default=False, init=False)
    date: datetime.datetime = datetime.datetime.now()

    def __post_init__(self) -> None:
        # Change done to done if first char is x
        if self.raw_text[0] == "x" and self.raw_text[1] == " ":
            self.done = True
            self.description = self.raw_text[1:]
        else:
            self.description = self.raw_text

        # Get description without words that star with @ or + or (A)
        self.description = re.sub(r"\B@\w+|\B\+\w+|\(\w\)", "", self.description)

        # Delete trailing whitespace
        self.description = self.description.strip()

        for word in self.raw_text.split():
            first_char = word[0]
            if first_char == "@":
                self.tags.append(word)
            elif first_char == "+":
                self.projects.append(word)
            elif first_char == "(" and len(word) == 3 and word[2] == ")":
                self.priority += word


class TaskParser:
    @staticmethod
    def check_exact_match(to_match, string):
        return re.search(rf"(?:^|\W){to_match}(?:$|\W)", string)


class TaskManager:
    def __init__(self, file_path=None) -> None:
        if not file_path:
            return
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.tasks = []
        self.read_file()  # Reads tasks to tasks list
        self.parser = TaskParser()

    def get_done_tasks(self):
        return [task for task in self.tasks if task.done]

    def get_pending_tasks(self):
        return [task for task in self.tasks if not task.done]

    # Printing methods
    @staticmethod
    def print_tasks(tasks: list) -> None:
        for task in tasks:
            print(task.raw_text)

    @staticmethod
    def print_tasks_in_dict(tasks_dict: dict) -> None:
        for k, v in tasks_dict.items():
            print(*k)
            for task in v:
                print(task.raw_text)
            print()

    def filter_tasks(self, to_match: str) -> list:
        return list(
            filter(
                lambda task: self.parser.check_exact_match(to_match, task),
                self.tasks_raw_task,
            )
        )

    def read_file(self):
        with open(self.file_path, encoding="utf-8") as file:
            for task in file.read().splitlines():
                self.tasks.append(Task(task))

    def write_file(self) -> None:
        raw_tasks = [task.raw_text for task in self.tasks]
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

    def search(self, to_match: str) -> list:
        """
        Returns list of Task objects that match the search
        Search is not case sensitive
        """
        return list(filter(lambda task: to_match.lower() in task.raw_text.lower(), self.tasks))

    def get_tasks_by_projects(self, tasks) -> dict:
        """
        Returns a dict with projects as keys and tasks as values
        Projects are sorted alphabetically
        Tasks under current projects are sorted by priority
        """
        # Get all sorted lists of projects
        all_projects = [sorted(task.projects) for task in tasks]
        # Sort the list of lists
        all_projects.sort()
        # Get all unique lists of projects
        all_projects = list(
            all_projects for all_projects, _ in itertools.groupby(all_projects)
        )

        tasks_by_projects = {}
        for projects in all_projects:
            tasks_with_current_projects = []
            for task in tasks:
                # Checking if lists contain the same elements
                if set(projects) == set(task.projects):
                    tasks_with_current_projects.append(task)
            # Key is a tuple of projects, value is a list of tasks
            tasks_current_tags_sort_priority = sorted(
                tasks_with_current_projects, key=none_priority_to_end_key
            )
            tasks_by_projects[tuple(projects)] = tasks_current_tags_sort_priority
        return tasks_by_projects

    def get_tasks_by_tags(self, tasks) -> dict:
        """
        Returns dict with tags as keys and tasks as values
        Tags are sorted alphabetically
        Tasks under current tags are sorted by priority
        """
        # Get all sorted lists of tags
        all_tags = [sorted(task.tags) for task in tasks]
        # Sort the list of lists
        all_tags.sort()
        # Get all unique lists of tags
        all_tags = list(all_tags for all_tags, _ in itertools.groupby(all_tags))

        tasks_by_tags = {}

        for tags in all_tags:
            tasks_with_current_tags = []
            for task in tasks:
                # Checking if lists contain the same elements
                if set(tags) == set(task.tags):
                    tasks_with_current_tags.append(task)
            # Sorting tasks by priority
            tasks_current_tags_sort_priority = sorted(
                tasks_with_current_tags, key=none_priority_to_end_key
            )
            # Key is a tuple of tags, value is a list of tasks
            tasks_by_tags[tuple(tags)] = tasks_current_tags_sort_priority
        return tasks_by_tags

    def __str__(self) -> str:
        raw_tasks = [task.raw_text for task in self.tasks]
        return "\n".join(raw_tasks)


def none_priority_to_end_key(task):
    """
    Key function for sorting tasks by priority.
    Tasks with no priority are sorted to the end.
    Use as key a tuple, like (False, value). If value is None, then the tuple should be (True, None)
    Tuples are compared by their first element first, then the second, et cetera.
    False sorts before True.
    So all None values will be sorted to the end.
    """
    value = task.priority if task.priority else None

    return value is None, value


def timing(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print(f"{f.__name__=}, {args=}, {kwargs=} took: {te - ts:.3f} seconds")
        return result

    return wrap
