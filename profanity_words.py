"""
Shared profanity word list - curse, sexual, abusive, adultery, f-words, obscene language
Used by both audio_profanity_detector.py and subtitle_processor.py
"""

import csv
from pathlib import Path


# Comprehensive profanity list - curse, sexual, abusive, adultery, f-words, obscene language
# Note: "damn" and variations are NOT included as they are not considered obscene
# Comprehensive profanity list - curse, sexual, abusive, adultery, f-words, obscene language
# Note: soft/romance/common-dialogue terms live in profanity_words_optional_soft.csv
_BUILTIN_PROFANITY_WORDS = {
    'moron',
    'kissass',
    'jerk',
    'fatass',
    'dumb',
    'fuck', 'fucking', 'fucked', 'fucker', 'fuckers', 'fuckin', 'fucka', 'fuckable',
    'fuckass', 'fuckbag', 'fuckbitch', 'fuckbook', 'fuckboy', 'fuckbrain', 'fuckbuddy', 'fuckbutt',
    'fuckd', 'fuckedup', 'fuckersucker', 'fuckface', 'fuckfest', 'fuckfreak', 'fuckfriend', 'fuckhead',
    'fuckheads', 'fuckher', 'fuckhole', 'fuckina', 'fuckings', 'fuckingshitmotherfucker', 'fuckinnuts', 'fuckinright',
    'fuckit', 'fuckknob', 'fuckme', 'fuckmeat', 'fuckmehard', 'fuckmonkey', 'fuckn', 'fucknugget',
    'fucknut', 'fucknuts', 'fucknutt', 'fucknutz', 'fuckoff', 'fuckpig', 'fuckpuppet', 'fuckr',
    'fucks', 'fuckstick', 'fucktard', 'fucktards', 'fucktoy', 'fucktrophy', 'fuckup', 'fuckwad',
    'fuckwhit', 'fuckwhore', 'fuckwit', 'fuckwitt', 'fuckyomama', 'fuckyou', 'fuk', 'fukah',
    'fuken', 'fuker', 'fukin', 'fuking', 'fukk', 'fukkah', 'fukken', 'fukker',
    'fukkin', 'fukking', 'fuks', 'fuktard', 'fuktards', 'fukwhit', 'fukwit', 'fuuck',
    'fux', 'fux0r', 'fuxor', 'fvck', 'fvk', 'fxck', 'shit', 'shitting',
    'shitty', 'shits', 'shitbox', 'shitcan', 'shitdick', 'shite', 'shiteater', 'shited',
    'shitface', 'shitfaced', 'shitfit', 'shitforbrains', 'shitfuck', 'shitfucker', 'shitfull', 'shithapens',
    'shithappens', 'shithead', 'shithouse', 'shiting', 'shitlist', 'shitola', 'shitoutofluck', 'shitstain',
    'shitted', 'shitter', 'bullshit', 'bullshits', 'bullshitted', 'horseshit', 'ass', 'asses',
    'asshole', 'assholes', 'assbag', 'assbagger', 'assbandit', 'assbang', 'assbanged', 'assbanger',
    'assbangs', 'assbite', 'assblaster', 'assclown', 'asscock', 'asscowboy', 'asscracker', 'assface',
    'assfuck', 'assfucker', 'assfukka', 'assgoblin', 'assh0le', 'assh0lez', 'asshat', 'asshead',
    'assho1e', 'assholz', 'asshopper', 'asshore', 'assjacker', 'assjockey', 'asskiss', 'asskisser',
    'assklown', 'asslick', 'asslicker', 'asslover', 'assman', 'assmaster', 'assmonkey', 'assmunch',
    'assmuncher', 'assnigger', 'asspacker', 'asspirate', 'asspuppies', 'assrammer', 'assranger', 'assshit',
    'assshole', 'asssucker', 'asswad', 'asswhole', 'asswhore', 'asswipe', 'asswipes', 'azz',
    'azzhole', 'bigass', 'dumbass', 'dumbasses', 'gassyass', 'gayass', 'bitch', 'bitches',
    'bitching', 'bitchass', 'bitched', 'bitcher', 'bitchers', 'bitchez', 'bitchin', 'bitchslap',
    'bitchtit', 'bitchy', 'biteme', 'dumbbitch', 'nastybitch', 'skankbitch', 'skankybitch', 'bastard',
    'bastards', 'bast', 'bastardo', 'bastardz', 'bassterd', 'bassterds', 'basterds', 'basterdz',
    'bigbastard', 'crap', 'crappy', 'crapola', 'crapper', 'piss', 'pissing', 'pissed',
    'pisser', 'pisses', 'pisshead', 'pissin', 'pissoff', 'dick', 'dicks', 'dickhead',
    'dick pic', 'dick-ish', 'dickbag', 'dickbeater', 'dickbeaters', 'dickbrain', 'dickdipper', 'dickface',
    'dickflipper', 'dickforbrains', 'dickfuck', 'dickheads', 'dickhole', 'dickish', 'dickjuice', 'dickless',
    'dicklick', 'dicklicker', 'dickman', 'dickmilk', 'dickmonger', 'dickpic', 'dickripper', 'dicksipper',
    'dickslap', 'dickslicker', 'dicksucker', 'dickwad', 'dickweasel', 'dickweed', 'dickwhipper', 'dickwod',
    'dickzipper', 'pindick', 'limpdick', 'cock', 'cocks', 'cock-head', 'cock-sucker', 'cockbite',
    'cockblock', 'cockblocker', 'cockburger', 'cockcowboy', 'cockface', 'cockfight', 'cockfucker', 'cockhead',
    'cockholster', 'cockjockey', 'cockknob', 'cockknocker', 'cockknoker', 'cocklicker', 'cocklover', 'cockmaster',
    'cockmongler', 'cockmongruel', 'cockmonkey', 'cockmunch', 'cockmuncher', 'cocknob', 'cocknose', 'cocknugget',
    'cockqueen', 'cockrider', 'cockshit', 'cocksman', 'cocksmith', 'cocksmoker', 'cocksucer', 'cocksuck',
    'cocksucked', 'cocksucker', 'cocksucking', 'cocksucks', 'cocksuka', 'cocksukka', 'cocktease', 'cocky',
    'c0ck', 'c0cks', 'c0cksucker', 'c0k', 'cawk', 'cawks', 'cazzo', 'cok',
    'cokmuncher', 'coksucka', 'kock', 'pussy', 'pussies', 'puss', 'pussie', 'pussycat',
    'pussyeater', 'pussyfucker', 'pussylicker', 'pussylips', 'pussylover', 'pussypounder', 'pusy', 'pu55i',
    'pu55y', 'hotpussy', 'destroyyourpussy', 'cunt', 'cunts', 'cunteyed', 'cuntface', 'cuntfuck',
    'cuntfucker', 'cunthole', 'cunthunter', 'cuntlick', 'cuntlicker', 'cuntlicking', 'cuntrag', 'cuntslut',
    'cuntsucker', 'cuntz', 'cnut', 'cnts', 'cntz', 'cunilingus', 'cunillingus', 'cunn',
    'cunnie', 'cunnilingus', 'cunntt', 'cunny', 'kunilingus', 'kunnilingus', 'kunt', 'kunts',
    'kuntz', 'whore', 'whores', 'asswhore', 'crackwhore', 'fuckwhore', 'nastywhore', 'sexwhore',
    'skankwhore', 'skankywhore', 'slutwhore', 'whorefucker', 'whorehouse', 'camwhore', 'easyslut', 'nastyslut',
    'slut', 'sluts', 'slutt', 'slutting', 'slutty', 'slutwear', 'slutwhore', 'motherfucker',
    'motherfuckers', 'motherfuck', 'motherfucked', 'motherfuckin', 'motherfucking', 'motherfuckings', 'mothafuck', 'mothafucka',
    'mothafuckaz', 'mothafucked', 'mothafucker', 'mothafuckin', 'mothafucking', 'mothafuckings', 'mofo', 'm0f0',
    'm0fo', 'sperm', 'semen', 'cum', 'cum face', 'cum licker', 'cumbubble', 'cumdumpster',
    'cumfest', 'cumguzzler', 'cuming', 'cumjockey', 'cumlickr', 'cumm', 'cummer', 'cummin',
    'cumming', 'cumquat', 'cumqueen', 'cums', 'cumshot', 'cumshots', 'cumslut', 'cumstain',
    'cumsucker', 'cumtart', 'kum', 'kumbubble', 'kumbullbe', 'kumer', 'kummer', 'kumming',
    'kumquat', 'kums', 'jiz', 'jizim', 'jizin', 'jizjuice', 'jizm', 'jizn',
    'jizz', 'jizzd', 'jizzed', 'jizzim', 'jizzin', 'jizzn', 'jizzum', 'jism',
    'jiss', 'jisim', 'sex', 'sexual', 'sexually', 'sexed', 'sexfarm', 'sexhound',
    'sexhouse', 'sexing', 'sexkitten', 'sexpot', 'sexslave', 'sextogo', 'sextoy', 'sextoys',
    'sexwhore', 'sexymoma', 'sexymoma', 'sexy-slim', 'cybersex', 'gay sex', 'gaysex', 'group sex',
    'hardcoresex', 'hotsex', 'livesex', 'phonesex', 'porn', 'pornography', 'pornographic', 'pornflick',
    'pornking', 'porno', 'pornprincess', 'barenaked', 'orgasm', 'orgasmic', 'orga', 'orgasim',
    'orgies', 'orgy', 'goregasm', 'masturbat', 'masturbation', 'masturbating', 'm45terbate', 'ma5terb8',
    'ma5terbate', 'massterbait', 'masstrbait', 'masstrbate', 'mastabate', 'mastabater', 'master-bate', 'masterb8',
    'masterbaiter', 'masterbat', 'masterbat3', 'masterbate', 'masterblaster', 'mastrabator', 'beatoff', 'beatyourmeat',
    'jerk off', 'jerk-off', 'jerk0ff', 'jerked', 'jerkoff', 'j3rk0ff', 'jack off', 'jack-off',
    'jackoff', 'smackthemonkey', 'spankthemonkey', 'ejaculat', 'ejaculation', 'ejackulate', 'ejakulate', 'penis',
    'vagina', 'genital', 'genitals', 'peni5', 'penile', 'penises', 'vaginal', 'breast',
    'breasts', 'boob', 'boobs', 'boobies', 'booby', 'b00b', 'b00bies', 'b00biez',
    'b00bs', 'b00bz', 'booobs', 'boooobs', 'booooobs', 'booooooobs', 'brea5t', 'breastjob',
    'breastlover', 'breastman', 'big breasts', 'big knockers', 'big tits', 'bigbreasts', 'bigtits', 'bitties',
    'dirty pillows', 'knockers', 'mams', 'tits', 'titties', 'tit', 'titbitnipply', 'titfuck',
    'titfucker', 'titfuckin', 'titjob', 'titlicker', 'titlover', 'titty', 'tittie', 'butt',
    'buttock', 'buttocks', 'butt plug', 'butt-pirate', 'buttbang', 'buttcheeks', 'buttface', 'buttfuck',
    'buttfucker', 'buttfuckers', 'butthead', 'butthole', 'buttman', 'buttmuch', 'buttmunch', 'buttmuncher',
    'buttpirate', 'buttplug', 'buttstain', 'buttwipe', 'bigbutt', 'rearend', 'rump', 'nipple',
    'nipplering', 'nipples', 'clit', 'clitface', 'clitfuck', 'clits', 'clitty', 'cl1t',
    'clitoris', 'labia', 'hymen', 'rectum', 'anus', 'scrotum', 'teste', 'testicle',
    'testicles', 'gonad', 'gonads', 'glans', 'foreskin', 'crotch', 'crotchjockey', 'crotchmonkey',
    'crotchrot', 'groin', 'foreplay', 'getiton', 'intercourse', 'sexual intercourse', 'coital', 'coitus',
    'copulate', 'fornicate', 'oral sex', 'anal sex', 'analsex', 'anilingus', 'cunnilingus', 'fellatio',
    'felatio', 'felch', 'felcher', 'felching', 'fellate', 'feltch', 'feltcher', 'feltching',
    'deep throat', 'deep throating', 'deapthroat', 'deepthroat', 'deepthroating', 'blow j', 'blow job', 'blow your l',
    'blow your load', 'blowjob', 'blowjobs', 'givehead', 'hand job', 'handjob', 'footjob', 'rimjob',
    'rimming', 'female squirting', 'femalesquirtin', 'femalesquirting', 'male squirting', 'squirting', 'erotic', 'erotica',
    'eroticism', 'ero', 'earotics', 'auto erotic', 'autoerotic', 'bondage', 'bdsm', 'dominatricks',
    'dominatrics', 'dominatrix', 'dommes', 'masochist', 'masokist', 'sadis', 'sadom', 'fetish',
    'fetishism', 'kinky', 'foot fetish', 'footaction', 'footfetish', 'footfuck', 'footfucker', 'footlicker',
    'footstar', 'stripper', 'threesome', 'threeway', 'foursome', 'gang bang', 'gangbang', 'gangbanged',
    'gangbanger', 'gangbangs', 'double penetration', 'doublepenetration', 'dp action', 'dpaction', 'bareback', 'barely legal',
    'barelylegal', 'creampie', 'pearlnecklace', 'golden shower', 'goldenshower', 'brown shower', 'brown showers', 'dog style',
    'dog-fucker', 'doggie style', 'doggie', 'doggie-style', 'doggiestyle', 'doggin', 'dogging', 'doggy style',
    'doggy-style', 'doggystyle', 'dawgie style', 'doggy', 'dawgie-style', 'cowgirl', 'dildo', 'dildos',
    'dild0', 'dild0s', 'd1ld0', 'd1ldo', 'dilld0', 'dilld0s', 'vibr', 'vibrater',
    'vibrator', 'bullet vibe', 'magicwand', 'fingerbang', 'fingerfood', 'fingerfuck', 'fingerfucked', 'fingerfucker',
    'fingerfuckers', 'fingerfucking', 'fingerfucks', 'fingering', 'fisted', 'fister', 'fistfuck', 'fistfucked',
    'fistfucker', 'fistfuckers', 'fistfucking', 'fistfuckings', 'fistfucks', 'fisting', 'fisty', 'frotting',
    'twerking', 'lapdance', 'queef', 'wetspot', 'adultery', 'turd', 'poop', 'pooper',
    'pooperscooper', 'pooping', 'dookie', 'doodoo', 'caca', 'fart', 'farted', 'farting',
    'fartknocker', 'farty', 'flatulence', 'piss', 'pissing', 'pissed', 'pisser', 'pisses',
    'pisshead', 'pissin', 'pissoff', 'pee', 'peehole', 'pee-pee', 'queer', 'queers',
    'fag', 'fag1t', 'fagbag', 'faget', 'fagfucker', 'fagg', 'fagg1t', 'fagged',
    'fagging', 'faggit', 'faggitt', 'faggot', 'faggotcock', 'faggs', 'fagit', 'fagot',
    'fagots', 'fags', 'fagt', 'fagtard', 'fagz', 'faig', 'faigs', 'faigt',
    'dyke', 'dykes', 'dike', 'lesbain', 'lesbayn', 'lesbin', 'lesbo', 'lesbos',
    'lez', 'lezbe', 'lezbefriends', 'lezbian', 'lezbians', 'lezbo', 'lezbos', 'lezz',
    'lezzian', 'lezzie', 'lezzies', 'lezzo', 'lezzy', 'bulldike', 'bulldyke', 'butchbabes',
    'butchdike', 'butchdyke', 'dixiedike', 'dixiedyke', 'homo', 'hom0', 'h0m0', 'h0mo',
    'homobangers', 'homodumbshit', 'homoey', 'trannie', 'tranny', 'transexual', 'transsexual', 'transvestite',
    'trisexual', 'sissy', 'pansies', 'pansy', 'prostitute', 'hooker', 'hookers', 'brothel',
    'redlight', 'escort', 'escorting', 'prostitution', 'camgirl', 'camboy', 'milf', 'dilf',
    'dirty', 'skank', 'skankfuck', 'skanky', 'slime', 'slimeball', 'slimebucket', 'smut',
    'snatch', 'snatchpatch', 'suck', 'suckdick', 'sucker', 'suckme', 'suckmyass', 'suckmydick',
    'suckmytit', 'suckoff', 'corksucker', 'cocksuck', 'cocksucked', 'cocksucker', 'cocksucking', 'cocksucks',
    'cocksuka', 'cocksukka', 'swallow', 'swallower', 'swalow', 'twat', 'twink', 'twinkie',
    'wank', 'wanker', 'wanking', 'williewanker', 'boner', 'boners', 'hardon', 'stiffy',
    'horny', 'horney', 'horniest', 'horndawg', 'horndog', 'booty', 'wetb', 'wetback',
    'condom', 'trojan', 'lubejob', 'livesex', 'peepshow', 'peepshpw', 'hentai', 'ecchi',
    'futanari', 'futanary', 'lolita', 'xxx', 'explicit', 'obscene', 'lewd', 'sucking',
    'sext', 'sexting', 'prick', 'prickhead', 'pric', 'pube', 'pubic', 'pubiclice',
    'pud', 'pudboy', 'pudd', 'puddboy', 'puke', 'quim', 'schlong', 'screw',
    'screwyou', 'shag', 'shaggin', 'shagging', 'shat', 'spunk', 'spunky', 'stiffy',
    'strapon', 'tampon', 'tinkle', 'tongethruster', 'tonguethrust', 'tonguetramp', 'turd', 'upskirt',
    'vulva', 'willy', 'willie', 'weewee', 'weenie', 'douche', 'douche bag', 'douche-fag',
    'douchebag', 'douchebags', 'douchewaffle', 'douchey', 'd0uch3', 'd0uche', 'douch3', 'duche',
    'dipshit', 'dipstick', 'dipship', 'dumbass', 'dumbasses', 'dumbbitch', 'dumbfuck', 'dumbshit',
    'dumshit', 'dumass', 'fugly', 'mafugly', 'gob', 'gook', 'gook eye', 'gook eyes',
    'gookeye', 'gookeyes', 'gookies', 'gooks', 'gooky', 'g00k', 'hobag', 'ho',
    'hoare', 'hoer', 'hoes', 'hoor', 'hoore', 'hore', 'h00r', 'h0ar',
    'h0r', 'h0re', 'jackass', 'jackhole', 'jackshit', 'knob', 'knobbing', 'knobead',
    'knobed', 'knobend', 'knobhead', 'knobjocky', 'knobjokey', 'knobz', 'lowlife', 'muff',
    'muffdive', 'muffdiver', 'muffindiver', 'mufflikcer', 'perv', 'pimp', 'pimped', 'pimper',
    'pimpjuic', 'pimpjuice', 'pimpsimp', 'popimp', 'poon', 'poontang', 'puntang', 'prick',
    'prickhead', 'pric', 'pube', 'pubic', 'pubiclice', 'pud', 'pudboy', 'pudd',
    'puddboy', 'puke', 'queer', 'queers', 'quim', 'schlong', 'screw', 'screwyou',
    'shag', 'shaggin', 'shagging', 'shat', 'skank', 'skankfuck', 'skanky', 'slime',
    'slimeball', 'slimebucket', 'smut', 'snatch', 'snatchpatch', 'snot', 'spunk', 'spunky',
    'suck', 'suckdick', 'sucker', 'suckme', 'suckmyass', 'suckmydick', 'suckmytit', 'suckoff',
    'swallow', 'swallower', 'swalow', 'tampon', 'tinkle', 'tongethruster', 'tonguethrust', 'tonguetramp',
    'turd', 'twat', 'twink', 'twinkie', 'upskirt', 'vulva', 'wank', 'wanker',
    'wanking', 'williewanker', 'willy', 'willie', 'weewee', 'weenie',
}


