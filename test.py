import func
# from unittest.mock import mock_open, patch


class TestTaskParser:
    def test_task_parser_parse_tags(self):
        string = "(A) Example task @next @action +project1"
        assert func.TaskParser.parse_tags(string) == ["next", "action"]

    def test_task_parser_parse_projects(self):
        string = "(A) Example task @next @action +project1"
        assert func.TaskParser.parse_projects(string) == ["project1"]

    def test_task_parser_parse_description(self):
        string = "(A) Example task @next @action +project1"
        assert func.TaskParser.parse_description(string) == "Example task"

    def test_task_parser_parse_priority(self):
        string = "(A) Example task @next @action +project1"
        assert func.TaskParser.parse_priority(string) == "A"


class TestCheckExactMatch:
    def test_check_exact_match_exact_match(self):
        match = "keyword"
        string = "contains keyword and should match"
        assert func.TaskManager.check_exact_match(match, string) is not None

    def test_check_exact_match_substring_match(self):
        match = "keyword"
        string = "contains keywordas a substring and should not match"
        assert func.TaskManager.check_exact_match(match, string) is None

    def test_check_exact_match_no_match(self):
        match = "keyword"
        string = "does not contain key word"
        assert func.TaskManager.check_exact_match(match, string) is None


class TestFilterTasks:
    def test_filter_tasks_no_match(self):
        o = func.TaskManager()
        o.task_list = ["Some task", "Another task"]
        assert o.filter_tasks("@to_match") == []

    def test_filter_tasks_match(self):
        o = func.TaskManager()
        o.task_list = ["Task with @to_match", "Task without match"]
        assert o.filter_tasks("to_match") == ["Task with @to_match"]

    def test_filter_tasks_two_matches(self):
        o = func.TaskManager()
        o.task_list = ["Task with @to_match", "Another @to_match"]
        assert o.filter_tasks("to_match") == ["Task with @to_match",
                                              "Another @to_match"]
