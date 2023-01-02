# from kivy.config import Config
#
# Config.set("graphics", "resizable", False)
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

        task_widgets = get_task_widgets(app.root.ids.mdlist.children)
        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(current_search_text, task_widgets)
        display_widget_lists(unsearched, searched)


class DoneLeftIcon(IconLeftWidget):
    def __init__(self, task_list_item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = "transparent.png"
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
        print("Enter pressed")
        old_task = self.task_list_item.task_object
        new_task = func.Task(self.current_input_field.text)
        print(f"Editing task {old_task.raw_text} to {new_task.raw_text}")
        app.task_manager.edit_task(old_task=old_task, new_task=new_task)
        app.task_manager.save_tasks()
        self.task_list_item.task_object = new_task
        self.task_list_item.text = self.current_input_field.text

        if new_task.done is True:
            self.task_list_item.children[1].children[0].children[0].state = "down"
        elif new_task.done is False:
            self.task_list_item.children[1].children[0].children[0].state = "normal"

        task_widgets = get_task_widgets(app.root.ids.mdlist.children)
        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(current_search_text, task_widgets)
        display_widget_lists(unsearched, searched)

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
        self.input_field.focus = True

    def on_enter(self, *args):
        app = MDApp.get_running_app()
        task_to_add = func.Task(self.input_field.text)

        app.task_manager.add_task(task_to_add)
        app.task_manager.save_tasks()

        app.root.ids.mdlist.add_widget(TaskListItem(task_to_add))
        self.input_field.text = ""

        current_search_text = app.root.ids.search_text_input.text
        task_widgets = get_task_widgets(app.root.ids.mdlist.children)
        searched, unsearched = filter_by_search_text(current_search_text, task_widgets)
        display_widget_lists(unsearched, searched)

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
        print(f"Deleting task {self.task_list_item.text}")
        app.task_manager.delete_task(self.task_list_item.task_object)
        self.task_list_item.parent.remove_widget(self.task_list_item)
        app.task_manager.save_tasks()


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


class ProjectsItem(TagsItem):
    def __init__(self, tags, *args, **kwargs):
        super(TagsItem, self).__init__(*args, **kwargs)


class TasksScrollView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def sort_by_priority(self):
        app = MDApp.get_running_app()
        task_widgets = get_task_widgets(app.root.ids.mdlist.children)
        tags_items = get_tag_widgets(app.root.ids.mdlist.children)
        # for tag_item in tags_items:
        #     tag_item.opacity = 0
        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(current_search_text, task_widgets)
        print(f"{searched=}")
        print(f"{unsearched=}")
        display_widget_lists(tags_items, unsearched, searched)

    def sort_by_tags(self):
        print("Sort by tags")
        app = MDApp.get_running_app()
        all_widgets = get_all_widgets()
        task_widgets = get_task_widgets(all_widgets)
        tag_widgets = get_tag_widgets(all_widgets)
        list_to_display = []

        # Moving empty tags to the end of the list
        # so tasks without tags appear last
        if tag_widgets[-1].tags == []:
            tag_widgets.insert(0, tag_widgets.pop())

        for tag_widget in tag_widgets:
            current_tasks = []
            for task_widget in task_widgets:
                if tag_widget.tags == sorted(task_widget.task_object.tags):
                    current_tasks.append(task_widget)
            current_tasks.append(tag_widget)
            list_to_display.extend(current_tasks)
        app = MDApp.get_running_app()
        app.root.ids.mdlist.children = list_to_display

    def sort_by_projects(self):
        print("Sort by projects")


class DarkSearchTextInput(MDTextField):
    def __init__(self, **kwargs):
        super(DarkSearchTextInput, self).__init__(**kwargs)
        self.mode = "round"

        self.default_size_hint_x = 0.5
        self.default_size_hint_y = 0.08

        self.size_hint_y = self.default_size_hint_y
        self.size_hint_x = self.default_size_hint_x

        self.valign = "center"
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        self.hint_text = "search"
        self.font_size = 300.35 * self.size_hint_y
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
            anim = Animation(
                size_hint=(
                    self.default_size_hint_x + 0.01,
                    self.default_size_hint_y + 0.01,
                ),
                duration=duration,
            )
            anim.start(self)
        else:
            # Scaling to default
            anim = Animation(
                size_hint=(self.default_size_hint_x, self.default_size_hint_y),
                duration=duration,
            )
            anim.start(self)  # start the animation

    # TODO: Highlight search results
    # https://stackoverflow.com/questions/36666797/changing-color-of-a-part-of-text-of-a-kivy-widget
    # https://kivy.org/doc/stable/api-kivy.core.text.markup.html

    # on_text is called everytime text in the input field is changed
    def on_text(self, instance, value):
        app = MDApp.get_running_app()
        task_widgets = get_task_widgets(app.root.ids.mdlist.children)
        tags_widgets = get_tag_widgets(app.root.ids.mdlist.children)
        searched, unsearched = filter_by_search_text(self.text, task_widgets)
        display_widget_lists(tags_widgets, unsearched, searched)


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

    app.root.ids.add_task_button.line_color = "black"
    # Creating a new search field with the light_theme
    # and adding it to widget tree
    light_search_field = LightSearchTextInput()
    search_field_to_delete = app.root.ids.search_text_input
    app.root.ids.mainbox.remove_widget(search_field_to_delete)
    app.root.ids["search_text_input"] = light_search_field
    app.root.ids.mainbox.add_widget(light_search_field, 2)

    func.save_settings(theme=app.theme_cls.theme_style)


class ContentNavigationDrawer(MDBoxLayout):
    pass


class ChooseFileButton(MDRectangleFlatIconButton):
    def __init__(self, **kwargs):
        super(ChooseFileButton, self).__init__(**kwargs)

    def on_release(self):
        app = MDApp.get_running_app()
        app.root.ids.mdlist.clear_widgets()
        app.file_manager_open()


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"
        self.title = "Done"
        self.path = None
        self.task_manager = None
        self.manager_open = False
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
        root = Builder.load_file("gui.kv")
        return root

    def on_start(self):
        settings = func.read_settings()

        app = MDApp.get_running_app()

        search_widget = DarkSearchTextInput()
        app.root.ids["search_text_input"] = search_widget
        app.root.ids.mainbox.add_widget(search_widget, 2)

        if settings:
            self.task_manager = func.TaskManager(settings["path"])
            for task in self.task_manager.tasks:
                app.root.ids.mdlist.add_widget(TaskListItem(task))
            if settings["theme"] == "Dark":
                set_dark_theme()
            else:
                set_light_theme()

            unique_tags_combinations = self.task_manager.get_unique_tags_combinations(
                self.task_manager.tasks
            )
            for tag_combination in unique_tags_combinations:
                print(f"{tag_combination=}")
                app.root.ids.mdlist.add_widget(TagsItem(tag_combination))
            tags_widgets = get_tag_widgets(app.root.ids.mdlist.children)
            task_widgets = get_task_widgets(app.root.ids.mdlist.children)
            current_search_text = app.root.ids.search_text_input.text
            searched, unsearched = filter_by_search_text(
                current_search_text, task_widgets
            )
            display_widget_lists(tags_widgets, unsearched, searched)

        else:
            self.dialog.open()

    def close_dialog(self, *_):
        self.dialog.dismiss()
        self.file_manager_open()

    def file_manager_open(self):
        self.file_manager.show(
            self.file_manager.current_path
        )  # output manager to the screen
        self.manager_open = True

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

        app = MDApp.get_running_app()
        for task in self.task_manager.tasks:
            app.root.ids.mdlist.add_widget(TaskListItem(task))

        unique_tags_combinations = self.task_manager.get_unique_tags_combinations(
            self.task_manager.tasks
        )
        for tag_combination in unique_tags_combinations:
            print(f"{tag_combination=}")
            app.root.ids.mdlist.add_widget(TagsItem(tag_combination))

        unique_projects_combinations = (
            self.task_manager.get_unique_projects_combinations(self.task_manager.tasks)
        )

        for project_combination in unique_tags_combinations:
            print(f"{project_combination=}")
            app.root.ids.mdlist.add_widget(ProjectItem(project_combination))

        tags_widgets = get_tag_widgets(app.root.ids.mdlist.children)
        task_widgets = get_task_widgets(app.root.ids.mdlist.children)
        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(current_search_text, task_widgets)
        display_widget_lists(tags_widgets, unsearched, searched)
        set_light_theme()
        func.save_settings(theme="Light")

    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""

        self.manager_open = False
        self.file_manager.close()


if __name__ == "__main__":
    MainApp().run()
