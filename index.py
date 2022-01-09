import os
import sys
import time

import mss
import yaml

import numpy as np

import pyautogui
import pygetwindow

from cv2 import cv2
from random import random, randint

from src.logger import logger, logger_map_clicked


# Load config file.
stream = open('config.yaml', 'r')

c = yaml.safe_load(stream)
ct = c['threshold']
ch = c['home']

pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause

cat = """
                                                _
                                               \\`*-.
                                                 )  _`-.
                                                .  : `. .
                                                : _   '  \\
                                                ; *` _.   `*-._
                                                `-.-'          `-.
                                                  ;       `       `.
                                                  :.       .        \\
                                                  .\\  .   :   .-'   .
                                                  '  `+.;  ;  '      :
                                                  :  '  |    ;       ;-.
                                                  ; '   : :`-:     _.`* ;
                                               .*' /  .*' ; .*`- +'  `*'
                                               `*-*   `*-*  `*-*'
=========================================================================
========== 💰 Have I helped you in any way? All I ask is a tip! 🧾 ======
========== ✨ Faça sua boa ação de hoje, manda aquela gorjeta! 😊 =======
=========================================================================
======================== vvv BCOIN BUSD BNB vvv =========================
============== 0xbd06182D8360FB7AC1B05e871e56c76372510dDf ===============
=========================================================================
===== https://www.paypal.com/donate?hosted_button_id=JVYSC6ZYCNQQQ ======
=========================================================================

>>---> Press ctrl + c to kill the bot.

>>---> Some configs can be found in the config.yaml file."""


def add_randomness(n, randomn_factor_size=None):
    """Returns n with randomness
    Parameters:
        n (int): A decimal integer
        randomn_factor_size (int): The maximum value+- of randomness that will be
            added to n

    Returns:
        int: n with randomness
    """
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size

    if random_factor > 5:
        random_factor = 5

    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)

    # logger('{} with randomness -> {}'.format(int(n), randomized_n))

    return int(randomized_n)


def move_to_with_randomness(x, y, t):
    pyautogui.moveTo(add_randomness(x, 10), add_randomness(y, 10), t + random() / 2)


def remove_suffix(input_string, suffix):
    """
    Returns the input_string without the suffix
    """
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]

    return input_string


def load_images(dir_path='./targets/'):
    """ Programatically loads all images of dir_path as a key:value where the
        key is the file name without the .png suffix

    Returns:
        dict: dictionary containing the loaded images as key:value pairs.
    """
    file_names = os.listdir(dir_path)
    targets = {}

    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets


def load_heroes_to_send_home():
    """
    Loads the images in the path and saves them as a list
    """
    file_names = os.listdir('./targets/heroes-to-send-home')
    heroes = []

    for file in file_names:
        path = './targets/heroes-to-send-home/' + file
        heroes.append(cv2.imread(path))

    print('>>---> %d heroes that should be sent home loaded' % len(heroes))

    return heroes


def show(rectangles, img=None):
    """
    Show an popup with rectangles showing the rectangles[(x, y, w, h),...]
    over img or a print_sreen if no img provided. Useful for debugging
    """
    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)

    cv2.imshow('img', img)
    cv2.waitKey(0)


def click_btn(img, timeout=3, threshold=ct['default']):
    """
    Search for img in the scree, if found moves the cursor over it and clicks.
    Parameters:
        img: The image that will be used as an template to find where to click.
        timeout (int): Time in seconds that it will keep looking for the img before returning with fail
        threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
    """

    logger(None, progress_indicator=True)

    start = time.time()
    has_timed_out = False

    while not has_timed_out:
        matches = positions(img, threshold=threshold)

        if len(matches) == 0:
            has_timed_out = time.time() - start > timeout
            continue

        x, y, w, h = matches[0]
        pos_click_x = x + w / 2
        pos_click_y = y + h / 2

        move_to_with_randomness(pos_click_x, pos_click_y, 1)

        pyautogui.click()

        return True

    return False


def print_sreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))

        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:, :, :3]


def positions(target, threshold=ct['default'], img=None):
    if img is None:
        img = print_sreen()

    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)

    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def scroll():
    commoms = positions(images['commom-text'], threshold=ct['commom'])
    if len(commoms) == 0:
        return

    # if len(commoms) == 0:
    #     commoms = positions(images['rare-text'], threshold = ct['rare'])
    #     if len(commoms) == 0:
    #         commoms = positions(images['super_rare-text'], threshold = ct['super_rare'])
    #         if len(commoms) == 0:
    #             commoms = positions(images['epic-text'], threshold = ct['epic'])
    #             if len(commoms) == 0:
    #                 return

    x, y, w, h = commoms[len(commoms) - 1]

    move_to_with_randomness(x, y, 1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0, -c['click_and_drag_amount'], duration=1, button='left')


