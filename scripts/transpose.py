from music21 import *
import os
import sys
import click

@click.command(name='visualize', help=__doc__)
@click.option('--work_path', 'work_path',
              default="F:\music\jigs", show_default=True, help="Path to the music files"
              )
@click.option('--new_root_folder', 'new_root_folder',
              default="jigs-transposed", show_default=True, help="Prefix path to where you want to store your melodies (they will be a stored in a %genre% folder)"
              )
def transpose(work_path, new_root_folder):
	def create_new_path(fold):
		new_fold = fold.replace(root_folder, new_root_folder)
		if not os.path.exists(os.path.split(new_fold)[0]):
			os.mkdir(os.path.split(new_fold)[0])
		if not os.path.exists(new_fold):
			os.mkdir(new_fold)

	def move_to_type_and_corr_dur(transpose_index, current_path):
		create_new_path(current_path)
		s1 = s.transpose(transpose_index)
		counter2 = 1
		s3 = stream.Score()
		for l, l1 in zip(s.recurse(), s1.recurse()):
			if counter2 > 2:
				l1.duration.quarterLength = l.duration.quarterLength
				s3.append(l1)
			counter2 += 1
		new_current_path = current_path.replace(root_folder, new_root_folder)
		s3.write('midi', fp=os.path.join(new_current_path, file))

	root_folder = os.path.split(work_path)[1]

	dic = {'amin': -5, 'bmin': 5, 'cmin': 4, 'dmin': 2,
		   'emin': 0, 'fmin': -1, 'gmin': -3,
		   'amaj': -2, 'bmaj': -4, 'cmaj': -5, 'dmaj': 5,
		   'emaj': 3, 'fmaj': 2, 'gmaj': 0,
		   'ador': -7, 'bdor': 3, 'cdor': 2, 'ddor': 0,
		   'edor': -2, 'fdor': -3, 'gdor': -5,
		   'amix': -2, 'bmix': -4, 'cmix': -5, 'dmix': 5,
		   'emix': 3, 'fmix': 2, 'gmix': 0}
	counter = 1
	for root, dirs, files in os.walk(work_path):
		if not os.path.exists(work_path.replace(root_folder, new_root_folder)):
			os.mkdir(work_path.replace(root_folder, new_root_folder))
		if files:
			counter += 1
			main_path = '\\'.join(root.split('\\')[:3])
			end_path = '\\'.join(root.split('\\')[3:])
			major_path = os.path.join(main_path, 'Major', end_path)
			minor_path = os.path.join(main_path, 'Minor', end_path)
			mix_path = os.path.join(main_path, 'Mixolydian', end_path)
			dor_path = os.path.join(main_path, 'Dorian', end_path)
			acc_path = os.path.join(main_path, 'Accompaniments', end_path)
			for file in files:
				try:
					s = converter.parse(os.path.join(root, file))
				except IndexError:
					os.remove(os.path.join(root, file))
					continue
				# accompaniments
				if len(s.parts) > 1:
					create_new_path(acc_path)
					new_path = acc_path.replace(root_folder, new_root_folder)
					s.write('midi', fp=os.path.join(new_path, file))
					continue
				key = file.split('_')[-1].split('.')[0].lower()
				print(key)
				if 'setting' in key:
					continue
				trans = dic[key]
				# standard midi
				if 'maj' in key:
					move_to_type_and_corr_dur(trans, major_path)
				elif 'min' in key:
					move_to_type_and_corr_dur(trans, minor_path)
				elif 'dor' in key:
					move_to_type_and_corr_dur(trans, dor_path)
				elif 'mix' in key:
					move_to_type_and_corr_dur(trans, mix_path)


if __name__ == '__main__':
	transpose()
