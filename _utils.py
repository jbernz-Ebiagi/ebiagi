import functools
import traceback
import subprocess

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            args[0].log(traceback.format_exc())
    return func

def clear_log_file():
    open('/Users/justin/Library/Preferences/Ableton/Live 10.1.3/Log.txt', 'w').close()

def set_input_routing(track, routing_name):
    for routing in track.available_input_routing_types:
        if routing.display_name == routing_name:
            track.input_routing_type = routing
            return

def set_output_routing(track, routing_name):
    for routing in track.available_output_routing_types:
        if routing.display_name == routing_name:
            track.output_routing_type = routing

def is_empty_midi_clip(clip):
    if clip.is_midi_clip:
        clip.select_all_notes()
        if len(clip.get_selected_notes()) > 0 or clip.has_envelopes:
            return False
    if clip.is_audio_clip:
        return False
    return True

qwerty_order = ['1','2','3','4','5','6','7','8','9','0','-','equal','q','w','e','r','t','y','u','i','o','p','lb','rb','a','s','d','f','g','h','j','k','l','semi','apos','z','x','c','v','b','n','m',',','.','slash']


#########

# def handle_xcontrol_and_binding_settings(self, s_path, identifier=MAIN_ID):
#     """ Handles xcontrol and binding settings for self or for the given XT script. """
#     settings = parse_config_file(s_path, 'X-Controls.txt', self._debug.log)
#     if settings:
#         parsed_settings = parse_xcontrol_settings(settings, identifier)
#         if parsed_settings:
#             if identifier != MAIN_ID:
#                 XControlComponent(self, parsed_settings)
#             else:
#                 self.register_component(XControlComponent(self, parsed_settings))
#     self._setup_bindings(s_path, identifier)

# MIN_XCONTROL_SETTING_LEN = 6
# MIDI_MSG_TYPES = {'cc': MIDI_CC_TYPE, 'note': MIDI_NOTE_TYPE}
# _midi_message_registry = {}

# def parse_number(num_as_string, default_value=None, min_value=None, max_value=None, is_float=False):
#     """ Parses the given string containing a number and returns the parsed number.
#     If a parse error occurs, the default_value will be returned. If a min_value or
#     max_value is given, the default_value will be returned if the parsed_value is not
#     within range. """
#     ret_value = default_value
#     try:
#         parsed_value = float(num_as_string) if is_float else int(num_as_string)
#         if min_value is not None and parsed_value < min_value:
#             return ret_value
#         if max_value is not None and parsed_value > max_value:
#             return ret_value
#         ret_value = parsed_value
#     except:
#         pass

#     return ret_value

# def register_midi_message(message, identifier):
#     """ Registers the given message for the script with the given identifier. """
#     reg = _midi_message_registry.setdefault(identifier, [])
#     reg.append(message)

# def parse_midi_value(num_as_string, default_value=0):
#     """ Returns a MIDI value (range 0 - 127) or the given default value. """
#     return parse_number(num_as_string, default_value=default_value, min_value=0, max_value=127)

# def parse_midi_channel(num_as_string):
#     """ Returns a MIDI channel number (0 - 15) or 0 if parse error. """
#     return parse_number(num_as_string, default_value=1, min_value=1, max_value=16) - 1

# def parse_xcontrol_settings(text, identifier):
#     """ Returns a dict of xcontrol settings parsed from the text. This ensures that
#     each setting is valid and that its associated MIDI message is unique. Note that this
#     handles casting to lower case since the settings file is not cast to lower case. """
#     x_dict = {}
#     for k, v in text.iteritems():
#         d = v.split(',')
#         if len(d) < MIN_XCONTROL_SETTING_LEN:
#             continue
#         msg_type = MIDI_MSG_TYPES.get(to_lower(d[0]), None)
#         if msg_type is None:
#             continue
#         ch = parse_midi_channel(d[1].strip())
#         num = parse_midi_value(d[2].strip())
#         msg = (msg_type, ch, num)
#         if can_register_midi_message(msg, identifier):
#             register_midi_message(msg, identifier)
#             led_off = parse_midi_value(d[3].strip())
#             led_on = parse_midi_value(d[4].strip(), default_value=127)
#             x_dict[k] = (msg, led_off, led_on, (',').join(d[5:]).strip())

