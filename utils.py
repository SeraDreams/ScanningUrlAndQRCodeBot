from aiogram.utils.helper import Helper, HelperMode, ListItem


class States(Helper):
    mode = HelperMode.snake_case
    URL_STATE = ListItem()
    QR_STATE = ListItem()

