import Live, sys
#from _osc.RawConfigParser import RawConfigParser
from configparser import MissingSectionHeaderError, ParsingError, ConfigParser
from collections import OrderedDict
import os
path_join = os.path.join
expanduser = os.path.expanduser
exists = os.path.exists
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from _Framework.SubjectSlot import subject_slot_group
from ._EbiagiComponent import EbiagiComponent

DEFAULT_XCONTROL_ON_THRESHOLD = 33
MIN_XCONTROL_SETTING_LEN = 6
MIDI_MSG_TYPES = {'cc': MIDI_CC_TYPE, 'note': MIDI_NOTE_TYPE}

def handle_xcontrol_and_binding_settings(identifier, parent, logger):
    """ Handles xcontrol and binding settings for self or for the given XT script. """
    s_path = path_join(expanduser('~'), 'nativeKONTROL', 'ClyphX_Pro')
    settings = _parse_config_file(s_path, 'X-Controls.txt', logger)
    if settings:
        parsed_settings = parse_xcontrol_settings(settings, identifier, logger, parent)
        if parsed_settings:
            XControlComponent(parsed_settings, parent)
    # self._setup_bindings(s_path, identifier)

def _parse_config_file(file_path, file_name, logger):
    """ Reads the given config file from the given path and returns a dict of
    the keys and values it contains. """
    file_to_read = path_join(file_path, file_name)
    parser = ConfigParser()
    parser.optionxform = str
    try:
        logger('Attempting to read config %s' % file_to_read)
        parser.read((file_to_read,))
    except ParsingError:
        logger(' -> %s contains parsing errors' % file_name)

    sections = parser.sections()
    file_data = OrderedDict()
    for s in sections:
        for key in parser.options(s):
            value = parser.get(s, key)
            if isinstance(value, list):
                value = (' ').join(value)
            file_data[key] = value.replace('\n', '')
            #logger(' -> %s: %s' % (key, file_data[key]))

    return file_data

def parse_xcontrol_settings(text, identifier, logger, parent):
    """ Returns a dict of xcontrol settings parsed from the text. This ensures that
    each setting is valid and that its associated MIDI message is unique. Note that this
    handles casting to lower case since the settings file is not cast to lower case. """
    x_dict = {}
    for k, v in text.items():
        d = v.split(',')
        if len(d) < MIN_XCONTROL_SETTING_LEN:
            continue
        msg_type = MIDI_MSG_TYPES.get(str(d[0]).lower(), None)
        if msg_type is None:
            continue
        ch = parse_midi_channel(d[1].strip())
        num = parse_midi_value(d[2].strip())
        msg = (msg_type, ch, num)
        if parent.can_register_midi_message(msg, identifier):
            parent.register_midi_message(msg, identifier)
            led_off = parse_midi_value(d[3].strip())
            led_on = parse_midi_value(d[4].strip(), default_value=127)
            x_dict[k] = (msg, led_off, led_on, (',').join(d[5:]).strip())

    return x_dict

def parse_midi_value(num_as_string, default_value=0):
    """ Returns a MIDI value (range 0 - 127) or the given default value. """
    return parse_number(num_as_string, default_value=default_value, min_value=0, max_value=127)

def parse_midi_channel(num_as_string):
    """ Returns a MIDI channel number (0 - 15) or 0 if parse error. """
    return parse_number(num_as_string, default_value=1, min_value=1, max_value=16) - 1

def parse_number(num_as_string, default_value=None, min_value=None, max_value=None, is_float=False):
    """ Parses the given string containing a number and returns the parsed number.
    If a parse error occurs, the default_value will be returned. If a min_value or
    max_value is given, the default_value will be returned if the parsed_value is not
    within range. """
    ret_value = default_value
    try:
        parsed_value = float(num_as_string) if is_float else int(num_as_string)
        if min_value is not None and parsed_value < min_value:
            return ret_value
        if max_value is not None and parsed_value > max_value:
            return ret_value
        ret_value = parsed_value
    except:
        pass

    return ret_value

class XControlComponent(EbiagiComponent):
    """ XControlComponent creates a list of buttons based on the given settings, monitors
    their values and handles triggering their action lists and setting their LED
    state. """

    def __init__(self, settings, parent, *a, **k):
        super(XControlComponent, self).__init__(*a, **k)
        self._parent = parent
        btns = []
        for s in settings.values():
            btn = ButtonElement(True, s[0][0], s[0][1], s[0][2], name=s[3])
            btns.append(btn)

        self.log(btns)

        self._on_button_value.replace_subjects(btns)

    def disconnect(self):
        super(XControlComponent, self).disconnect()
        self._parent = None
        return

    @subject_slot_group('value')
    def _on_button_value(self, value, button):
        self.log(button.name)
        parsed_xcontrol = button.name.split(' ')
        action_def = parsed_xcontrol[0]
        args = None
        if len(parsed_xcontrol) > 1:
            args = parsed_xcontrol[1]
        self._parent.handle_action(action_def, args)
