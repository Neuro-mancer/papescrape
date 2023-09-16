import requests, sys, os, bs4, re


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
        threadNum = getThreadNum(url)
        imagePath = makeThreadDir(threadNum)
        response = getWebPage(url)
        threadDom = bs4.BeautifulSoup(response.text, 'html.parser')
        imageSources = getImageSource(threadDom)
        downloadImages(imageSources, imagePath)

    #else:
        # otherwise list the catalog to /wg/ in human parseable format
        # ask which thread the user wants to scrape papes from


def downloadImages(imageSources, imagePath):
    count = 0
    totalImageCount = len(imageSources)
    for imageSource in imageSources:
        count += 1

        print(imageSource)
        print("Starting image download " + str(count) + " of " + str(totalImageCount) + "...")

        imageResponse = requests.get(imageSource, timeout = 5)
        imageResponse.raise_for_status()

        print("Successful image http get!")

        imageFile = open(os.path.join(imagePath, os.path.basename(imageSource)), 'wb')

        for dataChunk in imageResponse.iter_content(100000):
            imageFile.write(dataChunk)

        imageFile.close()

        print("Image " + str(count) + " of " + str(totalImageCount) + " done!")


def getThreadNum(url):
    pattern = re.compile('thread/([0-9]*$)')
    threadNum = pattern.search(url)

    try:
        return threadNum.group(1)
    except:
        print('Error, invalid thread url supplied\n')
        terminateSript()


def makeThreadDir(threadNum):
    homePath = os.getenv('HOME')
    imagePath = homePath + '/' + 'thread_' + threadNum

    try:
        os.makedirs(imagePath)
        return imagePath
    except:
        print('Error, could not create image directory, it already exists\n')
        downloadAnyway = input('Would you like to download the images anyway? (y/n): ')

        while downloadAnyway.lower() != 'y' and downloadAnyway.lower() != 'n':
            print('Error, invalid input\n')
            print(downloadAnyway.lower() != 'y')
            print(downloadAnyway.lower())
            downloadAnyway = input('Would you like to download the images anyway? (y/n): ')

        if downloadAnyway.lower() == 'y':
            return imagePath
        else:
            terminateScript()


def terminateSript():
    print("Terminating script")
    sys.exit(1)


def getWebPage(url):
    response = requests.get(url, timeout = 5)

    try:
        response.raise_for_status()
        return response
    except Exception as exc:
        print('There was a problem getting the webpage: %s' % (exc))
        terminateScript()


def getImageSource(threadDom):
    imageElements = threadDom.select('.postContainer .file .fileThumb')
    imageSources = []

    for element in imageElements:
        imageSources.append('https:' + element.get('href'))

    return imageSources


if __name__ == '__main__':
    main()
