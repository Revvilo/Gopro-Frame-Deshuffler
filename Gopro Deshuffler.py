import sys, argparse, os
import glob, datetime, subprocess, time

batch_size = 8

parser = argparse.ArgumentParser(description="Help msg",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--input", help="video to deshuffle", required=True)
parser.add_argument("-t", "--timestamp", help="timestamp of frame to begin deshuffling from", required=True)
parser.add_argument("-c", "--count", help="number of frames to start shuffling with", required=False)
parser.add_argument("-r", "--recurse", help="add a number to the frame sequence and run it all again", required=False)
args = parser.parse_args()

def is_linear(in_list:list):
  for i in range(0, len(in_list)-1):

    # print(f'\niteration {i}, list len: {len(in_list)}')
    # print(f'comparing {str(int(in_list[i])+1)} and {str(int(in_list[i+1]))}')
    # print(int(in_list[i])+1 != int(in_list[i+1]))

    if int(in_list[i])+1 != int(in_list[i+1]):
      return False
    i+=1
  return True

# Stole this. Learn how it works and appreciate it lmao
def permute(in_list:list, str_start_index, str_len, output_list:list):
  if str_start_index == str_len:
    output_list.append(in_list.copy())
  else:
    for i in range(str_start_index, str_len):
      in_list[str_start_index], in_list[i] = in_list[i], in_list[str_start_index]
      permute(in_list, str_start_index+1, str_len, output_list)
      in_list[str_start_index], in_list[i] = in_list[i], in_list[str_start_index]

time_format = '%H:%M:%S.%f'
try:
  timestamp = datetime.datetime.strptime(args.timestamp+"000", time_format)
  timestamp_str = timestamp.strftime(time_format)[:-3]
except Exception as e:
  print("There was an error parsing that timestamp:", e)
  sys.exit(2)

file = os.path.normpath(args.input)
if not os.path.exists(file):
  print("Unable to find file " + str(file))
  sys.exit(2)

print(f"Beginning deshuffle for file {file} from {timestamp_str}! Sending the attempt outputs into folder: /deshuffling_attempts/",)
if not os.path.exists("deshuffling_attempts"):
  os.makedirs("deshuffling_attempts")

index = 1
if args.count:
  sequence = list(map(lambda v : str(v), range(0, int(args.count))))
else:
  sequence = ['1', '0']
with open(os.devnull, 'wb') as DEVNULL:
  while(True):
    iteration_try_count = 0
    all_permutations = []
    permute(sequence, 0, len(sequence), all_permutations)
    for permutation in all_permutations:
      if is_linear(permutation):
        print(f'{" ".join(permutation)} is linear. Skipping.')
        continue
      print(f'Trying {" ".join(permutation)} as [{iteration_try_count}]')
      command = f"ffmpeg -ss {timestamp_str} -t 1s -i {file} -vf \"shuffleframes={' '.join(permutation)}\" -c:v h264 ./deshuffling_attempts/{os.path.splitext(file)[0]}-unshuffled[{iteration_try_count}].mp4 -y"
      # print(command)
      # subprocess.call(command)
      if iteration_try_count % batch_size:
        subprocess.Popen(command, stdout=DEVNULL, stderr=subprocess.STDOUT)
      else:
        print("Waiting for batch to finish...")
        subprocess.call(command, stdout=DEVNULL, stderr=subprocess.STDOUT)
        # time.sleep(2)
      iteration_try_count = iteration_try_count + 1
    index = index + 1
    sequence.append(str(index))
    print("Joining all of them together...")
    all_outputs = list.sort(glob.glob("deshuffling_attempts/*.mp4"))
    joining_filter = ""
    for i in range(0, len(all_outputs)-1):
      joining_filter = joining_filter + f"[{i}:v] [{i}:a] "
    joining_filter = joining_filter + f"concat=n={len(all_outputs)}:v=1:a=1 [v] [a]"
    # Don't ask. I did index-2 as a quick hack. Changing the index above can break things
    subprocess.call(f"ffmpeg -i {' -i '.join(all_outputs)} -filter_complex \"{joining_filter}\" -map \"[v]\" -map \"[a]\" ./deshuffling_attempts/batch-{index-2}.mp4 -y -progress -nostats", stdout=DEVNULL, stderr=subprocess.STDOUT)
    if args.recurse:
      input("Done. Waiting for next pass...")
    else:
      input("Done! Press any key to exit.")
      break
    
sys.exit()