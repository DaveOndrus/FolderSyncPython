import hashlib
import logging
import os
import shutil

from FileInfo import generate_tree

_CHUNK_SIZE = 4096

logger = logging.getLogger()


def sync_source_folder_with_replica_folder(source_location, replica_location):
    if not os.path.exists(replica_location):
        os.makedirs(replica_location)
    if ((hash_directory(source_location) == hash_directory(replica_location) and
            len(compare_directories(source_location, replica_location)) == 0) and
            len(compare_directories(replica_location, source_location)) == 0):
        return "Directories are synchronized"
    else:
        remove_non_source_files(source_location, replica_location)
        source = generate_tree(source_location)
        source.convert_to_relative_path(source_location)
        replica = generate_tree(replica_location)
        replica.convert_to_relative_path(replica_location)

        differences = []
        source.find_differences(replica, differences)
        copy_tagged_files(differences, source_location, replica_location)
        logger.info(f"Replica synchronised with source")


def hash_directory(path):
    md5 = hashlib.md5()
    for root, dirs, files in os.walk(path):
        for names in files:
            file_path = os.path.join(root, names)
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5()
                    for chunk in iter(lambda: f.read(_CHUNK_SIZE), b""):
                        file_hash.update(chunk)
                    md5.update(file_hash.digest())
            except (IOError, OSError):
                pass
    return md5.hexdigest()


def compute_hash(path):
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(_CHUNK_SIZE), b""):
            md5.update(chunk)
    return md5.hexdigest()


def copy_tagged_files(differences, source_path, replica_path):
    ordered_nodes = sorted(differences, key=lambda x: x.is_file, reverse=False)
    for file in ordered_nodes:
        copy_file(file, source_path, replica_path)


def copy_file(file, source_path, replica_path):
    if not file.is_file:
        copy_path = replica_path + remove_prefix(file.abs_path, source_path)
        destination_path = os.path.abspath(copy_path)
        if not os.path.exists(copy_path):
            os.makedirs(copy_path)
            logger.info(f"Created folder {copy_path}")
            if len(file.children) > 0:
                for child in file.children:
                    copy_file(child, source_path, replica_path)
        else:
            shutil.copyfile(file.abs_path, destination_path)
            logger.info(f"Copied folder {file.abs_path}")
    if file.is_file:
        copy_path = replica_path + remove_prefix(file.abs_path, source_path)
        destination_path = os.path.abspath(copy_path)
        shutil.copyfile(file.abs_path, destination_path)
        logger.info(f"Copied file {copy_path}")


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def remove_non_source_files(source_path, replica_path):
    result = compare_directories(source_path, replica_path)
    if len(result) != 0:
        for file_path in result:
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Removed file: {file_path}")
                except OSError as e:
                    logger.info(f"Error: {e} - {file_path}")
            else:
                try:
                    os.rmdir(file_path)
                    logger.info(f"Removed folder: {file_path}")
                except OSError as e:
                    logger.info(f"Error: {e} - {file_path}")


def compare_directories(source_path, replica_path):
    compare_list = []
    for root, dirs, files in os.walk(replica_path):
        for file in files:
            file_path1 = os.path.join(root, file)
            file_path2 = file_path1.replace(replica_path, source_path, 1)
            if not os.path.exists(file_path2):
                compare_list.append(file_path1)
        for d in dirs:
            file_path1 = os.path.join(root, d)
            file_path2 = file_path1.replace(replica_path, source_path, 1)
            if not os.path.exists(file_path2):
                compare_list.append(file_path1)
    return compare_list