def click_buttons():
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    # print(f'buttons: {len(buttons)}')

    for (x, y, w, h) in buttons:
        move_to_with_randomness(x + (w / 2), y + (h / 2), 1)

        pyautogui.click()

        global hero_clicks
        hero_clicks = hero_clicks + 1

        # cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)

        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return

    return len(buttons)


def is_home(hero, buttons):
    y = hero[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)

        if isBelow and isAbove:  # if send-home button exists, the hero is not home
            return False

    return True


def is_working(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)

        if isBelow and isAbove:
            return False

    return True


def click_green_bar_buttons(qtd_of_hero):
    # click on the q so trabaiano but i think it doesn't matter
    offset = 140

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger(f'🟩 {len(green_bars)} green bars detected')

    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger(f'🆗 {len(buttons)} buttons detected')

    not_working_green_bars = []
    for bar in green_bars:
        if not is_working(bar, buttons):
            not_working_green_bars.append(bar)

    if len(not_working_green_bars) > 0 and qtd_of_hero < c['qtd_heroes_to_work']:
        logger(f'🆗 {len(not_working_green_bars)} buttons with green bar detected')
        logger(f'👆 Clicking in {len(not_working_green_bars)} heroes')

    # if you have a button with y greater than bar y-10 and less than y+10
    hero_clicks_cnt = 0
    for (x, y, w, h) in not_working_green_bars:
        if qtd_of_hero >= c['qtd_heroes_to_work']:
            not_working_green_bars = []
            break

        # is_working(y, buttons)

        move_to_with_randomness(x + offset + (w / 2), y + (h / 2), 1)

        pyautogui.click()

        global hero_clicks
        hero_clicks += 1
        hero_clicks_cnt += 1
        qtd_of_hero += 1
        
        if hero_clicks_cnt > 20:
            logger('⚠️ Too many hero clicks, try to increase the go_to_work_btn threshold')
            return
        
        # cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)

    return len(not_working_green_bars), qtd_of_hero


