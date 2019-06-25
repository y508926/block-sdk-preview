#!/usr/bin/env python3

# $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
# Use, reproduction, transfer, publication or disclosure is prohibited except as specifically provided for in your License Agreement with Software AG
import shutil, json, os, subprocess
import blockMetadataGenerator
from pathlib import Path

ENCODING = 'UTF8'
BLOCK_METADATA_EVENT = 'apama.analyticsbuilder.BlockMetadata'
BLOCK_MESSAGES_EVENT = 'apama.analyticsbuilder.BlockMessages'

def add_arguments(parser):
	parser.add_argument('--input', metavar='DIR', type=str, required=True, help='Input directory containing mon files.')
	parser.add_argument('--output', metavar='ZIP_FILE', type=str, required=True, help='The output zip file.')
	parser.add_argument('--cdp', action='store_true', default=False, required=False, help='Package all mon files into a single cdp file.')
	parser.add_argument('--priority', metavar='N', type=int, required=False, help='Priority of the extension.')

def write_evt_file(ext_filed_dir, name, event):
	events_dir = ext_filed_dir / 'events'
	events_dir.mkdir(parents=True, exist_ok=True)
	with open(events_dir / name, mode='w+', encoding='UTF8') as f:
		return f.writelines([event])

def embeddable_json_str(json_str):
	s = json.dumps(json.loads(json_str, encoding=ENCODING), separators=(',', ':'))
	return json.dumps(s)

def gen_messages_evt_file(name, input, ext_files_dir, messages_from_metadata):
	all_msgs = messages_from_metadata.copy()
	msg_to_files = {}
	msg_files = list(input.rglob('messages.json')) + list(input.rglob('*-messages.json'))
	for f in msg_files:
		try:
			data = json.loads(f.read_text(encoding=ENCODING), encoding=ENCODING)
			if not isinstance(data, dict):
				print(f'Skipping JSON file with invalid messages format: {str(f)}')
				continue
			for (k, v) in data.items():
				if k in all_msgs:
					print(f'Message {k} defined multiple times in "{msg_to_files[k]}" and "{f}".')
				else:
					all_msgs[k] = v
					msg_to_files[k] = f
		except:
			print(f'Skipping invalid JSON file: {str(f)}')

	write_evt_file(ext_files_dir, f'{name}_messages.evt',
	               f'{BLOCK_MESSAGES_EVENT}("{name}", "EN", {embeddable_json_str(json.dumps(all_msgs))})')

def createCDP(name, mons, ext_files_dir):
	cmd = [
		os.path.join(os.getenv('APAMA_HOME'), 'bin', 'engine_package'),
		'-u',
		'-o', os.path.join(ext_files_dir, name+'.cdp'),
	] + [str(f) for f in mons]

	subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE).check_returncode()

def run_build_extension(input, output, tmpDir, cdp=False, priority=None, printMsg=False):
	input = Path(input).resolve()
	output = Path(output).resolve()
	tmpDir = Path(tmpDir).resolve()

	name = output.name  # catalog name
	if name.endswith('.zip'):
		name = name[:-4]
		output = output.with_name(name)

	ext_dir = tmpDir / name             # '/' operator on Path object joins them
	ext_files_dir = ext_dir / 'files'
	ext_files_dir.mkdir(parents=True, exist_ok=True)

	# Define priority of the extension if specified
	if priority is not None:
		ext_dir.joinpath('priority.txt').write_text(str(priority), encoding=ENCODING)

	files_to_copy = list(input.rglob('*.evt'))

	# Create CPD or copy mon files to extension directory while maintaining structure
	mons = list(input.rglob('*.mon'))
	if cdp:
		createCDP(name, mons, ext_files_dir)
	else:
		files_to_copy.extend(mons)

	for p in files_to_copy:
		target_file = ext_files_dir / p.relative_to(input)
		target_file.parent.mkdir(parents=True, exist_ok=True)
		shutil.copy2(p, target_file)

	# Generate block metadata
	metadata_tmp_dir = tmpDir / 'metadata'
	(metadata_json_file, messages) = blockMetadataGenerator.run_metadata_generator(input, str(metadata_tmp_dir / name), str(metadata_tmp_dir))

	if metadata_json_file:
		# Write evt file for metadata events
		metadata = Path(metadata_json_file).read_text(encoding=ENCODING)
		write_evt_file(ext_files_dir, f'{name}_metadata.evt', f'{BLOCK_METADATA_EVENT}("{name}", "EN", {embeddable_json_str(metadata)})')

	# Collate all the messages from the messages.json and *-messages.json
	gen_messages_evt_file(name, input, ext_files_dir, messages)

	# Create zip of extension
	shutil.make_archive(output, format='zip', root_dir=ext_dir)
	if printMsg:
		print(f'Created {output}.zip')

def run(args):
	return run_build_extension(args.input, args.output, args.tmpDir, args.cdp, args.priority, printMsg=True)