#     return x_dict

# def _parse_config_file(file_name, file_path, logger):
#     """ Reads the given config file from the given path and returns a dict of
#     the keys and values it contains. """
#     file_to_read = file_handler.path.join(file_path, file_name)
#     parser = file_handler.parser()
#     parser.optionxform = str
#     try:
#         logger('Attempting to read config %s' % file_to_read)
#         parser.read((file_to_read,))
#     except ParsingError:
#         logger(' -> %s contains parsing errors' % file_name)

#     sections = parser.sections()
#     file_data = OrderedDict()
#     for s in sections:
#         for key in parser.options(s):
#             value = parser.get(s, key)
#             if isinstance(value, list):
#                 value = (' ').join(value)
#             file_data[key] = value.replace('\n', '')
#             logger(' -> %s: %s' % (key, file_data[key]))

#     return file_data

# def _setup_bindings(self, s_path, identifier):
#     """ Sets up and adds the BindingComponent to self or XT script if present. """
#     with exception_guard():
#         from _cxp_bindings.BindingComponent import BindingComponent, BINDING_ACCESSORY_VERSION
#         self.log_message('Successfully imported Bindings Accessory %s for %s' % (
#             BINDING_ACCESSORY_VERSION, identifier))
#         if identifier != MAIN_ID:
#             self._binding_components.append(BindingComponent(s_path, identifier, self._debug.log, self._track_manager))
#         else:
#             self._binding_components.append(self.register_component(BindingComponent(s_path, identifier, self._debug.log, self._track_manager)))

# class XControlComponent(ClyphXComponentBase):
#     """ XControlComponent creates a list of buttons based on the given settings, monitors
#     their values and handles triggering their action lists and setting their LED
#     state. """
#     on_threshold = DEFAULT_XCONTROL_ON_THRESHOLD

#     def __init__(self, parent, settings, *a, **k):
#         super(XControlComponent, self).__init__(*a, **k)
#         self._parent = parent
#         btns = []
#         for s in settings.values():
#             btn = ButtonElement(s[0][0], s[0][1], s[0][2], s[1], s[2], name=s[3])
#             btns.append(btn)
#             btn.turn_off()

#         self._on_button_value.replace_subjects(btns)

#     def disconnect(self):
#         super(XControlComponent, self).disconnect()
#         self._parent = None
#         return

#     @subject_slot_group('value')
#     def _on_button_value(self, value, button):
#         if value == self.on_threshold:
#             return
#         self._parent.handle_action_list_trigger(button, value < self.on_threshold, False)
#         button.set_light(bool(value))

#     def handle_action_list_trigger(self, xtrigger, is_off_trig, reset_seq, _=None):
#         """ Called by xtriggers to trigger their action lists. """
#         if not live_object_is_valid(xtrigger):
#             if self._is_debugging:
#                 self._debug.log('handle_action_list_trigger: invalid xtrigger')
#             return
#         is_xclip = isinstance(xtrigger, Live.Clip.Clip)
#         can_name = is_xclip or isinstance(xtrigger, Live.Scene.Scene)
#         action_list = parse_xtrigger_payload(xtrigger.name, self._user_variables, self._user_macros, is_off_trig, is_xclip=is_xclip)
#         if self._is_debugging:
#             self._debug_handle_action_list_trigger(xtrigger, is_off_trig, reset_seq, action_list)
#         if action_list:
#             if action_list['nature'] in SEQ_TRIGGERS and not is_off_trig:
#                 seq_list = self._lseqs if action_list['nature'] == TriggerNature.LSEQ else self._pseqs
#                 actions = get_actions_for_seq_trigger(seq_list, action_list, xtrigger, reset_seq)
#                 for a in actions:
#                     self._trigger_action(a, xtrigger, is_xclip, can_name, action_list['ident'])

#             else:
#                 self._process_actions(action_list['actions'], xtrigger, is_xclip, can_name, action_list['ident'])