def click_full_bar_buttons(qtd_of_hero):
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not is_working(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('👆 Clicking in %d heroes' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        if qtd_of_hero >= c['qtd_heroes_to_work']:
            not_working_full_bars = []
            break

        move_to_with_randomness(x + offset + (w / 2), y + (h / 2), 1)

        pyautogui.click()

        global hero_clicks
        hero_clicks += 1
        qtd_of_hero += 1

    return len(not_working_full_bars), qtd_of_hero


def go_to_heroes():
    if click_btn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0

    # TODO take sleep when putting the pulling
    time.sleep(1)
    click_btn(images['hero-icon'])
    time.sleep(randint(1, 3))


def go_to_game():
    # in case of server overload popup
    click_btn(images['x'])
    # time.sleep(3)
    click_btn(images['x'])
    click_btn(images['treasure-hunt-icon'])


def refreshHeroesPositions():
    logger('🔃 Refreshing Heroes Positions')

    click_btn(images['go-back-arrow'])
    click_btn(images['treasure-hunt-icon'])
    # time.sleep(3)
    click_btn(images['treasure-hunt-icon'])


def login():
    global login_attempts
    logger('😿 Checking if game has disconnected')

    if login_attempts > 3:
        logger('🔃 Too many login attempts, refreshing')

        login_attempts = 0
        pyautogui.hotkey('ctrl', 'f5')
        return

    if click_btn(images['connect-wallet'], timeout=10):
        logger('🎉 Connect wallet button detected, logging in!')

        login_attempts = login_attempts + 1
        # TODO high it gives error and low the button doesn't open
        # time.sleep(10)

    if click_btn(images['select-wallet-2'], timeout=8):
        # sometimes the sign popup appears imediately
        login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print(f'{login_attempts} login attempt')

        if click_btn(images['treasure-hunt-icon'], timeout=15):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0

        return  # click ok button

    if not click_btn(images['select-wallet-1-no-hover'], ):
        if click_btn(images['select-wallet-1-hover'], threshold=ct['select_wallet_buttons']):
            pass
            # ideally, he would alternate between checking each of the 2 for a while.
            # print('sleep in case there is no metamask text removed')
            # time.sleep(20)
    else:
        # print('sleep in case there is no metamask text removed')
        # time.sleep(20)
        pass

    if click_btn(images['select-wallet-2'], timeout=20):
        login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print(f'{login_attempts} login attempt')

        # time.sleep(25)

        if click_btn(images['treasure-hunt-icon'], timeout=25):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0

        # time.sleep(15)

    if click_btn(images['ok'], timeout=5):
        # time.sleep(15)
        # print('ok button clicked')
        pass


def send_heroes_home():
    if not ch['enable']:
        return

    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len(hero_positions) == 0:
            # TODO maybe pick up match with most wheight instead of first
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)

    n = len(heroes_positions)
    if n == 0:
        print('No heroes that should be sent home found.')
        return

    print(' %d heroes that should be sent home found' % n)

    # if send-home button exists, the hero is not home
    go_home_buttons = positions(images['send-home'], threshold=ch['home_button_threshold'])

    # TODO pass it as an argument for both this and the other function that uses it
    go_work_buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    for position in heroes_positions:
        if not is_home(position, go_home_buttons):
            print(is_working(position, go_work_buttons))

            if not is_working(position, go_work_buttons):
                print('hero not working, sending him home')
                move_to_with_randomness(
                    go_home_buttons[0][0] + go_home_buttons[0][2] / 2, position[1] + position[3] / 2, 1
                )
                pyautogui.click()
            else:
                print('hero working, not sending him home(no dark work button)')
        else:
            print('hero already home, or home full(no dark home button)')


def refreshHeroes():
    logger('🏢 Search for heroes to work')

    go_to_heroes()

    if c['select_heroes_mode'] == "full":
        logger('⚒️ Sending heroes with full stamina bar to work', 'green')
    elif c['select_heroes_mode'] == "green":
        logger('⚒️ Sending heroes with green stamina bar to work', 'green')
    else:
        logger('⚒️ Sending all heroes to work', 'green')

    empty_scrolls_attempts = c['scroll_attemps']
    hero_to_works = 0
    qtd_of_hero = 0

    while empty_scrolls_attempts > 0:
        if c['select_heroes_mode'] == 'full':
            buttons_clicked, qtd_of_hero = click_full_bar_buttons(qtd_of_hero)
        elif c['select_heroes_mode'] == 'green':
            buttons_clicked, qtd_of_hero = click_green_bar_buttons(qtd_of_hero)
        else:
            buttons_clicked = click_buttons()

        send_heroes_home()

        if buttons_clicked == 0:
            empty_scrolls_attempts -= 1

        # empty_scrolls_attempts -= 1
        scroll()

        time.sleep(2)
    
    hero_to_works += qtd_of_hero

    logger(f'💣 {hero_to_works} heroes were sent to work on this process')
    logger(f'💪 Total off {hero_clicks} heroes sent to work')
    
    go_to_game()


def main():
    """
    Main execution setup and loop
    """
    global hero_clicks
    global login_attempts
    global last_log_is_progress

    hero_clicks = 0
    login_attempts = 0
    last_log_is_progress = False

    global images
    images = load_images()

    if ch['enable']:
        global home_heroes
        home_heroes = load_heroes_to_send_home()
    else:
        print('>>---> Home feature not enabled')

    print('\n')
    print(cat)

    time.sleep(7)

    t = c['time_intervals']
    windows = []
    windows_id = 0

    for w in pygetwindow.getWindowsWithTitle('bombcrypto - Google Chrome'):
        windows_id += 1
        windows.append({
            'window': w,
            'login': 0,
            'heroes': 0,
            'new_map': 0,
            'refresh_heroes': 0,
            'window_name': f'Bombcrypto_00{windows_id}'
        })

    while True:
        now = time.time()

        for last in windows:
            last['window'].activate()

            logger(f'{"=" * 36}', progress_indicator=False, line_break='\n\n')
            logger(f'{"=" * 10} {last.get("window_name").upper()} {"=" * 10}', progress_indicator=False)
            logger(f'{"=" * 36}', progress_indicator=False)

            time.sleep(2)

            if now - last['heroes'] > add_randomness(t['send_heroes_for_work'] * 60):
                last['heroes'] = now
                refreshHeroes()

            if now - last['login'] > add_randomness(t['check_for_login'] * 60):
                sys.stdout.flush()
                last['login'] = now
                login()

            if now - last['new_map'] > t['check_for_new_map_button']:
                last['new_map'] = now

                if click_btn(images['new-map']):
                    logger_map_clicked(f'{last.get("window_name").upper()}')

            if now - last["refresh_heroes"] > add_randomness(t['refresh_heroes_positions'] * 60):
                last["refresh_heroes"] = now
                refreshHeroesPositions()

            # click_btn(teasureHunt)

            logger(None, progress_indicator=True)

            sys.stdout.flush()

            time.sleep(30)


if __name__ == '__main__':
    main()

# cv2.imshow('img',sct_img)
# cv2.waitKey()

# put the button in pt
# only reset positions if you have not clicked on newmap in x seconds
