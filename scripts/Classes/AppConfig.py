import sys
import json
import Libraries.tools.general as gt
from Classes.Logger import Logger

class AppConfig:
    def __init__(self, args):
        self.args = args
        self.log = Logger(args.verbosity)
        self.config = None
        self.ls_config = None

        if hasattr(self.args, 'config_file'):
            fn = self.args.config_file;
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

# end class
