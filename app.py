# 
# -*- coding: utf-8 -*-
# 

import numpy as np
import cv2
import pyglet
import datetime
import threading


countLimit  = 15                # Порог срабатывания тревоги (число обнаруженных белых пикселов)
width       = 120               # Катет квадрата слежения
point1      = (230, 245)        # Положение левого верхнего угла области слежения
winLeft     = 1930              # Смещение окон с видео
saveToFile  = True              # Сохранение снимков в файл



# Запуск веб сервера в отдельном процессе
def clock(interval):
    execfile('admin.py')
th = threading.Thread(target=clock, args=(15,))
th.daemon = True
th.start()




point2 = (point1[0] + width, point1[1] + width)
cap    = cv2.VideoCapture(0)

# начальные значения...
t_minus = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)
t       = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)
t_plus  = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)


# Окна для отображения видео с камеры
winName1 = "Движущиеся объекты"
winName2 = "Исходное видео"
cv2.namedWindow(winName1, cv2.CV_WINDOW_AUTOSIZE)
cv2.namedWindow(winName2, cv2.CV_WINDOW_AUTOSIZE)

# Позиционирование окон
cv2.moveWindow(winName2, 0 + winLeft, 0)
cv2.moveWindow(winName1, 645 + winLeft, 0)


isSignal   = 0
intervalId = 50


# Воспроизводит звуковой сигнал
def buzzer():
    global isSignal
    
    if isSignal == 0:
        isSignal = 100
        
        src = pyglet.media.load('./alarm.wav')
        player = pyglet.media.Player()
        player.queue(src)
        player.volume = 0.3
        player.play()
    return

buzzer()


if cap.isOpened():
    frame = cap.read()


# Сохраняеттекущий кадр в файл
def saveCurrentImage():
    image    = cv2.cvtColor(frame[1], cv2.COLOR_RGB2GRAY)
    filename = './current.png';
    params   = list()
    
    params.append(cv2.cv.CV_IMWRITE_PNG_COMPRESSION)
    params.append(8)

    cv2.rectangle(image, point1, point2, (0,153,204), 2, cv2.CV_AA)
    cv2.imwrite(filename, image, params)
    return

saveCurrentImage()



while(cap.isOpened()):
    frame   = cap.read()
    t_minus = t
    t       = t_plus
    t_plus  = cv2.cvtColor(frame[1], cv2.COLOR_RGB2GRAY)

    if isSignal > 0:
        isSignal = isSignal - 1
    
    # Из сглаженного текущего кадра (t_plus) вычитаем предыдущий (t_minus).
    #t_minus = cv2.GaussianBlur(t_minus, (5,5), 0)
    t_plus  = cv2.GaussianBlur(t_plus, (5,5), 0)
    mask    = cv2.absdiff(t_minus, t_plus);

    # Сравниваем значения полученной разности с некоторым пороговым значением
    retval, mask = cv2.threshold(mask, 25, 255, cv2.THRESH_BINARY)

    # Применяем морфологические операции закрытия и открытия, чтобы избавиться от 
    # движущихся регионов малого размера (шумы камеры)
    kernel          = np.ones((5,5), np.uint8)
    mask            = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask            = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask_min        = cv2.getRectSubPix(mask, (width, width), (point1[0] + width/2, point1[1] + width/2))
    countNonZero    = cv2.countNonZero(mask_min)

    if intervalId > 0:
        intervalId = intervalId - 1
    else:
        intervalId = 1000
        print 'countNonZero = ', countNonZero

    # Если обнаружено движение
    if countNonZero > countLimit:
        print 'motion detected, countNonZero = ', countNonZero

        # Сохранение фотки в файл
        if saveToFile:
            params = list()
            params.append(cv2.cv.CV_IMWRITE_PNG_COMPRESSION)
            params.append(8)
            now = datetime.datetime.now()
            filename = './photos/' + now.strftime("%Y-%m-%d_%H:%M:%S") + '.png';
            cv2.imwrite(filename, frame[1], params)

        # Звуковой сигнал
        buzzer()

    # Картинка 2
    cv2.rectangle(mask, point1, point2, (255,0,0), 2)
    cv2.imshow(winName1, mask)
    
    # Картинка 1
    cv2.rectangle(frame[1], point1, point2, (0,153,204), 2, cv2.CV_AA)
    cv2.imshow(winName2, frame[1])

    # Большие значения задержки позволяют лучше реагировать на медленное движение
    # Для увеличения плавности видео задержку следует уменьшить (оптимальное значение - 25 ms)
    if cv2.waitKey(50) & 0xFF == ord('q'):
        break



cap.release()
cv2.destroyAllWindows()
