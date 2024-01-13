import glob, os, subprocess, datetime

videos = glob.glob("*.mp4")

i = 0
print("v  <- This is the index")
for v in videos:
  print("[" + str(i+1) + "] " + v)

while(True):
  try:
    user_input = int(input("Please enter index of file you're needing to deshuffle\n>>")) -1
    if(user_input < len(videos) and user_input > 0):
      print("Looks good. File chosen: " + videos[user_input])
    break
  except Exception as e:
    print("Error: " + e)
    continue

while(True):
  try:
    time_format = '%H:%M:%S.fff'
    timestamp = datetime.datetime.strptime(input("Please enter the timestamp on the first moved/shuffled frame after the freeze\n(mpv timestamp <" + time_format + ">)\n>>"), time_format)
    print("Success! Time at " + timestamp.strftime(time_format))
  except Exception as e:
    print("There was an error parsing that timestamp.", e)