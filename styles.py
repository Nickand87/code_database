import qdarkstyle


def get_dark_style():
    """
    Returns the dark style stylesheet.
    """
    stylesheet = qdarkstyle.load_stylesheet()
    custom_rules = """
       QListWidget {
           alternate-background-color: #505050;
       }
       QTableWidget {
            alternate-background-color: #9DA9B5; background-color: #60798B;
        }
       """
    return stylesheet + custom_rules


def get_light_style():
    """
    Returns the light style stylesheet.
    """
    return ""


def apply_style(app, style_name):
    """
    Applies the specified style to the application.
    """
    if style_name == "dark":
        app.setStyleSheet(get_dark_style())
    elif style_name == "light":
        app.setStyleSheet(get_light_style())
    else:
        app.setStyleSheet("")