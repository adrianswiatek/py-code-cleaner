#!/usr/bin/env python3

from argparse import ArgumentParser
from os import getcwd
from pathlib import Path


class UpdateResult(object):
    def __init__(self, updated_file_path):
        self.updated_file_path = updated_file_path

    @staticmethod
    def updated(file_path):
        return UpdateResult(file_path)

    @staticmethod
    def unchanged():
        return UpdateResult(None)

    def is_updated(self):
        return self.updated_file_path is not None


def parse_arguments():
    parser = ArgumentParser(description="Code cleaner")
    parser.add_argument("-p", "--path", default=getcwd(), required=False, help="Path to root directory")
    parser.add_argument("-f", "--file-type", default="*", required=False, help="Type of file")
    return parser.parse_args()


def make_path(path_arg):
    if "~" not in path_arg:
        return Path(path_arg)

    home_path = str(Path.home())
    return Path(path_arg.replace("~", home_path))


def remove_trailing_whitespaces(file_path):
    def read_content():
        try:
            with open(file_path, 'r') as file:
                original_content = file.read()
                split_content = original_content.split("\n")
                lines_map = map(lambda x: x.rstrip(), split_content)
                updated_content = "\n".join(lines_map)
                return updated_content if original_content != updated_content else None
        except UnicodeDecodeError as _:
            return None

    def write_content(content_to_write):
        with open(file_path, 'w') as file:
            file.write(content_to_write)

    if not file_path.exists():
        return UpdateResult.unchanged()

    content = read_content()

    if content is not None:
        write_content(content)
        return UpdateResult.updated(file_path)
    else:
        return UpdateResult.unchanged()


def print_results(results, paths):
    updated_files = list(filter(lambda x: x.is_updated(), results))

    number_of_files_checked = len(paths)
    number_of_updated_files = len(updated_files)

    if number_of_updated_files:
        print()  # Intentionally left empty

    for updated_file in updated_files:
        print(updated_file.updated_file_path)

    print(f"\nUpdated: {number_of_updated_files}/{number_of_files_checked}")


def should_omit_path(path_to_check):
    if path_to_check.is_dir():
        return True

    blacklist = [".git", ".idea", "venv"]
    str_path = str(path_to_check)

    return any(map(lambda x: x in str_path, blacklist))


def file_paths_for_root_path(root_path, extension):
    paths = root_path.glob(f"**/*.{extension}")
    filtered_file_paths = filter(lambda x: not should_omit_path(x), paths)
    return sorted(filtered_file_paths)


if __name__ == "__main__":
    arguments = parse_arguments()
    path = make_path(arguments.path)

    if path.exists():
        file_paths = file_paths_for_root_path(path, arguments.file_type)

        update_results = []
        for swift_file in file_paths:
            update_results.append(remove_trailing_whitespaces(swift_file))

        print_results(update_results, file_paths)
    else:
        print("Given path does not exist")
