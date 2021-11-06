# -*- coding: utf-8 -*-

"""
|-------------------------------------------------------------- idx file structure------------------------------------------------------------------------------------------|
| 结构             | 字段                    | 偏移(字节)                                      | 大小(字节)                 | 意义           | 值                              |
|-----------------|------------------------|------------------------------------------------|--------------------------|----------------|-----------------------------------|
| Metadata        | magic                  | 0                                              | 4                        | PKG文件标志     | 0x64                               |
|                 | n_files                | 4                                              | 4                        | 文件数目        | <N>                                |
|                 | m_offset               | 8                                              | 4                        | 文件表偏移      | <Metadata_Offset>                  |
|                 | m_size                 | 12                                             | 4                        | 文件表         | L                                  |
|-----------------|------------------------|------------------------------------------------|--------------------------|----------------------------------------------------|
| File Header 1   | file_1_filename_len    | <Metadata_Offset>                              | 2                        | 文件名长度      | <file_1_filename_len>              |
|                 | file_1_filename        | <Metadata_Offset> + 2                          | <file_1_filename_len>    | 文件名         | <file_1_filename in gbk encoding>  |
|                 | file_1_offset          | <Metadata_Offset> + <file_1_filename_len> + 2  | 4                        | 文件偏移       | <file_1_offset>                     |
|                 | file_1_flag            | <Metadata_Offset> + <file_1_filename_len> + 6  | 4                        | 固定标识       | 0x0                                 |
|                 | file_1_original_size   | <Metadata_Offset> + <file_1_filename_len> + 10 | 4                        | 文件原始大小    | <file_1_original_size>             |
|                 | file_1_compressed_size | <Metadata_Offset> + <file_1_filename_len> + 14 | 4                        | 文件压缩后大小  | <file_1_compressed_size>           |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| File Header 2   | ...                                                                                                                                                    |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| ...             | ...                                                                                                                                                    |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| File Header <N> | ...                                                                                                                                                    |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

|-------------------------------------------------------------- pkg file structure---------------------------------------------------------------------------------------- |
| 结构             | 字段                    | 偏移(字节)                                      | 大小(字节)                 | 意义           | 值                                |
|-----------------|------------------------|------------------------------------------------|--------------------------|----------------|----------------------------------|
| File 1          | data                   | <file_1_offset>                                | <file_1_compressed_size> | 文件1的压缩数据     | <file_1_compressed_data>       |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| ...             | ...                                                                                                                                                    |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| File <N>        | ...                                                                                                                                                    |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
"""

import ctypes, struct, zlib, os

class Metadata(ctypes.Structure):
    _fields_ = [
        ("magic", ctypes.c_uint32),
        ("n_files", ctypes.c_uint32),
        ("m_offset", ctypes.c_uint32),
        ("m_size", ctypes.c_uint32)
    ]

def main():
    index_filename = "object.idx"
    pkg_filename = "object.pkg"
    output_dir = "."
    with open(index_filename, "rb") as idx, open(pkg_filename, "rb") as pkg:
        metadata = Metadata.from_buffer_copy(idx.read(16))
        assert metadata.magic == 100
        for i in range(metadata.n_files):
            filename_len, = struct.unpack("H", idx.read(2))
            filename = idx.read(filename_len).decode("gbk")
            flag, = struct.unpack("I", idx.read(4))
            assert flag == 0
            offset, = struct.unpack("I", idx.read(4))
            original_size, = struct.unpack("I", idx.read(4))
            compressed_size, = struct.unpack("I", idx.read(4))
            pkg.seek(offset)
            compressed_data = pkg.read(compressed_size)
            original_data = zlib.decompress(compressed_data)
            assert original_size == len(original_data)
            output_filename = os.path.join(output_dir, filename)
            output_directory_name = os.path.dirname(output_filename)
            if not os.path.exists(output_directory_name):
                os.makedirs(output_directory_name)
            with open(output_filename, "wb") as output:
                output.write(original_data)


if __name__ == '__main__':
    main()