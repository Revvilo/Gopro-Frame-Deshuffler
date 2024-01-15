import sys, argparse, os
import glob, datetime, subprocess

parser = argparse.ArgumentParser(description="Help msg",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--input", help="video to deshuffle", required=True)
parser.add_argument("-t", "--timestamp", help="timestamp of frame to begin deshuffling from", required=True)
args = parser.parse_args()

# Stole this. Learn how it works and appreciate it lmao
def permute(in_str, str_start_index, str_len):
  if str_start_index == str_len:
    print(str(in_str))
  else:
    for i in range(str_start_index, str_len):
      in_str[str_start_index], in_str[i] = in_str[i], in_str[str_start_index]
      permute(in_str, str_start_index+1, str_len)
      in_str[str_start_index], in_str[i] = in_str[i], in_str[str_start_index]

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
  # sys.exit(2) # ENABLE THIS

print(f"Beginning deshuffle for file {file} from {timestamp_str}! Sending the attempt outputs into folder: /deshuffling_attempts/",)
index = 1
sequence = ['1', '0']
sequence_tried = []
while(True):
  command = f"ffmpeg -ss {timestamp_str} -t {(timestamp + datetime.timedelta(seconds=1)).strftime(time_format)[:-3]} -i {file} -vf \"shuffleframes={' '.join(sequence)}\" -c:v h264 ./deshuffling_attempts/{os.path.splitext(file)[0]}-unshuffled[{index-1}].mp4"
  print(command)
  # subprocess.call(command,shell=True)
  sequence_tried.append(sequence)
  index = index + 1
  
  sequence.append(str(index))

# while(True):
#   try:
#     user_input = int(input("Please enter index of file you're needing to deshuffle\n>>")) -1
#     if(user_input < len(videos) and user_input > 0):
#       print("Looks good. File chosen: " + videos[user_input])
#     break
#   except Exception as e:
#     print("Error: " + e)
#     continue

# while(True):
#   try:
#     time_format = '%H:%M:%S.fff'
#     timestamp = datetime.datetime.strptime(input("Please enter the timestamp on the first moved/shuffled frame after the freeze\n(mpv timestamp <" + time_format + ">)\n>>"), time_format)
#     print("Success! Time at " + timestamp.strftime(time_format))
#   except Exception as e:
#     print("There was an error parsing that timestamp.", e)