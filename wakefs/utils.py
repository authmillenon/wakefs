import wakefs.conn

def get_stats(name, location=None):
    fs_connection = wakefs.conn.connection_factory()
    return {               # get from connection or location
            'crc': 0,
            'st_mode': 0,
            'st_ino': 0,
            'st_dev': 0,
            'st_nlink': 0,
            'st_uid': 0,
            'st_gid': 0,
            'st_atime': 0,
            'st_mtime': 0,
            'st_ctime': 0,
        }

