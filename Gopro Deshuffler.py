import sys, argparse, os
import glob, datetime, subprocess, time

batch_size = 8

parser = argparse.ArgumentParser(description="Brute forces deshuffling of glitched out GoPro videos.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--input", help="video to deshuffle", required=True)
parser.add_argument("-t", "--timestamp", help="timestamp of frame to begin deshuffling from", required=True)
parser.add_argument("-c", "--count", help="number of frames to start shuffling with", required=False)
parser.add_argument("-s", "--sequence", help="sequence of frames. Requires all numbers inbetween to be included. Eg; 34012", required=False)
parser.add_argument("-r", "--recurse", help="add a number to the frame sequence and run it all again", required=False)
parser.add_argument("-v", "--verbose", help="output ffmpeg stuff", action='store_true')
parser.add_argument("-j", "--join", help="join all existing attempts together", action='store_true')
parser.add_argument("-f", "--finalize", help="fully deshuffle the video from the start timestamp", action='store_true')
args = parser.parse_args()


def throw_bad_arguments(in_str:str):
  print(in_str)
  sys.exit(0)

def check_sequence(in_str:str):
  return False

def join_all(in_list:list, batch = 2):
  # all_outputs = list.sort(glob.glob("deshuffling_attempts/*.mp4"))
  all_outputs = in_list
  joining_filter = ""
  for i in range(0, len(all_outputs)-1):
    joining_filter = joining_filter + f"[{i}:v] [{i}:a] "
  joining_filter = joining_filter + f"concat=n={len(all_outputs)}:v=1:a=1 [v] [a]"
  # Don't ask. I did batch-2 as a quick hack. Changing the index above can break things
  subprocess.call(f"ffmpeg -i {' -i '.join(all_outputs)} -filter_complex \"{joining_filter}\" -map \"[v]\" -map \"[a]\" -nostats -progress ./deshuffling_attempts/batch-{batch-2}.mp4 -y")

def is_linear(in_list:list):
  for i in range(0, len(in_list)-1):

    # print(f'\niteration {i}, list len: {len(in_list)}')
    # print(f'comparing {str(int(in_list[i])+1)} and {str(int(in_list[i+1]))}')
    # print(int(in_list[i])+1 != int(in_list[i+1]))

    if int(in_list[i])+1 != int(in_list[i+1]):
      return False
    i+=1
  return True

if args.sequence and args.count:
  throw_bad_arguments("The Count and Sequence arguments are mutually exclusive! Use just one or the other.")

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

if args.join:
  print("Join (-j) was passed. Only joining existing deshuffling attempts in /deshuffling_attempts/...")
  join_all(sorted(glob.glob("deshuffling_attempts\*.mp4")))
  print("Done!")
  sys.exit()

print(f"Beginning deshuffle for file {file} from {timestamp_str}! Sending the attempt outputs into folder: /deshuffling_attempts/",)
if not os.path.exists("deshuffling_attempts"):
  os.makedirs("deshuffling_attempts")

index = 1
do_permute = True
if args.count:
  sequence = list(map(lambda v : str(v), range(0, int(args.count))))
elif args.sequence:
  print("Sequence was specified. Skipping bruteforce and just encoding that sequence.")
  do_permute = False
  if not "0" in args.sequence:
    pass
    print("Please make the sequence zero based")
    sys.exit(2)
  else:
    sequence = [args.sequence]
else:
  sequence = ['1', '0']

do_one_second = True
if args.finalize and args.sequence:
  do_one_second = False

with open(os.devnull, 'wb') as DEVNULL:
  while(True):
    iteration_try_count = 0
    all_permutations = []
    if do_permute:
      permute(sequence, 0, len(sequence), all_permutations)
    else:
      all_permutations = sequence
    for permutation in all_permutations:
      if do_permute and is_linear(permutation):
        print(f'{" ".join(permutation)} is linear. Skipping.')
        continue
      print(f'Encoding {" ".join(permutation)} as [{iteration_try_count}]')
      command = f"ffmpeg -ss {timestamp_str} {'-t 1s' if do_one_second else ''} -i {file} -vf \"shuffleframes={' '.join(permutation)}\" -c:v h264 -nostats -progress ./deshuffling_attempts/{os.path.splitext(file)[0]}-attempt-{iteration_try_count}-[{''.join(permutation)}].mp4 -y"
      output = DEVNULL
      if args.verbose or args.finalize:
        output = None
        print("\nFFMPEG OUTPUT:\n")
      if iteration_try_count % batch_size:
        subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
      else:
        if do_permute:
          print("Waiting for batch to finish...")
        subprocess.call(command, stdout=output, stderr=subprocess.STDOUT)
        # time.sleep(2)
      iteration_try_count = iteration_try_count + 1
    index = index + 1
    sequence.append(str(index))

    if do_permute:
      print("Joining all of them together...")
      join_all(sorted(glob.glob(".\deshuffling_attempts\*.mp4")), index)

    if args.recurse:
      input("Done. Waiting for next pass...")
    elif do_permute:
      # Did this to hold the command window to refer to the indexes and stuff
      input("Done! Press any key to exit.")
      break
    
sys.exit()