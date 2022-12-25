from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.textfield import MDTextField
from kivy.animation import Animation
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
import func


tm = func.TaskManager("./file.txt")


class AddTaskButton(Button):
    def __init__(self, **kwargs):
        super(AddTaskButton, self).__init__(**kwargs)

        self.task_input_popup = AddTaskTextField(self)

    def add_task(self, *args):
        self.task_input_popup.open()


class AddTaskTextField(Popup):
    def __init__(self, my_widget, **kwargs):
        # my_widget is now the object where popup was called from.
        super(AddTaskTextField, self).__init__(**kwargs)
        Window.borderless = True
        # Hide the title
        self.title = ""
        self.separator_height = 0

        self.my_widget = my_widget
        self.size_hint = (0.8, 0.1)
        self.content = MDBoxLayout(orientation="horizontal")

        self.input_field = MDTextField(on_text_validate=self.on_enter)
        # self.save_button.bind(on_press=self.save)
        self.content.add_widget(self.input_field)

    def on_enter(self, *args):
        print("Enter pressed")
        tm.add_task(func.Task(self.input_field.text))
        app = MDApp.get_running_app()
        # Clear widget
        app.root.ids.mdlist.clear_widgets()
        # Clear input field
        self.input_field.text = ""
        for task in tm.tasks:
            app.root.ids.mdlist.add_widget(OneLineListItem(text=task.raw_text))
        self.dismiss()

    def cancel(self, *args):
        print("cancel")
        self.dismiss()

    pass


class TasksScrollView(ScrollView):
    pass


class SearchTextInput(MDTextField):
    default_size_hint_x = 0.5
    default_size_hint_y = 0.07

    def on_focus(self, *args):
        duration = 0.05
        if self.focus:  # gained focus
            # create an animation that scales the text field down
            anim = Animation(
                size_hint=(
                    self.default_size_hint_x + 0.05,
                    self.default_size_hint_y + 0.03,
                ),
                duration=duration,
            )
            anim.start(self)  # start the animation
        else:  # lost focus
            # create an animation that scales the text field up
            anim = Animation(
                size_hint=(self.default_size_hint_x, self.default_size_hint_y),
                duration=duration,
            )
            anim.start(self)  # start the animation

    def display_search_resulst(self, *args):
        search_results = tm.search(self.text)
        app = MDApp.get_running_app()
        app.root.ids.mdlist.clear_widgets()
        for task in search_results:
            app.root.ids.mdlist.add_widget(OneLineListItem(text=task.raw_text))

    def on_text(self, instance, value):
        self.display_search_resulst()


class MainApp(MDApp):

    title = "Done"

    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Dark"

        root = Builder.load_file("gui.kv")
        for task in tm.tasks:
            root.ids.mdlist.add_widget(OneLineListItem(text=task.raw_text))

        return root


if __name__ == "__main__":
    MainApp().run()
