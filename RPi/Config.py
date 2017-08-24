import os.path
import json


class Config(object):

    def __init__(self, path, load_config=True, auto_save=False):
        self.path = path
        self.auto_save = auto_save
        self.not_save = []
        self.not_write = []
        self.option_handlers = dict()
        self.option_types = dict()
        self.save_config = dict()
        if load_config:
            self.load()

    def add_not_save(self, option):
        self.not_save.append(option)

    def add_not_saves(self, options):
        self.not_save.extend(options)

    def add_not_write(self, option):
        self.not_write.append(option)

    def add_not_writes(self, options):
        self.not_write.extend(options)

    def set_option_type(self, option, type_):
        if type_ is not None:
            self.option_types[option] = type_

    def set_option_types(self, options, type_):
        for option in options:
            self.set_option_type(option, type_)

    def set_option_handler(self, option, load_handler, save_handler):
        if not callable(load_handler):
            raise ValueError("load_handler not an function")
        if not callable(save_handler):
            raise ValueError("save_handler not an function")
        self.option_handlers[option] = [load_handler, save_handler]

    def set_default(self, option, default, option_type=None):
        if option not in self.save_config:
            self.save_config[option] = default
        self.set_option_type(option, option_type)

    def get_option(self, option):
        if option in self.save_config:
            return self.save_config[option]
        else:
            return None

    def set_option(self, option, value):
        if option in self.not_write:
            return
        self.save_config[option] = value
        self._save()

    def is_set(self, option):
        return option in self.save_config

    def load(self):
        if not os.path.isfile(self.path):
            self._save(True)
            return

        with open(self.path) as file_:
            load_config = json.load(file_)
            for option, value in load_config.iteritems():
                self.save_config[option] = self.set_save_object(option, value)


    def set_save_object(self, option, value):
        if option in self.option_types.keys():
             return self.option_handlers[self.option_types[option]][0](value)
        else:
            return value

    def get_save_object(self, option):
        if option in self.option_types.keys():
            return self.option_handlers[self.option_types[option]][1](self.get_option(option))
        else:
            return self.get_option(option)

    def _save(self, ignore_autosave=False):
        if not (self.auto_save or ignore_autosave): return

        to_save = dict() #self.save_config.copy()
        for key, value in self.save_config.iteritems():
            if key in self.not_save:
                continue
            to_save[key] = self.get_save_object(key)

        with open(self.path, "w") as file_:
            json.dump(to_save, file_, indent=4, sort_keys=True)

    def save(self):
        self._save(True)