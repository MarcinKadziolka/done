import func


class TestEditing:
    def test_editing(self):
        tm = func.TaskManager()
        tm.tasks = [
            func.Task("Posprzątać pokój"),
            func.Task("Zrobić pranie"),
            func.Task("Zrobić zakupy"),
            func.Task("Przyrządzić obiad"),
        ]
        tm.edit_task(func.Task("Posprzątać pokój"), func.Task("Posprzątać mieszkanie"))
        assert func.Task("Posprzątać mieszkanie") in tm.tasks


class TestSearch:
    def test_search(self):
        tm = func.TaskManager()
        tm.tasks = [
            func.Task("Posprzątać pokój"),
            func.Task("Zrobić pranie"),
            func.Task("Zrobić zakupy"),
            func.Task("Przyrządzić obiad"),
        ]
        search_results = tm.search("robić")
        assert search_results == [
            func.Task("Zrobić pranie"),
            func.Task("Zrobić zakupy"),
        ]


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
        assert (
            func.Task(string).raw_text
            == "(A) Do homework (unit 6) @school @library +homework"
        )

    def test_task_description(self):
        string = "(A) Do homework (unit 6) @school @library +homework"
        assert func.Task(string).description == "Do homework (unit 6)"
