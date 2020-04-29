# misc

def sp_translate(text: str):
    return text.encode('ascii', 'ignore').decode('ascii')


def check_n_mkdir(dir: str):
    import os
    dir = dir.replace("\\", "/")
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir
