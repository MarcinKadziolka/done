# from kivy.config import Config
#
# Config.set("graphics", "resizable", False)
from os import path
from enum import Enum
from kivy.lang import Builder
from kivymd.app import Clock, MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem, OneLineListItem
from kivymd.uix.list.list import MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivy.animation import Animation
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivymd.uix.list import IconRightWidget, IconLeftWidget
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton, MDRectangleFlatIconButton
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.selectioncontrol import MDCheckbox
import func


class MyCheckBox(MDCheckbox):
    def __init__(self, task_list_item, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [1, 1, 1, 0]
        self.theme_text_color = "Custom"
        self.color_active = "#add8e6"
        app = MDApp.get_running_app()

        if app.theme_cls.theme_style == "Dark":
            self.color_inactive = "white"
        else:
            self.color_inactive = "black"
        self.checkbox_icon_normal = "checkbox-blank-outline"
        self.checkbox_icon_down = "checkbox-marked"
        self.task_list_item = task_list_item
        if self.task_list_item.task_object.done is True:
            self.state = "down"
        else:
            self.state = "normal"

    def on_active(self, instance, value):
        app = MDApp.get_running_app()
        current_task = self.task_list_item.task_object
        if self.state == "down" and current_task.done is False:
            new_task = func.Task("x " + current_task.raw_text)
            app.task_manager.edit_task(old_task=current_task, new_task=new_task)
            self.task_list_item.task_object = new_task
            self.task_list_item.text = new_task.raw_text
        elif self.state == "normal" and current_task.done is True:
            old_task = self.task_list_item.task_object
            new_task = func.Task(old_task.raw_text[2:])
            app.task_manager.edit_task(old_task=current_task, new_task=new_task)
            self.task_list_item.task_object = new_task
            self.task_list_item.text = new_task.raw_text

        app.task_manager.save_tasks()

        TasksScrollView.sort_all()


class DoneLeftIcon(IconLeftWidget):
    def __init__(self, task_list_item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = "assets/images/transparent.png"
        self.done_check_box = MyCheckBox(task_list_item)
        self.add_widget(self.done_check_box)


class TaskListItem(OneLineAvatarIconListItem):
    def __init__(self, task_object: func.Task, **kwargs):
        # Passes self to icon so it can access task text
        self.task_object = task_object
        super(TaskListItem, self).__init__(
            DoneLeftIcon(self), DeleteIcon(self), **kwargs
        )
        self.text = task_object.raw_text

        self.theme_text_color = "Custom"
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Dark":
            self.text_color = "white"
        else:
            self.text_color = "black"
        # Passes self to popup, so it can access task text

    def on_press(self):
        self.edit_task_popup = EditTaskField(self)
        self.edit_task_popup.open()


class MyTextField(MDTextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EditTaskField(Popup):
    def __init__(self, task_list_item, **kwargs):
        # parent_widget should be the object where popup was called from
        # because self.parent is None
        # it's required for access
        super(EditTaskField, self).__init__(**kwargs)
        # Window.borderless = True
        # Hide the title
        self.title = ""
        self.separator_height = 0
        self.task_list_item = task_list_item
        self.size_hint = (0.8, 0.1)
        self.content = MDBoxLayout(orientation="horizontal")
        # on_text_validate is what happens when enter is pressed
        self.current_input_field = MyTextField(
            on_text_validate=self.accept_task_edit,
            text=self.task_list_item.task_object.raw_text,
        )
        self.content.add_widget(self.current_input_field)

    def on_open(self):
        self.current_input_field.focus = True

    def accept_task_edit(self, *args):
        app = MDApp.get_running_app()
        old_task = self.task_list_item.task_object
        new_task = func.Task(self.current_input_field.text)
        app.task_manager.edit_task(old_task=old_task, new_task=new_task)
        app.task_manager.save_tasks()
        self.task_list_item.task_object = new_task
        self.task_list_item.text = self.current_input_field.text

        # Add tags widget if it doesn't already exist
        all_tags_widgets = get_tag_widgets(app.root.ids.mdlist.children)
        for w in all_tags_widgets:
            if sorted(self.task_list_item.task_object.tags) == w.tags:
                break
        else:
            app.root.ids.mdlist.add_widget(
                TagsItem(self.task_list_item.task_object.tags)
            )

        # Add project widgets if it doesn't already exist
        all_project_widgets = get_project_widgets(app.root.ids.mdlist.children)
        for w in all_project_widgets:
            if sorted(self.task_list_item.task_object.projects) == w.projects:
                break
        else:
            app.root.ids.mdlist.add_widget(
                ProjectsItem(self.task_list_item.task_object.projects)
            )

        if new_task.done is True:
            self.task_list_item.children[1].children[0].children[0].state = "down"
        elif new_task.done is False:
            self.task_list_item.children[1].children[0].children[0].state = "normal"

        TasksScrollView.sort_all()
        self.dismiss()


class AddTaskButton(MDIconButton):
    """
    Button class that has hidden popup with text field which is shown when button is released
    """

    def __init__(self, **kwargs):
        super(AddTaskButton, self).__init__(**kwargs)
        self.md_bg_color = "#add8e6"
        self.line_width: 1
        self.theme_icon_color = "Custom"
        self.icon_size = "48sp"
        self.task_input_popup = AddTaskTextField()

    def on_release(self):
        self.task_input_popup.open()


class AddTaskTextField(Popup):
    def __init__(self, **kwargs):
        super(AddTaskTextField, self).__init__(**kwargs)
        # Hide the title
        self.title = ""
        self.separator_height = 0

        self.size_hint = (0.8, 0.1)

        self.input_field = MDTextField(on_text_validate=self.on_enter)
        self.content = MDBoxLayout(orientation="horizontal")
        self.content.add_widget(self.input_field)

    def on_open(self):
        self.input_field.focus = True

    def on_dismiss(self):
        self.input_field.text = ""
        return super().on_dismiss()

    def on_enter(self, *args):
        if self.input_field.text == "":
            toast("Task cannot be empty")
            self.dismiss()
            return
        app = MDApp.get_running_app()
        task_to_add = func.Task(self.input_field.text)

        app.task_manager.add_task(task_to_add)
        app.task_manager.save_tasks()

        widget_to_add = TaskListItem(task_to_add)
        app.root.ids.mdlist.add_widget(widget_to_add)

        # Add tags widget if it doesn't already exist
        all_tags_widgets = get_tag_widgets(app.root.ids.mdlist.children)
        for w in all_tags_widgets:
            if sorted(widget_to_add.task_object.tags) == w.tags:
                break
        else:
            app.root.ids.mdlist.add_widget(TagsItem(widget_to_add.task_object.tags))

        # Add project widgets if it doesn't already exist
        all_project_widgets = get_project_widgets(app.root.ids.mdlist.children)
        for w in all_project_widgets:
            if sorted(widget_to_add.task_object.projects) == w.projects:
                break
        else:
            app.root.ids.mdlist.add_widget(
                ProjectsItem(widget_to_add.task_object.projects)
            )
        self.input_field.text = ""

        TasksScrollView.sort_all()

        # If the task added is the first in the list
        # highlight it and set appropriate index
        if len(app.task_manager.tasks) == 1:
            list_items = app.root.ids.mdlist.children
            app.selected_item_id = len(list_items) - 1
            app.selected_item = list_items[app.selected_item_id]
            set_active_element_theme(app.selected_item)

        # Allow for multiple entries
        Clock.schedule_once(self.refocus_ti)

    def refocus_ti(self, *args):
        self.input_field.focus = True


class DeleteIcon(IconRightWidget):
    def __init__(self, task_list_item, **kwargs):
        # parent_widget should be the object where popup was called from
        # because self.parent is None
        # it's passed so this class can access text from parent
        super(DeleteIcon, self).__init__(**kwargs)
        self.icon = "trash-can-outline"
        self.task_list_item = task_list_item
        self.theme_icon_color = "Custom"
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Dark":
            self.icon_color = "white"
        else:
            self.icon_color = "black"

    def on_press(self):
        self.delete_task()

    def delete_task(self, *args):
        app = MDApp.get_running_app()
        app.task_manager.delete_task(self.task_list_item.task_object)
        self.task_list_item.parent.remove_widget(self.task_list_item)
        app.task_manager.save_tasks()
        TasksScrollView.sort_all()


class TagsItem(OneLineListItem):
    def __init__(self, tags, *args, **kwargs):
        super(TagsItem, self).__init__(*args, **kwargs)
        self.tags = tags
        text_processed = ""
        for tag in tags:
            text_processed += str(tag) + " "
        self.text = text_processed[:-1]
        self.font_style = "H6"
        app = MDApp.get_running_app()
        self.theme_text_color = "Custom"
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Dark":
            self.text_color = "white"
        else:
            self.text_color = "black"


class ProjectsItem(OneLineListItem):
    def __init__(self, projects, *args, **kwargs):
        super(ProjectsItem, self).__init__(*args, **kwargs)
        self.projects = projects
        text_processed = ""
        for project in projects:
            text_processed += str(project) + " "
        self.text = text_processed[:-1]
        self.font_style = "H6"
        app = MDApp.get_running_app()
        self.theme_text_color = "Custom"
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Dark":
            self.text_color = "white"
        else:
            self.text_color = "black"


class TasksScrollView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def sort_all():
        app = MDApp.get_running_app()
        if app.sort_mode == SortMode.PRIORITY:
            TasksScrollView.sort_by_priority()
        elif app.sort_mode == SortMode.TAG:
            TasksScrollView.sort_by_tags()
        elif app.sort_mode == SortMode.PROJECT:
            TasksScrollView.sort_by_projects()

    @staticmethod
    def sort_by_priority():
        app = MDApp.get_running_app()
        all_widgets = get_all_widgets()
        task_widgets = get_task_widgets(all_widgets)
        tags_items = get_tag_widgets(all_widgets)
        project_widgets = get_project_widgets(all_widgets)
        for w in project_widgets:
            w.opacity = 0
        for w in tags_items:
            w.opacity = 0
        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(current_search_text, task_widgets)
        display_widget_lists(project_widgets, tags_items, unsearched, searched)

        app.sort_mode = app.sort_mode.PRIORITY

    @staticmethod
    def sort_by_tags():
        app = MDApp.get_running_app()

        all_widgets = get_all_widgets()
        task_widgets = get_task_widgets(all_widgets)
        projects_widgets = get_project_widgets(all_widgets)
        for project_widget in projects_widgets:
            project_widget.opacity = 0
        tag_widgets = get_tag_widgets(all_widgets)

        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(current_search_text, task_widgets)
        list_to_display = []

        tag_widgets.sort(key=lambda x: x.text, reverse=True)
        # Moving irrelevant widgets to the bottom
        list_to_display.extend(projects_widgets)
        list_to_display.extend(unsearched)
        # Moving empty tags to the end of the list
        # so tasks without tags appear last
        if tag_widgets[-1].tags == []:
            tag_widgets.insert(0, tag_widgets.pop())

        hidden_tag_widgets = []
        for tag_widget in tag_widgets:
            current_tasks = []
            for task_widget in searched:
                if tag_widget.tags == sorted(task_widget.task_object.tags):
                    current_tasks.append(task_widget)
            if len(current_tasks) > 0:
                tag_widget.opacity = 1
                current_tasks.append(tag_widget)
            else:
                tag_widget.opacity = 0
                hidden_tag_widgets.append(tag_widget)
            list_to_display.extend(current_tasks)

        display_widget_lists(hidden_tag_widgets, list_to_display)

        app.sort_mode = app.sort_mode.TAG

    @staticmethod
    def sort_by_projects():
        app = MDApp.get_running_app()
        all_widgets = get_all_widgets()
        project_widgets = get_project_widgets(all_widgets)
        task_widgets = get_task_widgets(all_widgets)
        tag_widgets = get_tag_widgets(all_widgets)
        for w in tag_widgets:
            w.opacity = 0

        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(current_search_text, task_widgets)

        project_widgets.sort(key=lambda x: x.text, reverse=True)

        list_to_display = []
        # Moving unnesessary widgets to the end of displaying
        list_to_display.extend(tag_widgets)
        # Moving empty projects to the end of the list
        # so tasks without tags appear last
        if project_widgets[-1].projects == []:
            project_widgets.insert(0, project_widgets.pop())

        hidden_project_tags = []
        for project_widget in project_widgets:
            current_tasks = []
            for task_widget in searched:
                if project_widget.projects == sorted(task_widget.task_object.projects):
                    current_tasks.append(task_widget)
            if len(current_tasks) > 0:
                project_widget.opacity = 1
                current_tasks.append(project_widget)
            else:
                project_widget.opacity = 0
                hidden_project_tags.append(project_widget)
            list_to_display.extend(current_tasks)
        display_widget_lists(hidden_project_tags, unsearched, list_to_display)

        app.sort_mode = app.sort_mode.PROJECT


class DarkSearchTextInput(MDTextField):
    def __init__(self, **kwargs):
        super(DarkSearchTextInput, self).__init__(**kwargs)
        self.mode = "round"

        self.default_size_hint_x = 0.6
        self.default_size_hint_y = 0.08
        self.default_size_height = 40
        # self.size_hint_y = self.default_size_hint_y
        self.size_hint_x = self.default_size_hint_x
        self.height = 40
        # self.width = 30

        self.valign = "center"
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        self.hint_text = "search"
        # self.font_size = 300.35 * self.size_hint_y
        self.font_size = 20
        self.active_line = False
        self.multiline = False
        self.icon_left = "magnify"

        # Dark theme
        self.fill_color_normal = "#000000"
        self.hint_text_color_normal = 1, 1, 1, 1
        self.hint_text_color_focus = 1, 1, 1, 1
        self.icon_left_color_normal = 1, 1, 1, 1
        self.icon_left_color_focus = 1, 1, 1, 1
        self.text_color_normal = [1, 1, 1, 1]
        self.text_color_focus = [1, 1, 1, 1]

    def on_focus(self, *args):
        duration = 0.05
        if self.focus:
            # Scaling up
            anim = Animation(size=(self.width, self.height + 5), duration=duration)
            anim.start(self)
        else:
            # Scaling to default
            anim = Animation(
                size=(self.width, self.default_size_height), duration=duration
            )
            anim.start(self)  # start the animation

    # TODO: Highlight search results
    # https://stackoverflow.com/questions/36666797/changing-color-of-a-part-of-text-of-a-kivy-widget
    # https://kivy.org/doc/stable/api-kivy.core.text.markup.html

    # on_text is called everytime text in the input field is changed
    def on_text(self, instance, value):
        TasksScrollView.sort_all()


class LightSearchTextInput(DarkSearchTextInput):
    def __init__(self, **kwargs):
        super(LightSearchTextInput, self).__init__(**kwargs)
        self.hint_text_color_normal = 0, 0, 0, 1
        self.hint_text_color_focus = 0, 0, 0, 1
        self.icon_left_color_normal = 0, 0, 0, 1
        self.icon_left_color_focus = 0, 0, 0, 1
        self.text_color_normal = [0, 0, 0, 1]
        self.text_color_focus = [0, 0, 0, 1]
        self.fill_color_normal = "#F5F5DC"


def filter_by_search_text_tags(
    search_text: str, task_widgets: list[TaskListItem]
) -> tuple[list[TaskListItem], list[TaskListItem]]:
    """
    return searched_sorted_by_priority, unsearched
    """
    search_text = search_text.lower()

    searched = []
    unsearched = []

    for task_widget in task_widgets:
        if search_text in task_widget.text.lower():
            task_widget.opacity = 1
            task_widget.disabled = False
            searched.append(task_widget)
        else:
            task_widget.opacity = 0
            task_widget.disabled = True
            unsearched.append(task_widget)
    searched_sorted_by_priority = sorted(
        searched,
        key=lambda x: (
            x.task_object.raw_text,
            sorted(x.task_object.tags),
            x.task_object.priority,
        ),
        reverse=True,
    )
    return searched_sorted_by_priority, unsearched


def filter_by_search_text(
    search_text: str, task_widgets: list[TaskListItem]
) -> tuple[list[TaskListItem], list[TaskListItem]]:
    """
    return searched_sorted_by_priority, unsearched
    """
    search_text = search_text.lower()

    searched = []
    unsearched = []

    for task_widget in task_widgets:
        if search_text in task_widget.text.lower():
            task_widget.opacity = 1
            task_widget.disabled = False
            searched.append(task_widget)
        else:
            task_widget.opacity = 0
            task_widget.disabled = True
            unsearched.append(task_widget)
    searched_sorted_by_priority = sorted(
        searched, key=func.none_priority_to_end_key_for_widgets, reverse=True
    )
    return searched_sorted_by_priority, unsearched


def filter_by_search_text(
    search_text: str, task_widgets: list[TaskListItem]
) -> tuple[list[TaskListItem], list[TaskListItem]]:
    """
    return searched_sorted_by_priority, unsearched
    """
    search_text = search_text.lower()

    searched = []
    unsearched = []

    for task_widget in task_widgets:
        if search_text in task_widget.text.lower():
            task_widget.opacity = 1
            task_widget.disabled = False
            searched.append(task_widget)
        else:
            task_widget.opacity = 0
            task_widget.disabled = True
            unsearched.append(task_widget)
    searched_sorted_by_priority = sorted(
        searched, key=func.none_priority_to_end_key_for_widgets, reverse=True
    )
    return searched_sorted_by_priority, unsearched


def get_all_widgets():
    return MDApp.get_running_app().root.ids.mdlist.children


def display_widget_lists(*widget_lists: list):
    """
    Displays the widgets in the lists in the reverse order they are passed
    Example:
    display_widget_lists([1, 2, 3], [4, 5, 6])
    will display 6, 5, 4, 3, 2, 1
    """

    all_widgets = []
    for widget_list in widget_lists:
        for widget in widget_list:
            all_widgets.append(widget)

    app = MDApp.get_running_app()
    app.root.ids.mdlist.children = all_widgets


# Navbar content below


class MyToggleButton(MDRectangleFlatIconButton, MDToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_down = self.theme_cls.primary_color

    def on_state(self, *_):
        app = MDApp.get_running_app()
        if app.root.ids.toggledark.state == "down":
            set_dark_theme()
        elif app.root.ids.togglelight.state == "down":
            set_light_theme()


def get_task_widgets(all_widgets):
    return [widget for widget in all_widgets if isinstance(widget, TaskListItem)]


def get_tag_widgets(all_widgets):
    return [widget for widget in all_widgets if isinstance(widget, TagsItem)]


def get_project_widgets(all_widgets):
    return [widget for widget in all_widgets if isinstance(widget, ProjectsItem)]


def set_dark_theme():
    app = MDApp.get_running_app()
    task_widgets = get_task_widgets(app.root.ids.mdlist.children)
    tags_widgets = get_tag_widgets(app.root.ids.mdlist.children)
    projects_widgets = get_project_widgets(app.root.ids.mdlist.children)
    # Setting dark theme
    app.theme_cls.theme_style = "Dark"
    app.root.ids.settingslabel.text_color = "white"
    for task in task_widgets:
        task.text_color = "white"
        # Trash icon color
        task.children[0].children[0].icon_color = "white"
        # Checkbox color
        task.children[1].children[0].children[0].color_inactive = "white"
        task.children[1].children[0].children[0].color_active = "#add8e6"

    for tag in tags_widgets:
        tag.text_color = "white"

    for project in projects_widgets:
        project.text_color = "white"

    app.root.ids.add_task_button.line_color = "#add8e6"
    # Creating a new search field with the light_theme
    # and adding it to widget tree
    dark_search_field = DarkSearchTextInput()
    search_field_to_delete = app.root.ids.search_text_input
    app.root.ids.mainbox.remove_widget(search_field_to_delete)
    app.root.ids["search_text_input"] = dark_search_field
    app.root.ids.mainbox.add_widget(dark_search_field, 2)

    func.save_settings(theme=app.theme_cls.theme_style)


def set_light_theme():
    app = MDApp.get_running_app()
    task_widgets = get_task_widgets(app.root.ids.mdlist.children)
    tags_widgets = get_tag_widgets(app.root.ids.mdlist.children)
    projects_widgets = get_project_widgets(app.root.ids.mdlist.children)

    # Setting light theme
    app.theme_cls.theme_style = "Light"
    app.root.ids.settingslabel.text_color = "black"
    for task in task_widgets:
        task.text_color = "black"
        # Trash icon color
        task.children[0].children[0].icon_color = "black"
        # Checkbox color
        task.children[1].children[0].children[0].color_inactive = "black"
        task.children[1].children[0].children[0].color_active = "#add8e6"

    for tag in tags_widgets:
        tag.text_color = "black"

    for project in projects_widgets:
        project.text_color = "black"

    app.root.ids.add_task_button.line_color = "black"
    # Creating a new search field with the light_theme
    # and adding it to widget tree
    light_search_field = LightSearchTextInput()
    search_field_to_delete = app.root.ids.search_text_input
    app.root.ids.mainbox.remove_widget(search_field_to_delete)
    app.root.ids["search_text_input"] = light_search_field
    app.root.ids.mainbox.add_widget(light_search_field, 2)

    func.save_settings(theme=app.theme_cls.theme_style)


def set_normal_element_theme(item, theme):
    if item is None:
        return
    if theme == "Dark":
        item.text_color = "white"
    else:
        item.text_color = "black"


def set_active_element_theme(item):
    item.text_color = "red"


class ContentNavigationDrawer(MDBoxLayout):
    pass


class ChooseFileButton(MDRectangleFlatIconButton):
    def __init__(self, **kwargs):
        super(ChooseFileButton, self).__init__(**kwargs)

    def on_release(self):
        app = MDApp.get_running_app()
        app.root.ids.mdlist.clear_widgets()
        app.file_manager_open()


class SortMode(Enum):
    PRIORITY = 1
    TAG = 2
    PROJECT = 3


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"
        self.title = "Done"
        self.path = "./tutorial.txt"
        self.task_manager = None
        self.manager_open = False
        self.sort_mode = SortMode.PRIORITY
        self.selected_item = None
        self.selected_item_id = None
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            ext=[".txt"],
        )
        self.dialog = MDDialog(
            text="Select .txt file",
            buttons=[MDFlatButton(text="OK", on_release=self.close_dialog)],
        )

    def build(self):
        Window.bind(on_keyboard=self.on_keyboard)
        root = Builder.load_file("done.kv")
        return root

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        app = MDApp.get_running_app()
        # Adding task
        if codepoint == "a" and (
            modifier == ["ctrl", "shift"] or modifier == ["shift", "ctrl"]
        ):
            app.root.ids.add_task_button.on_release()

        # Starting search
        elif codepoint == "s" and (
            modifier == ["ctrl", "shift"] or modifier == ["shift", "ctrl"]
        ):
            app.root.ids.search_text_input.focus = True

        # Sort by priority
        elif codepoint == "1" and (
            modifier == ["ctrl", "shift"] or modifier == ["shift", "ctrl"]
        ):
            toast("Sorting by priority")
            app.root.ids.tasks_scroll_view.sort_by_priority()

        # Sort by tags
        elif codepoint == "2" and (
            modifier == ["ctrl", "shift"] or modifier == ["shift", "ctrl"]
        ):
            toast("Sorting by tags")
            app.root.ids.tasks_scroll_view.sort_by_tags()

        # Sort by projects
        elif codepoint == "3" and (
            modifier == ["ctrl", "shift"] or modifier == ["shift", "ctrl"]
        ):
            toast("Sorting by projects")
            app.root.ids.tasks_scroll_view.sort_by_projects()

        # Edit selected task
        elif codepoint == "e" and (
            modifier == ["ctrl", "shift"] or modifier == ["ctrl", "shift"]
        ):
            self.selected_item.on_press()

        # Delete selected task
        elif codepoint == "d" and (
            modifier == ["ctrl", "shift"] or modifier == ["shift", "ctrl"]
        ):
            delete_object = self.selected_item.children[0].children[0]
            delete_object.delete_task()
            items_list = app.root.ids.mdlist.children
            if self.selected_item_id < len(items_list) - 1:
                self.selected_item = items_list[self.selected_item_id]
            else:
                self.selected_item_id -= 1
                self.selected_item = items_list[self.selected_item_id]
            set_active_element_theme(self.selected_item)

        # Mark selected task as done
        elif codepoint == "x" and (
            modifier == ["ctrl", "shift"] or modifier == ["ctrl", "shift"]
        ):
            checkbox = self.selected_item.children[1].children[0].children[0]
            checkbox.state = "down" if checkbox.state == "normal" else "normal"

            set_normal_element_theme(self.selected_item, app.theme_cls.theme_style)
            item_id = self.selected_item_id
            self.selected_item = app.root.ids.mdlist.children[item_id]
            set_active_element_theme(self.selected_item)
        # Arrow up
        elif key == 273:
            list_items = app.root.ids.mdlist.children
            if self.selected_item_id + 1 > len(list_items) - 1:
                return
            previous_item = self.selected_item

            if not isinstance(list_items[self.selected_item_id + 1], TaskListItem):
                if self.selected_item_id + 2 > len(list_items) - 1:
                    return
                self.selected_item_id += 2
            else:
                self.selected_item_id += 1
            self.selected_item = list_items[self.selected_item_id]
            set_normal_element_theme(previous_item, app.theme_cls.theme_style)
            set_active_element_theme(self.selected_item)
        # Arrow down
        elif key == 274:
            list_items = app.root.ids.mdlist.children
            if self.selected_item_id - 1 < 0:
                return
            previous_item = self.selected_item
            if self.selected_item_id - 1 >= 0:
                next_item = list_items[self.selected_item_id - 1]
                if isinstance(next_item, TaskListItem):
                    self.selected_item_id -= 1
                elif self.selected_item_id - 2 >= 0:
                    next_item = list_items[self.selected_item_id - 2]
                    if isinstance(next_item, TaskListItem):
                        self.selected_item_id -= 2
                else:
                    return
            self.selected_item = list_items[self.selected_item_id]
            set_normal_element_theme(previous_item, app.theme_cls.theme_style)
            set_active_element_theme(self.selected_item)

    def on_start(self):
        settings = func.read_settings()

        app = MDApp.get_running_app()

        search_widget = DarkSearchTextInput()
        app.root.ids["search_text_input"] = search_widget
        app.root.ids.mainbox.add_widget(search_widget, 2)

        if settings or path.exists(self.path):
            if settings:
                self.task_manager = func.TaskManager(settings["path"])
                if settings["theme"] == "Dark":
                    set_dark_theme()
                else:
                    set_light_theme()
            else:
                self.task_manager = func.TaskManager(self.path)
                set_light_theme()
            self.add_and_display_all_widgets()
        else:
            self.dialog.open()

        items_list = self.root.ids.mdlist.children
        length = len(items_list)
        if length <= 2:
            return
        self.selected_item_id = length - 1
        self.selected_item = self.root.ids.mdlist.children[self.selected_item_id]
        set_active_element_theme(self.selected_item)

    def close_dialog(self, *_):
        self.dialog.dismiss()
        self.file_manager_open()

    def file_manager_open(self):
        self.file_manager.show(
            self.file_manager.current_path
        )  # output manager to the screen
        self.manager_open = True

    def add_and_display_all_widgets(self):
        app = MDApp.get_running_app()
        for task in self.task_manager.tasks:
            app.root.ids.mdlist.add_widget(TaskListItem(task))

        unique_tags_combinations = self.task_manager.get_unique_tags_combinations(
            self.task_manager.tasks
        )
        for tag_combination in unique_tags_combinations:
            app.root.ids.mdlist.add_widget(TagsItem(tag_combination))

        unique_projects_combinations = (
            self.task_manager.get_unique_projects_combinations(self.task_manager.tasks)
        )

        for project_combination in unique_projects_combinations:
            app.root.ids.mdlist.add_widget(ProjectsItem(project_combination))

        TasksScrollView.sort_all()

    def select_path(self, path):
        """It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        """
        self.exit_manager()
        self.task_manager = func.TaskManager(path)
        func.save_settings(path=path)
        toast(path)
        self.add_and_display_all_widgets()
        set_light_theme()
        func.save_settings(theme="Light")

        items_list = self.root.ids.mdlist.children
        length = len(items_list)
        if length <= 2:
            return
        self.selected_item_id = length - 1
        self.selected_item = self.root.ids.mdlist.children[self.selected_item_id]
        set_active_element_theme(self.selected_item)

    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""

        self.manager_open = False
        self.file_manager.close()


if __name__ == "__main__":
    MainApp().run()