# Multi-word phrases used by audio and subtitle detection. These are included
# in the editable CSV so users can remove them without changing Python.
DEFAULT_PROFANITY_PHRASES = {
    'fuck you', 'fuck off', 'fuck this', 'fuck that', 'fuck me', 'fuck her', 'fuck him',
    'shit head', 'shit face', 'shit for brains', 'bull shit', 'bullshit',
    'ass hole', 'asshole', 'dumb ass', 'dumbass', 'smart ass', 'smartass',
    'son of a bitch', 'sonofabitch', 'mother fucker', 'motherfucker',
    'piece of shit', 'dick head', 'dickhead', 'cock sucker', 'cocksucker',
    'piss off', 'screw you', 'screw off',
}

DEFAULT_PROFANITY_WORDS = _BUILTIN_PROFANITY_WORDS | DEFAULT_PROFANITY_PHRASES
PROFANITY_CSV_PATH = Path(__file__).with_name('profanity_words.csv')

# These words are only inappropriate in specific contexts. Keeping the rules
# small and explicit avoids applying uncertain AI classification to hard swear
# words, which must always be filtered when enabled in the CSV.
AMBIGUOUS_CONTEXT_TERMS = {
    'swallow': {
        'cum', 'cumming', 'semen', 'sperm', 'cock', 'cocks', 'dick', 'dicks',
        'penis', 'oral', 'sex', 'sexual', 'blowjob', 'cocksucker', 'deepthroat',
    },
    'swallower': {
        'cum', 'cumming', 'semen', 'sperm', 'cock', 'cocks', 'dick', 'dicks',
        'penis', 'oral', 'sex', 'sexual', 'blowjob', 'cocksucker', 'deepthroat',
    },
    'swalow': {
        'cum', 'cumming', 'semen', 'sperm', 'cock', 'cocks', 'dick', 'dicks',
        'penis', 'oral', 'sex', 'sexual', 'blowjob', 'cocksucker', 'deepthroat',
    },
    'dirty': {
        'sex', 'sexual', 'porn', 'naked', 'nude', 'fuck', 'fucking', 'bitch',
        'whore', 'slut', 'talk', 'joke', 'jokes', 'mind', 'thought', 'thoughts',
    },
}

