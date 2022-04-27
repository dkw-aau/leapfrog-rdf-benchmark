import sys

# Number of lines
def file_length(file):
    with open(file, 'rb') as f:
        return sum(1 for _ in f)

# Copies a specified number of lines.
def copy_lines(file, line_count, output_file_name):
    with open(file, 'rb') as fi:
        for i in range(line_count):
            with open(output_file_name, 'ab') as fo:
                fo.write(fi.readline())

if len(sys.argv) < 3:
    raise "Size factor of dataset and input dataset file must be given."

num_lines = int(float(sys.argv[1]) * file_length(sys.argv[2]))
copy_lines(sys.argv[2], num_lines, 'resized.nt')
