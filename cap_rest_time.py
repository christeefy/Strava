import argparse
import xml.etree.ElementTree as ET
import datetime

# Create parser
parser = argparse.ArgumentParser(description='Script that limit rests in GPX files to be no more than `MAX_TIME_LIMIT`.')

# Add arguments
parser.add_argument('src_dir', help='directory of the source file')
parser.add_argument('-sc', '--save_copy', action='store_true', help='Save output file as a copy with `mod` appended to filename')
parser.add_argument('-mrt', '--MAX_REST_TIME', type=int, default=45, help='All rest times will be capped at this value (in minutes).')

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

# Initial loop to find and tag number of tags exceeding MAX_TIME_LIMIT
for i in range(len(times) - 1):
    curr_time = datetime.datetime.strptime(times[i].text, '%Y-%m-%dT%H:%M:%SZ')
    next_time = datetime.datetime.strptime(times[i + 1].text, '%Y-%m-%dT%H:%M:%SZ')

    # Calculate time diff
    time_diff = (next_time - curr_time).seconds // 60
    
    if time_diff > args.MAX_REST_TIME:
        next_time -= datetime.timedelta(minutes=time_diff - args.MAX_REST_TIME)
        times[i + 1].text = next_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# Save file
if args.save_copy:
    tree.write(args.src_dir.split('.gpx')[0] + '_mod.gpx')
else:
    tree.write(args.src_dir)