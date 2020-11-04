from dataclasses import dataclass
import hashlib

class KshParse(Exception):
    pass

DIFFICULTY_SHORTNAMES = {
    'novice': 'NOV',
    'advanced': 'ADV',
    'exhaust': 'EXH',
    'maximum': 'MXM',
    'infinite': 'INF',
    'gravity': 'GRV',
    'heavenly': 'HVN',
    'vivid': 'VVD'
}

KSH_DIFFICULTY_NAMES = {
    'novice': 'Novice',
    'challenge': 'Advanced',
    'extended': 'Exhaust',
    'infinite': 'Maximum'
}

@dataclass
class ChartData:
    charter: str
    difficulty_index: int
    difficulty_name: str
    difficulty_shortname: str

@dataclass
class SongData:
    title: str
    artist: str

MAX_KSH_LENGTH = 1024 * 1024 * 5

def load_ksh(kshFile):
    """ Parse a KSH file, getting the necessary data for DB storage.
    returns: a 3-tuple containing the chart file's SHA-3, the song metadata, and the chart metadata.
    """

    hasher = hashlib.sha3_512()
    contents = kshFile['contents']

    song, chart = parse_ksh_details(kshFile['name'], contents)
    hasher.update(contents.encode('utf-8'))

    return hasher.hexdigest(), song, chart

def parse_ksh_details(kshFilename, kshContents):
    ksh_dict = {}

    for line in kshContents.splitlines():
        if not '=' in line or line.startswith('#'):
            continue

        name, value = line.split('=')
        ksh_dict[name] = value.strip()

    real_difficulty_name = KSH_DIFFICULTY_NAMES[ksh_dict['difficulty']]
    song = SongData(
        ksh_dict['title'],
        ksh_dict['artist']
    )

    chart = ChartData(
        ksh_dict['effect'],
        int(ksh_dict['level']),
        real_difficulty_name,
        DIFFICULTY_SHORTNAMES[real_difficulty_name.lower()]
    )

    return (song, chart)
