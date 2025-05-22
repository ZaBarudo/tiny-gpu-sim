#!/usr/bin/env python3
import os
import argparse
import logging

def clean_optnone(input_dir, output_dir, overwrite=False):
    """
    Process all .ll files in input directory, remove 'optnone' attributes,
    and save to output directory with same directory structure.
    """
    processed_files = 0
    errors = 0

    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if not filename.endswith('.ll'):
                continue

            input_path = os.path.join(root, filename)
            relative_path = os.path.relpath(input_path, input_dir)
            output_path = os.path.join(output_dir, relative_path)

            # Skip if output exists and we're not overwriting
            if not overwrite and os.path.exists(output_path):
                logging.info(f"Skipping existing file: {output_path}")
                continue

            try:
                # Read input file
                with open(input_path, 'r') as infile:
                    content = infile.read()

                # Process content
                modified = content.replace('optnone', '')

                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Write output file
                with open(output_path, 'w') as outfile:
                    outfile.write(modified)
                
                processed_files += 1
                logging.info(f"Processed: {input_path} -> {output_path}")

            except Exception as e:
                errors += 1
                logging.error(f"Failed to process {input_path}: {str(e)}")

    return processed_files, errors

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Remove "optnone" attributes from LLVM IR files in a directory tree')
    parser.add_argument('-i', '--input', required=True,
                        help='Input directory containing LLVM IR files')
    parser.add_argument('-o', '--output', default='cleaned_ir',
                        help='Output directory (default: cleaned_ir)')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Overwrite existing files in output directory')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed processing information')
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=log_level
    )

    # Check input directory exists
    if not os.path.isdir(args.input):
        logging.error(f"Input directory does not exist: {args.input}")
        exit(1)

    # Process files
    processed, errors = clean_optnone(args.input, args.output, args.force)
    
    # Print summary
    logging.info(f"\nProcessing complete")
    logging.info(f"Files processed successfully: {processed}")
    logging.info(f"Files failed: {errors}")
    logging.info(f"Output directory: {os.path.abspath(args.output)}")

    exit(errors)