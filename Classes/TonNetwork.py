import re
import hashlib
import base64

class TonNetwork:
    def __init__(self, lite_client, log):
        self.lc = lite_client
        self.log = log

    def run_method(self, address, method):
        self.log.log(self.__class__.__name__, 3, "Running method '{}' on address '{}'".format(method, address))

        try:
            output = self.lc.exec('runmethod {} {}'.format(address, method))
        except Exception as e:
            self.log.log(self.__class__.__name__, 1, "Could not execute `runmethod`: " + str(e))
            return None

        match = re.search(r'^result:\s*\[(.*)\].*', output, re.MULTILINE)
        if (match):
            res = match.group(1).strip()
            self.log.log(self.__class__.__name__, 3, "Result: '{}'".format(res))
            return res

    def check_block_known(self, blockid=None, blockjson=None):
        if not blockid and blockjson:
            blockid = "({},{},{}):{}:{}".format(
                blockjson['workchain'],
                hex(blockjson['shard'])[3:],
                blockjson['seqno'],
                base64.b64decode(blockjson['root_hash']).hex().upper(),
                base64.b64decode(blockjson['file_hash']).hex().upper()
            )

        self.log.log(self.__class__.__name__, 3, "Checking for presence of block '{}'".format(blockid))

        self.log.log(self.__class__.__name__, 3, "Validate LS connectivity.")
        if not self.lc.last():
            self.log.log(self.__class__.__name__, 1, "Could not validate LS")
            return None

        try:
            stdout = self.lc.exec('gethead {}'.format(blockid), True)
        except Exception as e:
            self.log.log(self.__class__.__name__, 1, "Could not execute `gethead`: {}".format(str(e)))
            return None

        match = re.search(r'^(block header.+).+', stdout, re.MULTILINE)
        if (match):
            self.log.log(self.__class__.__name__, 3, "Block is known!")
            return 1
        else:
            self.log.log(self.__class__.__name__, 3, "Unknown block!")
            return 0

    def get_account_balance(self, account):
        rs = self.lc.exec("getaccount {}".format(account))
        if rs is None:
            return 0
        return self.ng2g(self.lc.parse_output(rs,['balance','grams','value']))

    def get_account_type(self, account):
        types = {
            'd670136510daff4fee1889b8872c4c1e89872ffa1fe58a23a5f5d99cef8edf32': 'wallet v1 r1',
            '2705a31a7ac162295c8aed0761cc6e031ab65521dd7b4a14631099e02de99e18': 'wallet v1 r2',
            'c3b9bb03936742cfbb9dcdd3a5e1f3204837f613ef141f273952aa41235d289e': 'wallet v1 r3',
            'fa44386e2c445f1edf64702e893e78c3f9a687a5a01397ad9e3994ee3d0efdbf': 'wallet v2 r1',
            'd5e63eff6fa268d612c0cf5b343c6674b7312c58dfd9ffa1b536f2014a919164': 'wallet v2 r2',
            '4505c335cb60f221e58448c71595bb6d7c980c01a798b392ebb53d86cb6061dc': 'wallet v3 r1',
            '8a6d73bdd8704894f17d8c76ce6139034b8a51b1802907ca36283417798a219b': 'wallet v3 r2',
            '7ae380664c513769eaa5c94f9cd5767356e3f7676163baab66a4b73d5edab0e5': 'wallet v4',
            'fc8e48ed7f9654ba76757f52cc6031b2214c02fab9e429ffa0340f5575f9f29c': 'wallet hv4',
            '57db8219f434d4aa2f4925fb8225c41414fc1957877c4034fd0a727022c40c52': 'nominator pool v1'
        }

        rs = self.lc.exec("getaccount {}".format(account))
        if rs is None:
            return 0
        data = self.lc.parse_raw_data(self.lc.parse_output(rs,['storage','state','code','value']))
        hash = hashlib.sha256(bytes.fromhex(next(s for s in data if s))).hexdigest()
        if hash in types:
            return types[hash]
        else:
            return None

    def get_validators_load(self, t_start, t_end):
        cmd = 'checkloadall {} {}'.format(t_start, t_end)
        output = self.lc.exec(cmd, wait=10)

        ## Following code base on mytonctrl (https://github.com/ton-blockchain/mytonctrl)
        lines = output.split('\n')
        data = list()
        for line in lines:
            if "val" in line and "pubkey" in line:
                buff = line.split(' ')
                vid = buff[1]
                vid = vid.replace('#', '')
                vid = vid.replace(':', '')
                vid = int(vid)
                pubkey = buff[3]
                pubkey = pubkey.replace(',', '')
                blocksCreated_buff = buff[6]
                blocksCreated_buff = blocksCreated_buff.replace('(', '')
                blocksCreated_buff = blocksCreated_buff.replace(')', '')
                blocksCreated_buff = blocksCreated_buff.split(',')
                masterBlocksCreated = float(blocksCreated_buff[0])
                workBlocksCreated = float(blocksCreated_buff[1])
                blocksExpected_buff = buff[8]
                blocksExpected_buff = blocksExpected_buff.replace('(', '')
                blocksExpected_buff = blocksExpected_buff.replace(')', '')
                blocksExpected_buff = blocksExpected_buff.split(',')
                masterBlocksExpected = float(blocksExpected_buff[0])
                workBlocksExpected = float(blocksExpected_buff[1])
                if masterBlocksExpected == 0:
                    mr = 0
                else:
                    mr = masterBlocksCreated / masterBlocksExpected
                if workBlocksExpected == 0:
                    wr = 0
                else:
                    wr = workBlocksCreated / workBlocksExpected
                r = (mr + wr) / 2
                efficiency = round(r * 100, 2)
                if efficiency > 10:
                    online = True
                else:
                    online = False
                item = dict()
                item["id"] = vid
                item["pubkey"] = pubkey
                item["masterBlocksCreated"] = masterBlocksCreated
                item["workBlocksCreated"] = workBlocksCreated
                item["masterBlocksExpected"] = masterBlocksExpected
                item["workBlocksExpected"] = workBlocksExpected
                item["mr"] = mr
                item["wr"] = wr
                item["efficiency"] = efficiency
                item["online"] = online

                # Get complaint file
                index = lines.index(line)
                nextIndex = index + 2
                if nextIndex < len(lines):
                    nextLine = lines[nextIndex]
                    if "COMPLAINT_SAVED" in nextLine:
                        buff = nextLine.split('\t')
                        item["var1"] = buff[1]
                        item["var2"] = buff[2]
                        item["fileName"] = buff[3]
                data.append(item)
        # end for
        return data
# end class
