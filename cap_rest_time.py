import argparse
import xml.etree.ElementTree as ET
import datetime

# Create parser
parser = argparse.ArgumentParser(description='Script that limit rests in GPX files to be no more than `MAX_TIME_LIMIT`.')

# Add arguments
parser.add_argument('src_dir', help='directory of the source file')
parser.add_argument('-sc', '--save_copy', action='store_true', help='Save output file as a copy with `copy` appended to filename')
parser.add_argument('-mrt', '--MAX_REST_TIME', type=int, default=45, help='All rest time will be limited to this value (in minutes).')

# Parse arguments
args = parser.parse_args()

# Create xml tree
tree = ET.parse(args.src_dir)

# Find all unique namespaces and convert set to list
namespaces = list({element.tag.split('{')[-1].split('}')[0] for element in tree.iter()})

# Convert list to dict (hard-coded to garmin)
namespaces = {'gpxtpx' if 'garmin' in namespace else '': namespace for namespace in namespaces}

# Register all namespaces to prevent tag corruption during file saving
for k, v in namespaces.items():
    ET.register_namespace(k, v)

# Find all <time> tags
times = tree.findall('.//ns:time', namespaces={'ns': namespaces['']})

# Define variable that tracks critical time indices where time difference exceeds the MAX_TIME_LIMIT
crit_time_indices = []

# Initial loop to find and tag number of tags exceeding MAX_TIME_LIMIT
for i in range(len(times) - 1):
    curr_time = datetime.datetime.strptime(times[i].text, '%Y-%m-%dT%H:%M:%SZ')
    next_time = datetime.datetime.strptime(times[i + 1].text, '%Y-%m-%dT%H:%M:%SZ')
    
    if (next_time - curr_time).seconds // 60 > args.MAX_REST_TIME:
        crit_time_indices.append(i + 1)
        
    
# Modify timestamp based on crit_time_indices
for i in range(len(times)):
    num_shifts = sum([idx <= i for idx in crit_time_indices])
    
    if num_shifts:
        mod_time = datetime.datetime.strptime(times[i].text, '%Y-%m-%dT%H:%M:%SZ') \
                   - datetime.timedelta(minutes=num_shifts * args.MAX_REST_TIME)
        
        times[i].text = mod_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# Save file
if args.save_copy:
    tree.write(args.src_dir.split('.gpx')[0] + '_copy.gpx')
else:
    tree.write(args.src_dir)