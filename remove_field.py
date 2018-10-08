import argparse
import xml.etree.ElementTree as ET

def get_namespaces(gpx_dir):
    '''
    Get all unique namespaces for `gpx_dir`.
    '''
    # Create xml tree object
    tree = ET.parse(gpx_dir)
    
    # Find all unique namespaces and convert set to list
    namespaces = list({element.tag.split('{')[-1].split('}')[0] for element in tree.iter()})

    # Convert list to dict (hard-coded to 'garmin')
    namespaces = {'gpxtpx' if 'garmin' in namespace else '': namespace for namespace in namespaces}
    
    return namespaces

def remove_field(gpx_dir, child_key, parent_key):
    # Split namespace and name from xml keys
    parent_ns, parent_name = parent_key.split(':')
    child_ns, child_name =  child_key.split(':')

    # Create xml tree object
    tree = ET.parse(gpx_dir)

    # Get namespaces
    namespaces = get_namespaces(gpx_dir)

    # Register all namespaces to prevent tag corruption during file saving
    for k, v in namespaces.items():
        ET.register_namespace(k, v)

    for parent in tree.findall(f'.//ns:{parent_name}', namespaces={'ns': namespaces[parent_ns]}):
        for child in parent.getchildren():
            if child_name in child.tag:
                parent.remove(child)
                               
    # Write to directory
    tree.write(args.gpx_dir.split('.gpx')[0] + '_mod.gpx')


if __name__ == '__main__':
    # Create argument parser
    parser = argparse.ArgumentParser(description='General purpose script to remove all instance of particular field from gpx file.')

    # Add arguments
    parser.add_argument('gpx_dir', help='Path to gpx file to modify.')
    parser.add_argument('-k', '--key_to_delete', help='The particular xml key to delete. Include namespace if present. (i.e. `namespace`:`key`')
    parser.add_argument('-p', '--parent_key', help='xml key containing key to delete. Include namespace if present.')

    # Parse arguments
    args = parser.parse_args()

    remove_field(gpx_dir=args.gpx_dir, child_key=args.key_to_delete, parent_key=args.parent_key)