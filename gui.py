from os import wait
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.textfield import MDTextField
from kivy.animation import Animation
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivymd.uix.list import IconRightWidget
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton, MDRectangleFlatIconButton
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
import func


class TaskListItem(OneLineAvatarIconListItem):
    def __init__(self, task_object: func.Task, **kwargs):
        # Passes self to icon so it can access task text
        super(TaskListItem, self).__init__(
            DeleteIcon(self, icon="trash-can-outline"), **kwargs
        )
        self.task_object = task_object
        self.text = task_object.raw_text

        self.theme_text_color = "Custom"
        self.text_color = "white"
        # Passes self to popup, so it can access task text
        self.edit_task_popup = EditTaskField(self)

    def on_press(self):
        self.edit_task_popup.open()


class EditTaskField(Popup):
    def __init__(self, task_list_item, **kwargs):
        # parent_widget should be the object where popup was called from
        # because self.parent is None
        # it's required for access
        super(EditTaskField, self).__init__(**kwargs)
        Window.borderless = True
        # Hide the title
        self.title = ""
        self.separator_height = 0
        self.task_list_item = task_list_item
        self.size_hint = (0.8, 0.1)
        self.content = MDBoxLayout(orientation="horizontal")

        # on_text_validate is what happens when enter is pressed
        self.current_input_field = MDTextField(
            on_text_validate=self.accept_task_edit, text=self.task_list_item.text
        )
        self.content.add_widget(self.current_input_field)

    def accept_task_edit(self, *args):
        app = MDApp.get_running_app()
        print("Enter pressed")
        old_task = self.task_list_item.task_object
        new_task = func.Task(self.current_input_field.text)
        print(f"Editing task {old_task.raw_text} to {new_task.raw_text}")
        app.task_manager.edit_task(old_task=old_task, new_task=new_task)
        app.task_manager.write_file()
        self.task_list_item.task_object = new_task
        self.task_list_item.text = self.current_input_field.text

        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(
            current_search_text, app.root.ids.mdlist.children
        )
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
        Window.borderless = True
        # Hide the title
        self.title = ""
        self.separator_height = 0

        self.size_hint = (0.8, 0.1)

        self.input_field = MDTextField(on_text_validate=self.on_enter)

        self.content = MDBoxLayout(orientation="horizontal")
        self.content.add_widget(self.input_field)

    def on_enter(self, *args):
        app = MDApp.get_running_app()
        print("Enter pressed")
        task_to_add = func.Task(self.input_field.text)

        app.task_manager.add_task(task_to_add)
        app.task_manager.write_file()

        app.root.ids.mdlist.add_widget(TaskListItem(task_to_add))
        self.input_field.text = ""

        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(
            current_search_text, app.root.ids.mdlist.children
        )
        display_widget_lists(unsearched, searched)

        self.dismiss()


class DeleteIcon(IconRightWidget):
    def __init__(self, task_list_item, **kwargs):
        # parent_widget should be the object where popup was called from
        # because self.parent is None
        # it's passed so this class can access text from parent
        super(DeleteIcon, self).__init__(**kwargs)
        self.task_list_item = task_list_item
        self.theme_icon_color = "Custom"
        self.icon_color = "white"

    def on_press(self):
        self.delete_task()

    def delete_task(self, *args):
        app = MDApp.get_running_app()
        print(f"Deleting task {self.task_list_item.text}")
        app.task_manager.delete_task(self.task_list_item.task_object)
        self.task_list_item.parent.remove_widget(self.task_list_item)
        app.task_manager.write_file()


class TasksScrollView(ScrollView):
    pass


class DarkSearchTextInput(MDTextField):
    def __init__(self, **kwargs):
        super(DarkSearchTextInput, self).__init__(**kwargs)
        self.mode = "round"

        self.default_size_hint_x = 0.5
        self.default_size_hint_y = 0.07

        self.size_hint_y = self.default_size_hint_y
        self.size_hint_x = self.default_size_hint_x

        self.valign = "center"
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        self.hint_text = "search"
        self.font_size = 1.35 * self.height
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
        task_widgets = get_task_widgets()
        searched, unsearched = filter_by_search_text(self.text, task_widgets)
        display_widget_lists(unsearched, searched)


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


def get_task_widgets():
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


def set_dark_theme():
    app = MDApp.get_running_app()
    task_widgets = get_task_widgets()
    # Setting dark theme
    app.theme_cls.theme_style = "Dark"
    app.root.ids.settingslabel.text_color = "white"
    for task in task_widgets:
        task.text_color = "white"
        task.children[0].children[0].icon_color = "white"

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
    task_widgets = get_task_widgets()
    # Setting light theme
    app.theme_cls.theme_style = "Light"
    app.root.ids.settingslabel.text_color = "black"
    for task in task_widgets:
        task.text_color = "black"
        task.children[0].children[0].icon_color = "black"

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
        self.theme_cls.theme_style = "Dark"
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

            current_search_text = app.root.ids.search_text_input.text
            searched, unsearched = filter_by_search_text(
                current_search_text, app.root.ids.mdlist.children
            )
            display_widget_lists(unsearched, searched)

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
        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(
            current_search_text, app.root.ids.mdlist.children
        )
        display_widget_lists(unsearched, searched)

    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""

        self.manager_open = False
        self.file_manager.close()


if __name__ == "__main__":
    MainApp().run()
