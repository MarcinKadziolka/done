import func


class TestTask:
    def test_task_priority(self):
        string = "(A) Do homework (unit 6) @school @library +homework"
        assert func.Task(string).priority == "(A)"

    def test_task_tags(self):
        string = "(A) Do homework mk@uj.pl (unit 6) @school @library +homework"
        assert func.Task(string).tags == ["@school", "@library"]

    def test_task_project(self):
        string = "(A) Do homework 2+2 (unit 6) @school @library +homework"
        assert func.Task(string).projects == ["+homework"]

    def test_task_raw_task(self):
        string = "(A) Do homework (unit 6) @school @library +homework"
        assert func.Task(string).raw_task == "(A) Do homework (unit 6) @school @library +homework"

    def test_task_description(self):
        string = "(A) Do homework (unit 6) @school @library +homework"
        assert func.Task(string).description == "Do homework (unit 6)"


class TestCheckExactMatch:
    def test_check_exact_match_exact_match(self):
        match = "keyword"
        string = "contains keyword and should match"
        assert func.TaskParser.check_exact_match(match, string) is not None

    def test_check_exact_match_substring_match(self):
        match = "keyword"
        string = "contains keywordas a substring and should not match"
        assert func.TaskParser.check_exact_match(match, string) is None

    def test_check_exact_match_no_match(self):
        match = "keyword"
        string = "does not contain key word"
        assert func.TaskParser.check_exact_match(match, string) is None
