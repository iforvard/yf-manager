import os

import flet
from flet import (
    Page,
    ElevatedButton,
    icons,
    colors,
    Text,
    TextButton,
    AlertDialog,
    ListView,
    Column,
    Row,
    Icon,
    IconButton,
)
from flet.page import ControlEvent


class BaseApp:
    clipboard = None
    file_icon = icons.FILE_OPEN
    folder_icon = icons.FOLDER

    def __init__(self, page: Page):
        self.page = page
        self.dir_tree_btn = ElevatedButton(
            "BTN",
            icon=icons.ARROW_RIGHT,
            icon_color=colors.CYAN,
            on_long_press=self.click_open_dir_tree,
            on_click=self.click_open_dir_tree,
        )
        self.dir_tree = ListView(height=300, width=300)
        self.dialog_dir_tree = AlertDialog(
            modal=True,
            title=Text("Please choose an action"),
            content=Text("Choose a directory"),
            actions=[
                Column(
                    [
                        self.dir_tree,
                        TextButton(
                            "OK", icon=icons.CHECK, on_click=self.change_tree_path
                        ),
                        TextButton(
                            "Cancel", icon=icons.CANCEL, on_click=self.change_tree_path
                        ),
                    ]
                )
            ],
        )

        self.setup_page()

    def click_open_dir_tree(self, event: ControlEvent):
        self.clipboard = event.control.data
        self.dialog_manager(self.dialog_dir_tree)

    def dialog_manager(self, dialog, text=None, is_open=True):
        self.page.dialog = dialog
        if text:
            dialog.content = Text(text)
        dialog.open = is_open
        self.page.update()

    def setup_page(self):
        self.page.title = "YF manager"
        self.page.add(
            self.dir_tree_btn,
            # Row(
            #     [
            #         Column(
            #             [self.dir_tree,
            #              TextButton("Delete", icon=icons.DELETE, on_click=self.change_tree_path),
            #              TextButton("Cancel", icon=icons.CANCEL, on_click=self.change_tree_path), ]
            #         )
            #     ],
            #
            # ),
        )
        self.init_dir_tree()
        self.page.update()

    def change_tree_path(self, event: ControlEvent):
        # element, screen_controls = self.clipboard
        # if event.control.text == "Copy":
        self.dialog_manager(self.dialog_dir_tree, is_open=False)

    def init_dir_tree(self):
        self.dir_tree.controls.clear()
        for item, icon in self.get_dir_elements("/"):
            if icon == self.folder_icon:
                self.dir_tree.controls.append(
                    Row(
                        [
                            Column(
                                [
                                    TextButton(
                                        icon=icon,
                                        icon_color="blue400",
                                        text=item,
                                        on_click=self.click_tree_item,
                                        data=item,

                                    ),
                                    Row(
                                        [
                                            Icon(name=icons.SUBDIRECTORY_ARROW_RIGHT),
                                            TextButton(
                                                icon=icon,
                                                icon_color="blue400",
                                                text=item,
                                                on_click=self.click_tree_item,
                                                data=item,

                                            ),
                                        ]
                                    ),
                                    Row(
                                        [
                                            Icon(),
                                            Icon(name=icons.SUBDIRECTORY_ARROW_RIGHT),
                                            TextButton(
                                                icon=icon,
                                                icon_color="blue400",
                                                text=item,
                                                on_click=self.click_tree_item,
                                                data=item,
                                            ),
                                        ]
                                    )
                                ]
                            )
                            
                        ]
                    ),

                )
        self.page.update()

    def click_tree_item(self, event: ControlEvent):
        print(event.control.data)

    def get_dir_elements(self, path: str = "/"):
        """
        Generator of files and folders in directories and their icons
        """
        for element in os.listdir(path=path):
            if os.path.isdir(f"{path}/{element}"):
                yield element, self.folder_icon
            else:
                yield element, self.file_icon


flet.app(target=BaseApp, port=9000)
