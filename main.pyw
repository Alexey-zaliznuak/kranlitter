import argparse
from enum import Enum
from functools import partial
import json
import logging

import keyboard
import pyperclip


class Modes(str, Enum):
    copy = "copy"
    paste = "paste"
    copy_paste = "copy-paste"

MODES = [e.value for e in Modes]


def setup_logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(asctime)s] - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    with open(log_file, 'w'):
        pass

    return logger


def load_translate(path: str):
    return json.load(open(path, encoding='utf-8'))


def translate(text: str, keys_translate: dict[str, str]) -> str:
    return ''.join([keys_translate.get(s, s) for s in text])


def paste_translated(keys_translate: dict[str, str], mode: Modes):
    """
    Copy translated text to clipboard and paste it.
    """

    logger = logging.getLogger(__name__)

    text = pyperclip.paste()

    new_text = translate(text, keys_translate)

    match mode:
        case Modes.copy:
            pyperclip.copy(new_text)

        case Modes.paste:
            keyboard.write(new_text)

        case Modes.copy_paste:
            pyperclip.copy(new_text)
            keyboard.send("Ctrl+V")

    logger.info("'" + str(text) + "'" + " -> " + "'" + str(new_text) + "'")

def main():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("-h", "--hotkey",  type=str, default = "Ctrl + Alt")
    parser.add_argument("-l", "--log-file", type=str, default = "log.log")
    parser.add_argument("-m", "--mode", type=str, default = "copy-paste", choices=MODES)
    parser.add_argument("-t", "--translate-file", type=str, default = "./translate/en-ru.json")

    args = parser.parse_args()

    log_file = args.log_file
    hotkey = args.hotkey
    translate_file = args.translate_file
    mode = args.mode

    logger = setup_logger(log_file)

    logger.debug(f"Settings: {log_file=} {hotkey=} {mode=} {translate_file=}")

    keys_translate = load_translate(translate_file)

    keyboard.add_hotkey(hotkey, partial(paste_translated, keys_translate, mode))

    keyboard.wait()

if __name__ == "__main__":
    main()
