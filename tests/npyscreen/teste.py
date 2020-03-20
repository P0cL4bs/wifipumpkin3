import npyscreen, curses


class MyTestApp(npyscreen.NPSAppManaged):
    def onStart(self):
        # When Application starts, set up the Forms that will be used.
        # These two forms are persistent between each edit.
        self.addForm("MAIN", MainForm, name="Screen 1", color="IMPORTANT", )
        self.addForm("SECOND", MainForm, name="Screen 2", color="WARNING", )
        # This one will be re-created each time it is edited.
        self.addFormClass("THIRD", MainForm, name="Screen 3", color="CRITICAL", )

    def onCleanExit(self):
        npyscreen.notify_wait("Goodbye!")

    def change_form(self, name):
        # Switch forms.  NB. Do *not* call the .edit() method directly (which
        # would lead to a memory leak and ultimately a recursion error).
        # Instead, use the method .switchForm to change forms.
        self.switchForm(name)

        # By default the application keeps track of every form visited.
        # There's no harm in this, but we don't need it so:
        self.resetHistory()


class MainForm(npyscreen.ActionForm):
    def create(self):
        self.add(npyscreen.TitleText, name="Text:", value="Press ^T to change screens")
        self.title = self.add(npyscreen.FixedText, value="Press ^T to change screens")

        self.add_handlers({"^T": self.change_forms})

    def on_ok(self):
        # Exit the application if the OK button is pressed.
        self.parentApp.switchForm(None)

    def on_cancel(self):
        self.title.value = "Hello 4!"

    def change_forms(self, *args, **keywords):
        if self.name == "Screen 1":
            change_to = "SECOND"
        elif self.name == "Screen 2":
            change_to = "THIRD"
        else:
            change_to = "MAIN"

        # Tell the MyTestApp object to change forms.
        self.parentApp.change_form(change_to)


def main():
    TA = MyTestApp()
    TA.run()


if __name__ == '__main__':
    main()