import os


def get_setting(setting_name, default=None, convert=lambda _value: _value or None):
    """
    Returns a setting value: either from ENV, or from Dynaconf.
    If none found, default is used.
    If convert is provided, it converts a value of setting.

    :param setting_name: setting name
    :param default: default value if nothing is found
    :param convert: a converter for a found value
    :return: a value
    """

    value = os.getenv(setting_name)
    if not value:
        try:
            from dynaconf import settings

            value = settings.get(setting_name)
        except ImportError:
            pass

    value = value or default
    return convert(value)
