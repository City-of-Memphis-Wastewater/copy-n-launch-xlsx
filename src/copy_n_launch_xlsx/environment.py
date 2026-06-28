
@cache
def is_in_dev_environment():
    if pyhabitat.is_in_git_repo(os.path.dirname(current_file_path)):
        return True
    else:
        return False
