from .base import Base
import subprocess
import re

def ghc_mod(args):
    cmd = ["stack", "exec", "--", "ghc-mod"] + args
    x = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return x.stdout.decode().splitlines()

def ghc_mod_symbols(module):
    return ghc_mod(["browse", module])

def to_candidates(words):
    return list(map(lambda x: { 'word': x }, words))

class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.rank = 1000
        self.name = "ghc-mod"
        self.mark = "[ghc]"
        self.sorters = ["sorter_rank"]
        self.filetypes = ["haskell"]
        self.min_pattern_length = 1000
        self.input_pattern += r'(^\s*{-#\s*(LANGUAGE|OPTIONS_GHC)\s+\S+'\
                            '|^import\s+(qualified\s+)?[A-Z]\S*'\
                            '|^import\s+(qualified\s+)?[A-Z]\S*\s*\(.*[a-zA-Z_]\S*)$'
        self.ghc_lang_exts = to_candidates(ghc_mod(["lang"]))
        self.ghc_flag_options = to_candidates(ghc_mod(["flag"]))
        self.ghc_modules = to_candidates(ghc_mod(["modules"]))

    def get_complete_position(self, context):
        m = re.search('[a-zA-Z_\-]\S*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        line = context['input']
        f = open("/tmp/hoge", "a")
        # f.write(line)
        if re.search(r'LANGUAGE', line):
            return self.ghc_lang_exts
        elif re.search(r'OPTIONS_GHC', line):
            return self.ghc_flag_options
        elif re.search(r'^import', line):
            m = re.search(r'^import\s+(qualified\s+)?([A-Z]\S*)\s*\(.*[a-zA-Z_]\S*$', line)
            if m:
                module = str(m.group(2))
                return to_candidates(ghc_mod_symbols(module))
            else:
                return self.ghc_modules
        else:
            return []

