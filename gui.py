from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.textfield import MDTextField
from kivy.animation import Animation
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
import func


tm = func.TaskManager("./file.txt")


class AddTaskButton(Button):
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
