from collections import deque
import time
import json
import requests
import concurrent.futures
import os
from multiprocessing import Manager
import sys
import threading

# Global list: Holds thread_id's of parent threads which have found path.
found_path = []

# Query wikipedia api for links.
# If there is more than 500, send plcontinue value to new query until all links have been fetched
# thread returns as completed when it has gotten every link in its list


def get_links(title, pt):
    global found_path
    pagelist = []
    print()
    if(pt in found_path):
        return []
    S = requests.Session()

    URL = "https://fi.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "links",
        "pllimit": "max"
    }

    R = S.get(url=URL, params=PARAMS)

    DATA = R.json()
    PAGES = DATA["query"]["pages"]
    if(PAGES):
        for k, v in PAGES.items():
            try:
                for l in v["links"]:
                    pagelist.append((l["title"]))
            except:
                return pagelist
        while("continue" in DATA):
            CONT = DATA["continue"]["plcontinue"]
            PARAMS["plcontinue"] = CONT

            R = S.get(url=URL, params=PARAMS)
            DATA = R.json()
            PAGES = DATA["query"]["pages"]

            for k, v in PAGES.items():
                try:
                    for l in v["links"]:
                        pagelist.append((l["title"]))
                except:
                    return pagelist
    return pagelist


def find_shortest_path(start, end):
    '''
    Create managed dictionary to save found paths to nodes.
    Pages we want to visit go into deque.
    Worker objects and results are stored in another dictionary for the time of execution.
    When path is found, add the main (caller of this function) thread id to path_found list
    Base for this search algorithm is from: https://github.com/stong1108/WikiRacer/blob/master/wikiracer.py
    '''
    path = {}
    path[start] = [start]
    Q = deque([start])
    futures_dict = {}
    final_path = []
    global found_path
    # If we havent found the path yet, continue
    while not (threading.get_ident() in found_path):
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            # Pool of workers. Each thread grabs a link, gets links from the page and returns.
            while Q:
                if not (threading.get_ident() in found_path):

                    page = Q.popleft()
                    futures_dict[executor.submit(
                        get_links, page, threading.get_ident())] = page

            for future in concurrent.futures.as_completed(futures_dict):
                # Results are processed after workers have returned.
                try:
                    if(future.result() == -1):
                        break
                    # Get future result and remove that future from dictionary.
                    page = futures_dict[future]
                    links = future.result()
                    futures_dict.pop(future)
                    # Remove redundant links from results
                    # Mainly for .en wikipedia
                    for link in links:
                        if link.startswith("Wikipedia:") or link.startswith("Template:"):
                            continue

                        # if link is our destination, we're done!
                        if link in end:
                            # Save the found path
                            path[link] = path[page] + [link]
                            final_path.append(path[page] + [end])
                            # Add current thread id to path_found list, so workers know to exit
                            if(not threading.get_ident() in found_path):
                                found_path.append(threading.get_ident())

                        # if not, check if we already have a record of the shortest path from the start page to this link- if we don't, we need to record the path and add the link to our queue of pages to explore
                        if (link not in path) and (link != page):
                            path[link] = path[page] + [link]
                            Q.append(link)

                except Exception as e:
                    # If future runs into issue we discard it and move to the next
                    pass

    # When remaining threads in executor have stopped, we can return the result.

    return final_path


def wikiexecutor(s, e):
    global found_path
    ret_list = []

    try:
        start = s.strip().capitalize()
        end = e.strip().capitalize()

        if(not start or not end):
            return ["Error", "Cannot search with empty input :-("]
        if(start == end):
            return ["Error", "Start and end are the same!"]
        # validate that starting & ending page has links
        # this check for end page is bit lazy but we can assume its a valid page if it has atleast some links

        if(len(get_links(start, -1)) == 0 or len(get_links(end, -1)) == 0):

            return ["Error", "Start or end page had no links :-("]

        starttime = time.time()
        path = find_shortest_path(start.capitalize(), end.capitalize())
        # remove thread id from list after completion
        found_path.remove(threading.get_ident())
        endtime = time.time()

    except Exception as e:
        print(e)
    # If something goes wrong when executing wikisearch,
    # error message will be outputted into server console
        return ["Error", e]

    # Some formatting of the return list
    totaltime = (endtime - starttime) % 60
    path_str = "PATH: "
    for n in path[0]:
        path_str += (" ->" + n)
    ret_list.append(path_str)
    ret_list.append(str(totaltime).format("{:.3f}s") + " seconds")

    return ret_list