AMBIGUOUS_CONTEXT_PHRASES = {
    'dirty': {
        'dirty talk', 'talk dirty', 'dirty joke', 'dirty jokes',
        'dirty mind', 'dirty thoughts',
    },
}


def _normalize_context_text(context) -> str:
    if isinstance(context, str):
        text = context
    else:
        text = ' '.join(str(value) for value in context)
    return ' '.join(
        token.strip(".,!?;:'\"()[]{}").lower()
        for token in text.split()
        if token.strip(".,!?;:'\"()[]{}")
    )


def should_filter_word(word: str, context) -> bool:
    """
    Return whether an enabled word should be filtered in the supplied context.

    Non-ambiguous words always return True. Ambiguous words require an explicit
    sexual/offensive context term or phrase.
    """
    normalized_word = word.strip().lower()
    required_terms = AMBIGUOUS_CONTEXT_TERMS.get(normalized_word)
    if required_terms is None:
        return True

    context_text = _normalize_context_text(context)
    context_tokens = set(context_text.split())
    if context_tokens & required_terms:
        return True

    return any(
        phrase in context_text
        for phrase in AMBIGUOUS_CONTEXT_PHRASES.get(normalized_word, set())
    )


def load_profanity_words(csv_path=None):
    """
    Load comma-separated words/phrases from the user-editable CSV.

    An existing empty CSV intentionally enables no default words. If the file
    is missing or unreadable, use the built-in defaults so installs do not fail.
    """
    path = Path(csv_path) if csv_path is not None else PROFANITY_CSV_PATH
    if not path.exists():
        return set(DEFAULT_PROFANITY_WORDS)

    try:
        words = set()
        with path.open('r', encoding='utf-8-sig', newline='') as handle:
            for row in csv.reader(handle):
                for value in row:
                    word = value.strip().lower()
                    if word and not word.startswith('#'):
                        words.add(word)
        return words
    except (OSError, csv.Error, UnicodeError):
        return set(DEFAULT_PROFANITY_WORDS)


# Backward compatibility for modules that import the set directly.
PROFANITY_WORDS = load_profanity_words()

# Optional religious/exclamatory terms. Disabled by default to avoid over-filtering
# normal dialogue (e.g. "Oh my God" in non-offensive contexts).
RELIGIOUS_PROFANITY_WORDS = {
    'god', 'gods', 'goddamn', 'goddamned', 'goddamnit', 'goddammit', 'godammit',
    'jesus', 'christ', 'jeezus',
    'damn', 'damned', 'dammit', 'damnit', 'darn',
    'hell', 'hells',
    'omg', 'omfg',
}


def get_profanity_words(include_religious: bool = False):
    """Return the active profanity word set for detection/filtering."""
    # Reload for each new detector so long-running apps pick up CSV edits.
    words = load_profanity_words()
    if include_religious:
        words |= RELIGIOUS_PROFANITY_WORDS
    return words

