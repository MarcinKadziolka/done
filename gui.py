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

import func


task_manager = func.TaskManager("./file.txt")


class TaskListItem(OneLineAvatarIconListItem):
    def __init__(self, task_object: func.Task, **kwargs):
        # Passes self to icon so it can access task text
        super(TaskListItem, self).__init__(
            DeleteIcon(self, icon="trash-can-outline"), **kwargs
        )
        self.task_object = task_object
        self.text = task_object.raw_text

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
        print("Enter pressed")
        old_task = self.task_list_item.task_object
        new_task = func.Task(self.current_input_field.text)
        print(f"Editing task {old_task.raw_text} to {new_task.raw_text}")
        task_manager.edit_task(old_task=old_task, new_task=new_task)
        task_manager.write_file()
        self.task_list_item.task_object = new_task
        self.task_list_item.text = self.current_input_field.text

        app = MDApp.get_running_app()
        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(
            current_search_text, app.root.ids.mdlist.children
        )
        display_widget_lists(unsearched, searched)

        self.dismiss()


class AddTaskButton(Button):
    """
    Button class that has hidden popup with text field which is shown when button is released
    """

    def __init__(self, **kwargs):
        super(AddTaskButton, self).__init__(**kwargs)

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
        print("Enter pressed")
        task_to_add = func.Task(self.input_field.text)

        task_manager.add_task(task_to_add)
        task_manager.write_file()

        app = MDApp.get_running_app()
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

    def on_press(self):
        self.delete_task()

    def delete_task(self, *args):
        print(f"Deleting task {self.task_list_item.text}")
        task_manager.delete_task(self.task_list_item.task_object)
        self.task_list_item.parent.remove_widget(self.task_list_item)
        task_manager.write_file()


class TasksScrollView(ScrollView):
    pass


class SearchTextInput(MDTextField):
    default_size_hint_x = 0.5
    default_size_hint_y = 0.07

    def on_focus(self, *args):
        duration = 0.05
        if self.focus:
            # Scaling up
            anim = Animation(
                size_hint=(
                    self.default_size_hint_x + 0.05,
                    self.default_size_hint_y + 0.03,
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


class MainApp(MDApp):

    title = "Done"

    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Dark"
        root = Builder.load_file("gui.kv")
        for task in task_manager.tasks:
            root.ids.mdlist.add_widget(TaskListItem(task))
        return root

    def on_start(self):
        app = MDApp.get_running_app()
        current_search_text = app.root.ids.search_text_input.text
        searched, unsearched = filter_by_search_text(
            current_search_text, app.root.ids.mdlist.children
        )
        display_widget_lists(unsearched, searched)


if __name__ == "__main__":
    MainApp().run()
    task_manager.write_file()
