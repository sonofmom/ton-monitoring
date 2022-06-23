import subprocess
import time


class LiteClient:
    def __init__(self, args, config, log):
        self.log = log
        self.config = config
        self.ls_addr = args.ls_addr
        self.ls_key = args.ls_key
        self.log.log(self.__class__.__name__, 3, 'liteClient binary : ' + self.config["bin"])
        self.log.log(self.__class__.__name__, 3, 'liteServer address: ' + self.ls_addr)
        self.log.log(self.__class__.__name__, 3, 'liteServer key    : ' + self.ls_key)

    def exec(self, cmd, nothrow = False, wait = None):
        self.log.log(self.__class__.__name__, 3, 'Executing command : ' + cmd)
        args = [self.config["bin"],
                "--addr", self.ls_addr,
                "--b64", self.ls_key,
                "--verbosity", "0",
                "--cmd", cmd]

        if nothrow:
            process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     timeout=self.config["timeout"])
            return process.stdout.decode("utf-8")

        success = False
        output = None
        for loop in range(0, self.config["retries"]+1):
            try:
                process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     timeout=self.config["timeout"])
                output = process.stdout.decode("utf-8")
                stderr = process.stderr.decode("utf-8")
                if wait:
                    time.sleep(wait)
                if process.returncode == 0:
                    success = True
                    continue

            except subprocess.TimeoutExpired as e:
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
