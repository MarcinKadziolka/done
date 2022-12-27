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


class TaskItem(OneLineAvatarIconListItem):
    def __init__(self, **kwargs):
        # Passes self to icon so it can access task text
        super(TaskItem, self).__init__(
            DeleteIcon(self, icon="trash-can-outline"), **kwargs
        )

        # Passes self to popup, so it can access task text
        self.edit_task_popup = EditTaskField(self)

    def on_press(self):
        self.edit_task_popup.open()


class EditTaskField(Popup):
    def __init__(self, calling_widget, **kwargs):
        # parent_widget should be the object where popup was called from
        # because self.parent is None
        # it's required for access
        super(EditTaskField, self).__init__(**kwargs)
        Window.borderless = True
        # Hide the title
        self.title = ""
        self.separator_height = 0
        self.calling_widget = calling_widget
        self.size_hint = (0.8, 0.1)
        self.content = MDBoxLayout(orientation="horizontal")

        # on_text_validate is what happens when enter is pressed
        self.current_input_field = MDTextField(
            on_text_validate=self.accept_task_edit, text=self.calling_widget.text
        )
        self.content.add_widget(self.current_input_field)

    def accept_task_edit(self, *args):
        print("Enter pressed")
        print(
            f"Editing task {self.calling_widget.text} to {self.current_input_field.text}"
        )
        task_manager.edit_task(
            old_task=func.Task(self.calling_widget.text),
            new_task=func.Task(self.current_input_field.text),
        )

        task_manager.write_file()
        self.calling_widget.text = self.current_input_field.text
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
        task_manager.add_task(func.Task(self.input_field.text))

        app = MDApp.get_running_app()
        app.root.ids.mdlist.clear_widgets()

        self.input_field.text = ""

        for task in task_manager.tasks:
            app.root.ids.mdlist.add_widget(TaskItem(text=task.raw_text))
        task_manager.write_file()
        self.dismiss()


class DeleteIcon(IconRightWidget):
    def __init__(self, calling_widget, **kwargs):
        # parent_widget should be the object where popup was called from
        # because self.parent is None
        # it's passed so this class can access text from parent
        super(DeleteIcon, self).__init__(**kwargs)
        self.calling_widget = calling_widget

    def on_press(self):
        self.delete_task()

    def delete_task(self, *args):
        print(f"Deleting task {self.calling_widget.text}")
        task_manager.delete_task(func.Task(self.calling_widget.text))
        self.calling_widget.parent.remove_widget(self.calling_widget)
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

    def display_search_results(self, *args):
        search_results = task_manager.search(self.text)

        app = MDApp.get_running_app()
        app.root.ids.mdlist.clear_widgets()

        for task in search_results:
            app.root.ids.mdlist.add_widget(TaskItem(text=task.raw_text))

    # TODO: Highlight search results
    # https://stackoverflow.com/questions/36666797/changing-color-of-a-part-of-text-of-a-kivy-widget
    # https://kivy.org/doc/stable/api-kivy.core.text.markup.html

    # on_text is called everytime text in the input field is changed
    def on_text(self, instance, value):
        app = MDApp.get_running_app()
        seq = app.root.ids.mdlist.children

        length = len(seq)
        for i in range(length):
            if self.text.lower() not in seq[i].text.lower():
                el = seq.pop(i)
                el.disabled = True
                el.opacity = 0
                seq.insert(0, el)
            else:
                seq[i].opacity = 1
                seq[i].disabled = False
    # def reverse_2(seq):
    #     length = len(seq)
    #     for i in range(length):
    #         seq.insert(i, seq.pop())


class MainApp(MDApp):

    title = "Done"

    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Dark"

        root = Builder.load_file("gui.kv")
        for task in task_manager.tasks:
            root.ids.mdlist.add_widget(TaskItem(text=task.raw_text))

        return root


if __name__ == "__main__":
    MainApp().run()
    task_manager.write_file()
