import qdarkstyle


def dark_style():
    # Load the default dark stylesheet from qdarkstyle
    stylesheet = qdarkstyle.load_stylesheet()

    # Add custom rules for QListWidget
    custom_rules = """
       QListWidget {
           alternate-background-color: #505050;
       }
       """

    # Combine the default stylesheet with the custom rules
    return stylesheet + custom_rules


def light_style():
    # Define or load the light style here
    return ""
