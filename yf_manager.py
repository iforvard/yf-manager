import os
from dataclasses import dataclass
from pathlib import Path

from flet import (
    icons,
    Page,
    Row,
    ElevatedButton,
    GridView,
    TextField,
    colors,
    Text,
    AppBar,
    IconButton,
    Draggable,
    TextButton,
    DragTarget,
    Container,
    AlertDialog,
)
from flet.page import ControlEvent
from loguru import logger

from utils import copy_anything, make_dir, move_dir, delete_anything


@dataclass
class ScreenControls:
    screen_dir: GridView
    back_btn: ElevatedButton
    change_path_btn: ElevatedButton
    path_input: TextField


class YFManagerApp:
    file_icon = icons.FOLDER
    folder_icon = icons.FILE_OPEN
    themes = {
        "dark": ("light", icons.WB_SUNNY_OUTLINED),
        "light": ("dark", icons.BRIGHTNESS_2),
    }
    clipboard = None

    def __init__(self, page: Page):
        self.page = page

        self.top_change_path_btn = ElevatedButton(
            icon=icons.FIND_IN_PAGE,
            on_click=self.open_dir_by_path,
            # related name ScreenControls
            data="top_screen_controls",
        )
        self.bottom_change_path_btn = ElevatedButton(
            icon=icons.FIND_IN_PAGE,
            on_click=self.open_dir_by_path,
            # related name ScreenControls
            data="bottom_screen_controls",
        )
        self.top_back_btn = ElevatedButton(
            icon=icons.ARROW_BACK,
            on_click=self.previous_dir,
            # related name ScreenControls
            data="top_screen_controls",
        )
        self.bottom_back_btn = ElevatedButton(
            icon=icons.ARROW_BACK,
            on_click=self.previous_dir,
            # related name ScreenControls
            data="bottom_screen_controls",
        )
        self.top_create_btn = ElevatedButton(
            icon=icons.CREATE_NEW_FOLDER,
            on_click=self.click_create_dir,
            # related name ScreenControls
            data="top_screen_controls",
        )
        self.bottom_create_btn = ElevatedButton(
            icon=icons.CREATE_NEW_FOLDER,
            on_click=self.click_create_dir,
            # related name ScreenControls
            data="bottom_screen_controls",
        )
        self.top_path_input = TextField(label="/", value="/", expand=1)
        self.bottom_path_input = TextField(label="/", value="/", expand=1)
        self.top_screen_dir = GridView(
            expand=1,
            runs_count=5,
            max_extent=150,
            child_aspect_ratio=1.0,
            spacing=5,
            run_spacing=5,
            # related name ScreenControls
            data="top_screen_controls",
        )
        self.bottom_screen_dir = GridView(
            expand=1,
            runs_count=5,
            max_extent=150,
            child_aspect_ratio=1.0,
            spacing=5,
            run_spacing=5,
            # related name ScreenControls
            data="bottom_screen_controls",
        )
        self.top_drag_target_screen_dir = Container(
            DragTarget(
                group="bottom_screen_controls",
                content=self.top_screen_dir,
                on_accept=self.move_element,
            ),
            expand=1,
        )
        self.bottom_drag_target_screen_dir = Container(
            DragTarget(
                group="top_screen_controls",
                content=self.bottom_screen_dir,
                on_accept=self.move_element,
            ),
            expand=1,
        )
        self.dialog_copy_or_move = AlertDialog(
            modal=True,
            title=Text("Please choose an action"),
            content=Text("Copy or move"),
            actions=[
                TextButton("Copy", icon=icons.COPY, on_click=self.copy_element),
                TextButton("Move", icon=icons.MOVE_UP, on_click=self.copy_element),
                TextButton("Delete", icon=icons.DELETE, on_click=self.copy_element),
                TextButton("Cancel", icon=icons.CANCEL, on_click=self.copy_element),
            ],
        )
        self.dialog_create_dir = AlertDialog(
            modal=True,
            title=Text("Please choose an action"),
            content=Text("Enter folder name"),
            actions=[
                TextField(),
                TextButton("OK", icon=icons.CHECK, on_click=self.create_dir),
                TextButton("Cancel", icon=icons.CANCEL, on_click=self.create_dir),
            ],
        )
        self.dialog_delete_element = AlertDialog(
            modal=True,
            title=Text("Please choose an action"),
            content=Text(),
            actions=[
                TextButton("OK", icon=icons.CHECK, on_click=self.delete_element),
                TextButton("Cancel", icon=icons.CANCEL, on_click=self.delete_element),
            ],
        )
        self.top_screen_controls = ScreenControls(
            screen_dir=self.top_screen_dir,
            back_btn=self.top_back_btn,
            change_path_btn=self.top_change_path_btn,
            path_input=self.top_path_input,
        )
        self.bottom_screen_controls = ScreenControls(
            screen_dir=self.bottom_screen_dir,
            back_btn=self.bottom_back_btn,
            change_path_btn=self.bottom_change_path_btn,
            path_input=self.bottom_path_input,
        )
        self.setup_page()

    def setup_page(self):
        self.page.title = "YF manager"
        self.page.theme_mode = "dark"
        self.update_app_bar()
        self.page.add(
            Row(
                [
                    self.top_path_input,
                    self.top_change_path_btn,
                    self.top_back_btn,
                    self.top_create_btn,
                ]
            )
        )
        self.page.add(self.top_drag_target_screen_dir)
        self.page.add(
            Row(
                [
                    self.bottom_path_input,
                    self.bottom_change_path_btn,
                    self.bottom_back_btn,
                    self.bottom_create_btn,
                ]
            )
        )
        self.page.add(self.bottom_drag_target_screen_dir)
        self.update_screen_dir(self.top_screen_dir, "/")
        self.update_screen_dir(self.bottom_screen_dir, "/")

    def get_dir_elements(self, path: str = "/"):
        """
        Generator of files and folders in directories and their icons
        """
        for element in os.listdir(path=path):
            if os.path.isdir(f"{path}/{element}"):
                yield element, self.file_icon
            else:
                yield element, self.folder_icon

    def get_screen_controls(self, name: str) -> ScreenControls:
        return getattr(self, name)

    def previous_dir(self, event: ControlEvent):
        """
        handler for switching to the previous directory
        example: /usr/bin/ => /usr/
        """
        screen_controls = self.get_screen_controls(event.control.data)
        screen_controls.path_input.value = Path(
            screen_controls.path_input.value
        ).parent.absolute()
        self.change_dir(screen_controls.screen_dir, screen_controls.path_input)

    def open_dir_by_path(self, event: ControlEvent):
        """
        handler try opens the directory at the selected path
        """
        screen_controls = self.get_screen_controls(event.control.data)
        self.change_dir(screen_controls.screen_dir, screen_controls.path_input)

    def change_dir(self, dir_screen: GridView, path_input: TextField):
        """
        If the path exists, update the screen
        """
        if os.path.isdir(path_input.value):
            if str(path_input.value)[-1] != "/":
                path_input.value = f"{path_input.value}/"
            path_input.label = path_input.value
            self.update_screen_dir(dir_screen, path_input.label)

    def click_element(self, event: ControlEvent):
        """
        Click handler for a file or folder on the screen.
        """
        path, name_screen_controls = event.control.data
        screen_controls = self.get_screen_controls(name_screen_controls)
        screen_controls.path_input.value = path
        screen_controls.path_input.label = path
        self.change_dir(screen_controls.screen_dir, screen_controls.path_input)

    def move_element(self, event: ControlEvent):
        """
        Move file or folder between dir_screen
        """
        name_screen_dir_in = event.control.content.data
        screen_controls_in = self.get_screen_controls(name_screen_dir_in)

        src = self.page.get_control(event.data)
        element, name_screen_dir_out = src.content.data
        screen_controls_out = self.get_screen_controls(name_screen_dir_out)

        text = f"Do you want to move, copy '{element}' to '{screen_controls_in.path_input.value}' or delete?"
        logger.info(text)
        self.clipboard = element, screen_controls_in
        self.dialog_manager(self.dialog_copy_or_move, text)

    def click_create_dir(self, event: ControlEvent):
        self.clipboard = event.control.data
        self.dialog_manager(self.dialog_create_dir)

    def delete_element(self, event: ControlEvent):
        logger.info(event.control.text)
        element = self.clipboard
        if event.control.text == "OK":
            delete_anything(element)
        self.dialog_manager(self.dialog_delete_element, is_open=False)
        self.update_all_screens_dir()

    def create_dir(self, event: ControlEvent):
        screen_controls = self.get_screen_controls(str(self.clipboard))
        if event.control.text == "OK":
            make_dir(
                screen_controls.path_input.value,
                self.dialog_create_dir.actions[0].value,
            )
        self.dialog_manager(self.dialog_create_dir, is_open=False)
        self.update_all_screens_dir()

    def dialog_manager(self, dialog, text=None, is_open=True):
        self.page.dialog = dialog
        if text:
            dialog.content = Text(text)
        dialog.open = is_open
        self.page.update()

    def copy_element(self, event: ControlEvent):
        element, screen_controls = self.clipboard
        if event.control.text == "Copy":
            logger.info((element, screen_controls.path_input.label))
            copy_anything(element, screen_controls.path_input.label)
            self.dialog_manager(self.dialog_copy_or_move, is_open=False)
        elif event.control.text == "Move":
            move_dir(element, screen_controls.path_input.label)
            self.dialog_manager(self.dialog_copy_or_move, is_open=False)
        elif event.control.text == "Delete":
            logger.info(event.control.text)
            self.clipboard = element
            self.dialog_manager(self.dialog_copy_or_move, is_open=False)
            self.dialog_manager(
                self.dialog_delete_element,
                text=f"Are you sure you want to delete {element}?",
            )
        self.update_all_screens_dir()

    def update_all_screens_dir(self):
        """
        Update the top and bottom screens to the current path.
        Required after moving, copying, or deleting elements.
        """
        self.update_screen_dir(
            self.top_screen_controls.screen_dir,
            self.top_screen_controls.path_input.value,
        )
        self.update_screen_dir(
            self.bottom_screen_controls.screen_dir,
            self.bottom_screen_controls.path_input.value,
        )

    def update_screen_dir(self, screen_dir: GridView, path: str):
        """
        Update files and folders from a path on the selected screen.
        Add in data TextButton path and related name ScreenControls.
        """
        screen_dir.controls.clear()
        for element in self.get_dir_elements(path):
            screen_dir.controls.append(
                Draggable(
                    group=screen_dir.data,
                    content=TextButton(
                        icon=element[1],
                        icon_color="blue400",
                        text=element[0],
                        data=(f"{path}{element[0]}/", screen_dir.data),
                        on_click=self.click_element,
                    ),
                    content_feedback=TextButton(
                        icon=element[1],
                        text=element[0],
                    ),
                )
            )
        self.page.update()

    def theme_switch(self, event: ControlEvent):
        event.control.icon = self.themes[event.control.data][1]
        event.control.data = self.themes[event.control.data][0]
        event.page.theme_mode = self.themes[event.control.data][0]
        event.page.update()

    def update_app_bar(self):
        self.page.appbar = AppBar(
            # leading=Icon(icons.PALETTE),
            # leading_width=40,
            title=Text("YF manager"),
            center_title=True,
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                IconButton(
                    data="light",
                    icon=icons.WB_SUNNY_OUTLINED,
                    on_click=self.theme_switch,
                ),
            ],
        )
