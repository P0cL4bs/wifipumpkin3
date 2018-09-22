
import npyscreen
import threading

# npyscreen.disableColor()
class TestApp(npyscreen.NPSApp):
    def main(self):
        F = npyscreen.Form(name="Welcome to Npyscreen", )
        t = F.add(npyscreen.BoxBasic, name="Basic Box:", max_width=30, relx=2, max_height=3)
        t.footer = "This is a footer"

        t1 = F.add(npyscreen.BoxBasic, name="Basic Box:", rely=2, relx=32,
                   max_width=30, max_height=3)
        t1.values = ["dsamdsoa"]
        t2 = F.add(npyscreen.BoxTitle, name="Box Title:", max_height=6)
        t3 = F.add(npyscreen.BoxTitle, name="Box Title2:", max_height=6,
                   scroll_exit=True,
                   contained_widget_arguments={
                       'color': "WARNING",
                       'widgets_inherit_color': True, }
                   )
        t4 = F.add(npyscreen.BoxTitle, name="Box Title2:", max_height=6,
                   scroll_exit=True,
                   contained_widget_arguments={
                       'color': "WARNING",
                       'widgets_inherit_color': True, }
                   )
        t2.entry_widget.scroll_exit = True
        t2.values = ["Hello",
                     "This is a Test",
                     "This is another test",
                     "And here is another line",
                     "And here is another line, which is really very long.  abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz",
                     "And one more."]
        t3.values = t2.values
        t2.values.append("testa")

        F.edit()


class MyTestApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", MainForm())

# This form class defines the display that will be presented to the user.

class MainForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.TitleText, name = "Text:", value= "Hellow World!" )

    def afterEditing(self):
        self.parentApp.setNextForm(None)

class TestApp3(npyscreen.NPSApp):
    def main(self):
        # These lines create the form and populate it with widgets.
        # A fairly complex screen in only 8 or so lines of code - a line for each control.
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        F = npyscreen.ActionFormWithMenus(name="Welcome to Npyscreen", )
        t = F.add(npyscreen.TitleText, name="Text:", )
        fn = F.add(npyscreen.TitleFilename, name="Filename:")
        dt = F.add(npyscreen.TitleDateCombo, name="Date:")
        s = F.add(npyscreen.TitleSlider, out_of=12, name="Slider")
        ml = F.add(npyscreen.MultiLineEdit,
                   value="""try typing here! Mutiline text, press ^R to reformat.\n""",
                   max_height=5, rely=9)
        ms = F.add(npyscreen.TitleSelectOne, max_height=4, value=[1, ], name="Pick One",
                   values=["Option1", "Option2", "Option3"], scroll_exit=True)
        self.ms2 = F.add(npyscreen.TitleMultiSelect, max_height=4, value=[1, ], name="Pick Several",
                    values=["Option1", "Option2", "Option3"], scroll_exit=True)
        # This lets the user play with the Form.
        F.edit()


    def get(self):
        print([self.ms2.values[idx] for idx in self.ms2.value])


class TestApp4(npyscreen.NPSApp):
    def main(self):
        # These lines create the form and populate it with widgets.
        # A fairly complex screen in only 8 or so lines of code - a line for each control.
        F = npyscreen.ActionFormWithMenus(name="Welcome to Npyscreen", )
        f = F.add(npyscreen.TitleFixedText, name="Fixed Text:", value="This is fixed text")
        t = F.add(npyscreen.TitleText, name="Text:", )
        p = F.add(npyscreen.TitlePassword, name="Password:")
        fn = F.add(npyscreen.TitleFilename, name="Filename:")
        dt = F.add(npyscreen.TitleDateCombo, name="Date:")
        cb = F.add(npyscreen.Checkbox, name="A Checkbox")
        s = F.add(npyscreen.TitleSlider, out_of=12, name="Slider")
        ml = F.add(npyscreen.MultiLineEdit,
                   value="""try typing here! Mutiline text, press ^R to reformat.\nPress ^X for automatically created list of menus""",
                   max_height=5, rely=9)
        ms = F.add(npyscreen.TitleSelectOne, max_height=4, value=[1, ], name="Pick One",
                   values=["Option1", "Option2", "Option3"], scroll_exit=True, width=30)
        ms2 = F.add(npyscreen.MultiSelect, max_height=4, value=[1, ],
                    values=["Option1", "Option2", "Option3"], scroll_exit=True, width=20)

        bn = F.add(npyscreen.MiniButton, name="Button", )

        # gd = F.add(npyscreen.SimpleGrid, relx = 42, rely=15, width=20)
        gd = F.add(npyscreen.GridColTitles, relx=42, rely=15, width=40, col_titles=['1', '2', '3', '4'])
        gd.values = []
        for x in range(36):
            row = []
            for y in range(x, x + 36):
                row.append(y)
            gd.values.append(row)

        # This lets the user play with the Form.
        F.edit()

class TestApp2(npyscreen.NPSApp):
    def main(self):
        value_list = [
            "This is the first",
            "This is the second",
            "This is the third",
            "This is the fourth",
        ]
        F = npyscreen.Form(name="Welcome to Npyscreen", )
        t = F.add(npyscreen.MultiLineEditableBoxed,
                  max_height=20,
                  name='List of Values',
                  footer="Press i or o to insert values",
                  values=value_list,
                  slow_scroll=False)

        # This lets the user play with the Form.
        F.edit()


if __name__ == "__main__":
    App = TestApp4()
    App.run()
    print("dfsaoadsmd")
    #App.run()
