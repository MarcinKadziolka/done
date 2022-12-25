from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.textfield import MDTextField
import func


tm = func.TaskManager("./file.txt")


class SearchTextInput(MDTextField):
    pass


class MainApp(MDApp):

    title = "KivyMD"

    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Dark"

        root = Builder.load_file("gui.kv")
        for task in tm.tasks:
            root.ids.mdlist.add_widget(OneLineListItem(text=task.raw_task))

        return root


if __name__ == "__main__":
    MainApp().run()
