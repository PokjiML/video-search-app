import os

videos_list = sorted([f for f in os.listdir('data/videos') if f.endswith('.mp4')])
print(videos_list[:5])

for video_name in videos_list[15:20]:
    print(video_name.split('.')[0])
