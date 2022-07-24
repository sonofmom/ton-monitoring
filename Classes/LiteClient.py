import subprocess
import time
import os
import signal


class LiteClient:
    def __init__(self, args, config, log):
        self.log = log
        self.config = config
        self.ls_addr = None
        self.ls_key = None
        self.ls_config = None
        if "ls_addr" in args:
            self.ls_addr = args.ls_addr
            self.ls_key = args.ls_key
        else:
            self.ls_config = self.config["config"]

        self.log.log(self.__class__.__name__, 3, 'liteClient binary : {}'.format(self.config["bin"]))
        self.log.log(self.__class__.__name__, 3, 'liteServer address: {}'.format(str(self.ls_addr)))
        self.log.log(self.__class__.__name__, 3, 'liteServer key    : {}'.format(str(self.ls_key)))
        self.log.log(self.__class__.__name__, 3, 'liteServer config : {}'.format(str(self.ls_config)))

    def exec(self, cmd, nothrow = False, wait = None):
        self.log.log(self.__class__.__name__, 3, 'Executing command : {}'.format(cmd))
        if self.ls_addr:
            args = [self.config["bin"],
                    "--addr", self.ls_addr,
                    "--b64", self.ls_key,
                    "--verbosity", "0",
                    "--cmd", cmd]
        else:
            args = [self.config["bin"],
                    "--global-config", self.ls_config,
                    "--verbosity", "0",
                    "--cmd", cmd]

        if nothrow:
            process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     timeout=self.config["timeout"])
            return process.stdout.decode("utf-8")

        success = False
        output = None
        for loop in range(0, self.config["retries"]+1):
            self.log.log(self.__class__.__name__, 3, 'liteServer query attempt {}'.format(loop))
            try:
                start = time.time()
                process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     timeout=self.config["timeout"])
                self.log.log(self.__class__.__name__, 3, 'query runtime: {} seconds'.format(time.time() - start))
                if wait:
                    self.log.log(self.__class__.__name__, 3, 'sleeping for {} seconds'.format(wait))
                    time.sleep(wait)

                output = process.stdout.decode("utf-8")

                if process.returncode == 0:
                    success = True
                    break
                else:
                    continue

            except subprocess.TimeoutExpired as e:
                self.log.log(self.__class__.__name__, 3, 'liteServer query {}sec timeout expired'.format(self.config["timeout"]))
                continue

        if success:
            self.log.log(self.__class__.__name__, 3, 'Command succsesful!')
            return output
        else:
            msg = "LiteClient failure after {} retries".format(loop)
            self.log.log(self.__class__.__name__, 1, msg)
            raise Exception(msg)


    # Based on code by https://github.com/igroman787/mytonctrl
    #
    def parse_output(self, text, path):
        result = None
        if path is None or text is None:
            return None

        if not isinstance(path, list):
            path = [path]

        for idx, element in enumerate(path):
            if ':' not in element:
                element += ':'
            if element not in text:
                break

            start = text.find(element) + len(element)
            count = 0
            bcount = 0
            textLen = len(text)
            end = textLen
            for i in range(start, textLen):
                letter = text[i]
                if letter == '(':
                    count += 1
                    bcount += 1
                elif letter == ')':
                    count -= 1
                if letter == ')' and count < 1:
                    end = i + 1
                    break
                elif letter == '\n' and count < 1:
                    end = i
                    break
            text = text[start:end]
            if count != 0 and bcount == 0:
                text = text.replace(')', '')

            if idx+1 == len(path):
                result = text

        return result
    # end define
# end class
