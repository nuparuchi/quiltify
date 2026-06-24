#quiltify
#turn images into patches of (hopefully) representative two-color patches
########

from PIL import Image
import os
import sys

import random

########
#method:
#read every image from /patches/... and add each and their inverse to a list
#of patches (sorted by brightness)

#create an output image, for each 8x8 pixel patch:
# - determine what brightness we have
# - decide which patch most closely matches the brightness
#   (and similarity, as a tie-breaker)
# - fill that part of the image with that patch

def quiltify(imageName, quilted=False, scale=1, bleach=0, contrast=0,
             similarity=0, quantize=1):
    print("Quilting " + imageName)
    
    #get patches
    patches = [[] for i in range(65)]
    
    for patchName in os.listdir('patches/'):
        if len(patchName) < 5 or patchName[-4:] != '.png':
            continue
        
        patch = Image.open('patches/' + patchName)
        pWidth, pHeight = patch.size

        if pWidth != 8 or pHeight != 8:
            continue

        patchBits = [[1 for i in range(8)] for j in range(8)]
        patchBitsI = [[0 for i in range(8)] for j in range(8)]
        brightness = 64
        for x in range(pWidth):
            for y in range(pHeight):
                r,g,b,a = patch.getpixel((x,y))

                if r == g == b == 0:
                    patchBits[x][y] = 0
                    patchBitsI[x][y] = 1
                    brightness -= 1

        patches[brightness].append(patchBits)
        patches[64 - brightness].append(patchBitsI)

    #for bright in range(65):
    #    print(str(len(patches[bright])) + " of brightness " + str(bright))
    #return True

    #open image and make new image
    im = Image.open(imageName)
    if im.mode != "RGB":
        im = im.convert("RGB")

    height,width = im.size
    height = round(height*scale)
    width = round(width*scale)
    im = im.resize((height,width))
    
    out = Image.new('RGB', ((height - height%8),(width - width%8)))
    #iterate through each patch
    #currently doesn't change stuff too small for a patch
    for x in range(height//8):
        for y in range(width//8):
            #iterate through patch
            #get brightness of this patch
            brightness = 0
            for i in range(8):
                for j in range(8):
                    r,g,b = im.getpixel(((x*8 + i),(y*8 + j)))
                    brightness += ((r+g+b)/(255*3))#*(a/255)
            brightness = round(brightness)
            assert(0 <= brightness <= 64)

            #see if current brightness value has any corresponding patches
            potentialPatches = patches[brightness]

            searchDist = 0
            while len(potentialPatches) == 0:
                #go +/-1 brightness and see if they're also empty
                searchDist += 1
                
                potentialPatches = []
                if brightness - searchDist >= 0:
                    potentialPatches += patches[brightness - searchDist]

                if brightness + searchDist <= 64:
                    potentialPatches += patches[brightness + searchDist]

            #from potentialPatches, find the one that matches the best
            match similarity:
                case 0:
                    #see which patch is most similar to this part of the image
                    chosenPatch = potentialPatches[0]

                    if len(potentialPatches) > 1:
                        #if there's more than one patch,
                        minError = 0
                        #get the error of this patch
                        for i in range(8):
                            for j in range(8):
                                r,g,b = im.getpixel(((x*8 + i),(y*8 + j)))
                                minError += abs(((r+g+b)/(255*3)) - chosenPatch[i][j])

                        for patchI in range(1, len(potentialPatches)):
                            totalError = 0
                            for i in range(8):
                                for j in range(8):
                                    r,g,b = im.getpixel(((x*8 + i),(y*8 + j)))
                                    totalError += abs(((r+g+b)/(255*3)) - potentialPatches[patchI][i][j])
                                        
                            if totalError < minError:
                                minError = totalError
                                chosenPatch = potentialPatches[patchI]

                case 1:
                    #use error squared rather than absolute value of error
                    #maybe faster to calculate? idk maybe we're just shaving
                    #a sign off the front with abs so this is slower
                    chosenPatch = potentialPatches[0]

                    if len(potentialPatches) > 1:
                        #if there's more than one patch,
                        minError = 0
                        #get the error of this patch
                        for i in range(8):
                            for j in range(8):
                                r,g,b = im.getpixel(((x*8 + i),(y*8 + j)))
                                minError += (((r+g+b)/(255*3)) - chosenPatch[i][j])**2

                        for patchI in range(1, len(potentialPatches)):
                            totalError = 0
                            for i in range(8):
                                for j in range(8):
                                    r,g,b = im.getpixel(((x*8 + i),(y*8 + j)))
                                    totalError += (((r+g+b)/(255*3)) - potentialPatches[patchI][i][j])**2

                            if totalError < minError:
                                minError = totalError
                                chosenPatch = potentialPatches[patchI]
                    
                case 2:
                    #randomly select a patch from the ones
                    #with the right brightness
                    chosenPatch = potentialPatches[random.randint(0,
                                            len(potentialPatches)-1)]
                    
                case _:
                    #just take the first patch
                    chosenPatch = potentialPatches[0]

            #copy chosen patch onto image
            ourColors = [[255,255,255,255],[0,0,0,255]]

            #if the quilted setting is enabled
            #the two colors of this patch are taken from
            #the colors of the image at this patch
            if quilted:
                #first get the average brightness of the patch
                patchAvg = 0
                for i in range(8):
                    for j in range(8):
                        r,g,b = im.getpixel(((x*8 + i),(y*8 + j)))
                        patchAvg += (r+g+b)/(255*3)
                        
                patchAvg = patchAvg/64

                #then make the light color the average of the colors lighter
                #than average, and the dark color the average of the colors
                #darker than average
                ourColors[0] = [255*bleach,255*bleach,255*bleach,255]
                colorAmounts = [bleach,bleach]
                for i in range(8):
                    for j in range(8):
                        r,g,b = im.getpixel(((x*8 + i),(y*8 + j)))
                        colorOff = ((r+g+b)/(255*3)) < patchAvg
                        
                        ourColors[colorOff][0] += r
                        ourColors[colorOff][1] += g
                        ourColors[colorOff][2] += b
                        colorAmounts[colorOff] += 1

                #we ought to have at least one light color
                #and one dark color, the only time we wont
                #is if the patch is all one color
                assert(colorAmounts[0] + colorAmounts[1] > 2*(bleach))

                #in that case just make both colors the same
                if colorAmounts[0] == bleach:
                    for m in range(3):
                        ourColors[1][m] = ourColors[1][m]//colorAmounts[1]
                        ourColors[0][m] = ourColors[1][m]

                elif colorAmounts[1] == bleach:
                    for m in range(3):
                        ourColors[0][m] = ourColors[0][m]//colorAmounts[0]
                        ourColors[1][m] = ourColors[0][m]

                else:
                    for m in range(3):
                        ourColors[0][m] = ourColors[0][m]//colorAmounts[0]
                        ourColors[1][m] = ourColors[1][m]//colorAmounts[1]

            if contrast > 0 and ourColors[0] != ourColors[1]:
                raw = [ourColors[1][i] - ourColors[0][i] for i in range(3)]
                diff = [float(i)/sum(raw) for i in raw]
                for i in range(3):
                    ourColors[0][i] += round(diff[i]*contrast)
                    ourColors[1][i] -= round(diff[i]*contrast)

                    ourColors[0][i] = max(0, min(255, ourColors[0][i]))
                    ourColors[1][i] = max(0, min(255, ourColors[1][i]))

            if quantize > 1:
                for i in range(3):
                    ourColors[0][i] -= ourColors[0][i] % quantize
                    ourColors[1][i] -= ourColors[1][i] % quantize
            
            ourColors[0] = tuple(ourColors[0])
            ourColors[1] = tuple(ourColors[1])
            
            for i in range(8):
                for j in range(8):
                    if chosenPatch[i][j]:
                        thisColor = ourColors[0]
                    else:
                        thisColor = ourColors[1]
                    out.putpixel(((x*8 + i), (y*8 + j)), thisColor)

    #name the image and save it
    newName = imageName[:-4] + "-quiltify" + imageName[-4:]
    out.save(newName,quality=100)
    print("Quilted " + imageName)

    return True

thisQuilted = False
thisScale = 1
thisBleach = 0
thisContrast = 0
thisSimilarity = 0
thisQuantize = 1
quiltifyAll = sys.argv[1] == "all"

for arg in sys.argv[2:]:
    match arg.split(':')[0]:
        case "quilted":
            thisQuilted = bool(arg.split(':')[1])
        case "scale":
            thisScale = float(arg.split(':')[1])
        case "bleach":
            thisBleach = float(arg.split(':')[1])
        case "contrast":
            thisContrast = float(arg.split(':')[1])
        case "similarity":
            thisSimilarity = int(arg.split(':')[1])
        case "quantize":
            thisQuantize = int(arg.split(':')[1])
        case _:
            print("Arg not understood: " + arg)

if quiltifyAll:
    for fileName in os.listdir():
        if (len(fileName) < 5 or (fileName[-4:] != '.png' and
                                 fileName[-4:] != '.jpg')
                              or ('quiltify' in fileName)):
            continue
        quiltify(fileName, quilted=thisQuilted, scale=thisScale,
                 bleach=thisBleach, contrast=thisContrast,
                 similarity=thisSimilarity, quantize=thisQuantize)

else:
    quiltify(sys.argv[1], quilted=thisQuilted, scale=thisScale,
             bleach=thisBleach, contrast=thisContrast,
             similarity=thisSimilarity, quantize=thisQuantize)
