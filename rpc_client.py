import xmlrpc.client
from datetime import datetime
from tqdm import tqdm
import time
import traceback
# python -m pip install tqdm or comment lines: 3 and 71-72

# holds session records, will be later implemented to server side
resultdict = {}


def client():
    print("\t>> Welcome to WikiFinder <<\n")
    while(1):
        print("-------------------------------------------\n")
        print(" > 1. Find new path\n",
              "> 2. Check session results\n",
              "> 0. Exit\n")

        c = input("What would you like to do: ")
        if c.isdigit():

            if (c == '0'):
                print("\nGoodbye :)\n")
                exit(0)
            elif (c == '1'):
                getpath()
            elif (c == '2'):
                results()
        else:
            print("Incorrect input, try again\n")


def results():
    # shows results of session, s.getresults() will be added later so this is just a placeholder
    print("\n-------------------------------------------\n\t>> Current results <<\n")
    if(resultdict):

        for k, v in resultdict.items():
            print(f"{k}. {v[0]} - Time: {v[1]}\n")
    else:
        print("No current records. Go find some wikipaths!\n")


def getpath():
    start = input("Starting page: ")
    end = input("Final page: ")
    print("Starting search, this can take a moment..\n")
    ret_list = s.findpath(start, end)
    if(not ret_list):
        print("Server error :(\n")
        print("Try again!\n")
        return

    elif(ret_list[0] == "Error" and ret_list[1]):
        print(f"Error: {ret_list[1]}\n")
        return
    else:
        if(not resultdict):
            x = 1
        else:
            x = len(resultdict) + 1
        resultdict[x] = ret_list
        print("PATH FOUND!\n")
        print(f">>Result<<\n {ret_list[0]} in {ret_list[1]}\n")


if __name__ == "__main__":
    # Fancy animation + connection check
    print("\nStarting WikiFinder™...")
    for i in tqdm(range(4)):
        time.sleep(0.23)
    print("\n\n")
    try:
        s = xmlrpc.client.ServerProxy('http://127.0.0.1:7999')
        if(s.up(1)):
            client()
    except Exception as e:
        print("\nCannot currently connect to the server, try again later!\n")
        print(e)
