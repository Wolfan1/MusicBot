#############
# Version: 9/15/2022
#############

import pafy
import urllib.request
import re

def GetURLS(search: str) -> list[str]:
    searchKeyword = search.replace(' ', '+')
    html = urllib.request.urlopen('https://www.youtube.com/results?search_query=' + searchKeyword)
    videoIDS = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    videoURLS = ['https://www.youtube.com/watch?v=' + id for id in videoIDS]
    return videoURLS[0:min(10, len(videoURLS))] # returns at most 6 videos

def GetBest(videoURLS: list[str]):
    # Makes list of pafy objects
    videoList = []
    for url in videoURLS:
        try:
            videoList.append(pafy.new(url))
            if len(videoList) == 3:
                break
        except Exception:
            pass
    '''
    # Sorts videos by length
    videoList.sort(key = lambda video: video.length)
  
    # Calculates scores for clustering
    videoTimes = [video.length for video in videoList]
    videoScores = [len([True for compare in videoTimes if abs(time - compare) <= time/10]) for time in videoTimes]
    maxScore = max(videoScores)
    # Finds best video by viewcount in largest cluster
    clusteredVideos = [videoList[i] for i in range(len(videoScores)) if videoScores[i] == maxScore]
    clusteredVideos.sort(key = lambda video: video.viewcount, reverse = True)
    return clusteredVideos[0]
    '''
    videoTimes = [video.length for video in videoList]
    if abs(videoTimes[1] - videoTimes[2]) < 3 and abs(videoTimes[0] - videoTimes[1]) > 3 and abs(videoTimes[0] - videoTimes[2]) > 3:
        if videoList[1].viewcount > videoList[2].viewcount:
            return videoList[1]
        else:
            return videoList[2]
    return videoList[0]

def youtube_search(argument:str) -> str:
    videoURLS = GetURLS(argument)
    video = GetBest(videoURLS)
    return video.getbestaudio().url, video.title, video.length, "https://www.youtube.com/watch?v=" + video.videoid

if __name__ == '__main__':
    # Makes list of pafy videos based on search
    search = 'i knew you were trouble'
    videoURLS = GetURLS(search)
    bestVideo = GetBest(videoURLS)

    print(bestVideo.title, bestVideo.length, bestVideo.viewcount, bestVideo.watchv_url)
