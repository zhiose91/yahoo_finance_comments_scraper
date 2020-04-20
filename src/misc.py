# misc

def sp_translate(text):
    return text.encode('ascii', 'ignore').decode('ascii')


def check_n_mkdir(dir):
    import os
    dir = dir.replace("\\", "/")
    if not os.path.exists(dir):
        os.mkdir(dir)
    return dir
