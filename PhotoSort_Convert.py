import os
import shutil
import json as js

import datetime
import pytz


def quicksort(array):
    if len(array) < 2:
        return array

    low, same, high = [], [], []
    #could just choose middle element as pivot
    pivot = array[int(len(array) / 2)]

    for item in array:
        if item[2] < pivot[2]:
            low.append(item)
        elif item[2] == pivot[2]:
            same.append(item)
        elif item[2] > pivot[2]:
            high.append(item)

    return quicksort(low) + same + quicksort(high)


def sortImageJSON(path):
    images = path + '\Images'
    json = path + '\JSON'
    try:
        os.makedirs(images)
        os.makedirs(json)
    except:
        pass
    if os.path.exists(path):
        for dirpath, dirs, files, in os.walk(path):
            for FILE in files:
                fileName = os.path.splitext(FILE)
                if fileName[1] == '.json':
                    try:
                        shutil.move(os.path.join(dirpath, FILE), json)
                        #print('JSON Added')
                    except: 
                        try:
                            os.makedirs(json + '\\UnsortedJSON')
                        except:
                            pass
                        shutil.move(os.path.join(dirpath, FILE), json + '\\UnsortedJSON')

                elif fileName[1] != '' and fileName[0] != 'Images' and fileName[0] != 'JSON':
                    try:
                        shutil.move(os.path.join(dirpath, FILE), images)
                        #print('Image Added')
                    except:
                        try:
                            os.makedirs(images + '\\UnsortedImages')
                        except:
                            pass
                        shutil.move(os.path.join(dirpath, FILE), images + '\\UnsortedImages')
        return True
    return False


def sortDate(path):
    images = path + '\Images'
    json = path + '\JSON'
    sortedNames = []
    for item in os.listdir(images):
        root = os.path.splitext(item)[0]
        fileType = os.path.splitext(item)[1]
        try:
            jsonObject = js.load(open(json + '\\' + str(item) + '.json'))
            sortedNames.append([item, fileType, jsonObject['photoTakenTime']['timestamp'], jsonObject['photoTakenTime']['formatted']])
        except:
            try:
                os.makedirs(images + '\\UnsortedImages')
            except:
                pass
            shutil.move(os.path.join(images, item), images + '\\UnsortedImages')     
    sortedNames = quicksort(sortedNames)

    for item in sortedNames:
        date = datetime.datetime.strptime(str(item[3])[0:len(str(item[3])) - 7], '%b %d, %Y, %H:%M:%S')
        timeOfDay = str(item[3])[len(str(item[3])) - 6: len(str(item[2])) - 4]
        if timeOfDay == 'PM':
            date += datetime.timedelta(hours = 12)
        else:
            if date.hour == 12:
                date -= datetime.timedelta(hours = 12)
        est = date.astimezone(pytz.timezone('US/Eastern'))
        estOffset = int(str(est)[len(str(est)) - 5:len(str(est)) - 3])
        date -= datetime.timedelta(hours = estOffset)
        item.append(date)
        #print(date)
    digits = len(str(len(sortedNames)))


    for num in range(len(sortedNames)):
        fileNum = ''
        for numZ in range(digits - len(str(num))):
            fileNum += '0'
        try:
            fileNum += str(num)
            date = sortedNames[num][4]
            dateReformat = str(date.strftime('%d')) + str(date.strftime('%b')) + str(date.strftime('%y'))
            newFileName = fileNum + '-' + dateReformat + sortedNames[num][1]
            #print(newFileName)
            os.rename(images + '\\' + sortedNames[num][0], images + '\\' + newFileName)
            
            os.rename(json + '\\' + sortedNames[num][0] + '.json', json + '\\' + newFileName + '.json') 
        except:
            try:
                os.makedirs(json + 'UnsortedJSON')
            except:
                pass
            shutil.move((json + '\\' + sortedNames[num][0] + '.json'), json + '\\UnsortedJSON')
    
def googleDataSort(path):
    sortImageJSON(path)
    sortDate(path)

#this bit actually works well
def generalDataSort(path):
    if os.path.exists(path):
        sortedNames = []
        totalFiles = []
        for dirpath, dirs, files in os.walk(path):
            for fileName in files:
                totalFiles.append([dirpath, fileName])    
        for pair in totalFiles:
            fileName = pair[1]
            dirpath = pair[0]
            root = os.path.splitext(fileName)[0]
            type = os.path.splitext(fileName)[1]
            #print(root)
            #print(type)
            try:
                #sometimes its getmtime or getctime depending on modification or creation
                unixTimestamp = os.path.getctime(dirpath + '\\' + fileName)
                #print(unixTimestamp)
                sortedNames.append([root, type, unixTimestamp, dirpath])
                #print(dirpath)
            except:
                try:
                    os.makedirs(path + '\\UnsortedImages')
                except:
                    pass
                shutil.move(os.path.join(dirpath, fileName), path + '\\UnsortedImages')       
        sortedNames = quicksort(sortedNames)
        for item in sortedNames:
            date = datetime.datetime.fromtimestamp(item[2])
            item.append(date)
        digits = len(str(len(sortedNames)))
        for num in range(len(sortedNames)):
            fileNum = ''
            for numZ in range(digits - len(str(num))):
                fileNum += '0'
            fileNum += str(num)        
            date = sortedNames[num][4]
            dateReformat = str(date.strftime('%d')) + str(date.strftime('%b')) + str(date.strftime('%y'))
            try:
                os.makedirs(path + '\\' + str(date.year))
            except:
                pass
            newFileName = fileNum + '-' + dateReformat + sortedNames[num][1]
            os.rename(sortedNames[num][3] + '\\' + sortedNames[num][0] + sortedNames[num][1], sortedNames[num][3] + '\\' + newFileName)
            shutil.move(os.path.join(sortedNames[num][3], newFileName), path + '\\' + str(date.year))
        return True
    return False
        
    

#need a way to unify google and general usage sort
#differentiate by using 'google' boolean or something
#make this into .exe using pyinstaller
#combine google with general sort by merging json metadata with the files then removing it or something


print('Welcome to Photo Sorter.')
print('------------------------')
cont = True
while cont:
    path = input('Enter File Path Where Photos Exist: ')
    conf = input('Confirm Sorting Of Photos At Path "' + path + '"? (Y/N): ')
    if conf == 'Y' or conf == 'y':
        if generalDataSort(path):
            print('>> Photos Sorted.')
        else:
            print('>> Path Not Found.')
    elif conf == 'N' or conf == 'n':
        print('>> Sorting Terminated.')

    while True:
        ans = input('Continue? (Y/N): ')
        if ans == 'N' or ans == 'n':
            cont = False
            break
        elif ans == 'Y' or ans == 'y':
            print('>> Continuing...')
            break
        else:
            print('>> Invalid Input.')
input('>> Hit Any Key To Close Program.')
