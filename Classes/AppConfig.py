import os
import sys
import json
from Libraries.tools import general as gt
from Classes.Logger import Logger

class AppConfig:
    def __init__(self, args):
        self.args = args
        self.log = Logger(args.verbosity)
        self.config = None
        self.ls_config = None
        self.cache_path = None

        if hasattr(self.args, 'config_file'):
            fn = self.args.config_file
            self.log.log(self.__class__.__name__, 3, 'Config file {}'.format(fn))
            if not gt.check_file_exists(fn):
                self.log.log(self.__class__.__name__, 1, "Configuration file does not exist!")
                sys.exit(1)
            try:
                fh = open(fn, 'r')
                self.config = json.loads(fh.read())
                fh.close()
            except Exception as e:
                self.log.log(self.__class__.__name__, 1, "Configuration file read error: {}".format(str(e)))
                sys.exit(1)

            if "liteClient" in self.config:
                fn = self.config["liteClient"]["config"];
                self.log.log(self.__class__.__name__, 3, 'LS Config file {}'.format(fn))
                if not gt.check_file_exists(fn):
                    self.log.log(self.__class__.__name__, 1, "LS Configuration file does not exist!")
                    sys.exit(1)
                try:
                    fh = open(fn, 'r')
                    self.ls_config = json.loads(fh.read())
                    fh.close()
                except Exception as e:
                    self.log.log(self.__class__.__name__, 1, "LS Configuration file read error: {}".format(str(e)))
                    sys.exit(1)

            if "caches" in self.config:
                self.cache_path = "{}/{}.{}".format(self.config["caches"]["path"],self.config["caches"]["prefix"], os.getuid())
                if not os.path.exists(self.cache_path):
                    os.makedirs(self.cache_path)

                if not (os.path.exists(self.cache_path) and os.path.isdir(self.cache_path) and os.access(self.cache_path, os.W_OK)):
                    self.log.log(self.__class__.__name__, 1, "Cache path {} could not be created or is not writable".format(self.cache_path))
                    sys.exit(1)

# end class
