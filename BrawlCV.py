import aiohttp
import asyncio
import json
import os
import re
import tkinter as tk
import tkinter.font
import webbrowser
from tkinter import messagebox

import pyglet
import requests
from bs4 import BeautifulSoup
from emot.emo_unicode import UNICODE_EMOJI
from PIL import Image, ImageDraw, ImageFont, ImageTk

GlobalTag = ''
TEXT_FONT = 'fonts/LilitaOne-Fresh.ttf'
IOS_FONT = 'fonts/AppleColorEmoji.ttf'
VERSION = 'v0.2.1'
Window = tk.Tk()
GlobalStats = {}
GlobalStatsLong = {}
GlobalRanks = []
GlobalOfficial = {}
AvailOfficial = []
ErrCode = 0
BgColorOverride = 0
BrawlerOverride = ''
BrawlerPinList = []


def url_tasks(session, url_list):
    tasks = []
    for url in url_list:
        tasks.append(session.get(url, ssl=False))
    return tasks


async def url_fetch(player_tag):
    url_list = [
        f'https://cr.is-a.dev/{player_tag.upper()}',    # get user long
        'https://cr.is-a.dev/v1/brawlers',      # get official
        f'https://brawlstats.com/profile/{player_tag.upper()}'  # get pl
    ]
    url_list_purpose = ['user_long', 'official', 'pl']
    user_json_dict = {}
    async with aiohttp.ClientSession() as session:
        tasks = url_tasks(session, url_list)
        responses = await asyncio.gather(*tasks)
        for v, response in enumerate(responses):
            if v == 2:
                user_json_dict[url_list_purpose[v]] = await response.text()
                continue
            user_json_dict[url_list_purpose[v]] = await response.json()
    # =======================================BeautifulSoup get pl start
    soup = BeautifulSoup(user_json_dict['pl'], 'html.parser')
    temp_ranks = []
    if soup.find('div', {'class': '_230Gh9q1rJmb0YFOn6qXf5'}) is not None:
        user_json_dict['pl_error'] = '500 error'
        return user_json_dict
    for item in soup.find_all('img', {'class': 'DPUFH-EhiGBBrkki4Gsaf'}):
        temp_ranks.append(item['src'])
    challenge_attrs = soup.find_all(
        'div', {'class': 'mo25VS9slOfRz6jng3WTf'})
    challenge_wins = int(challenge_attrs[10].text)
    ranks = []
    for item in temp_ranks:
        for s in re.findall(r'\d+', item):
            if s.isdigit():
                ranks.append(int(s))
    ranks.append(challenge_wins)
    # =======================================get pl end
    user_json_dict['pl'] = ranks
    return user_json_dict


def get_official(code=0):
    global GlobalOfficial
    if GlobalOfficial == '':
        url = 'https://cr.is-a.dev/v1/brawlers'
        response = requests.get(url)
        if response.status_code in [400, 403, 404, 429, 500, 503]:
            raise Exception(response.status_code)
        official_json = response.json()
    else:
        official_json = GlobalOfficial
    brawler_available = len(official_json['items'])
    brawler_disabled = 0
    brawler_available -= brawler_disabled
    sp_available = 0
    sp_disabled = 0
    for i in official_json['items']:
        sp_available += len(i['starPowers'])
    sp_available -= sp_disabled
    gadget_available = 0
    for i in official_json['items']:
        gadget_available += len(i['gadgets'])
    gadget_disabled = 0
    gadget_available -= gadget_disabled
    official_list = [brawler_available, sp_available, gadget_available]
    sp_list = []
    for i in official_json['items']:
        temp = [i['id']]
        for j in range(2):
            try:
                temp.append(i['starPowers'][j]['id'])
            except IndexError:
                pass
        sp_list.append(temp)
        del temp
    gad_list = []
    for i in official_json['items']:
        temp = [i['id']]
        for j in range(2):
            try:
                temp.append(i['gadgets'][j]['id'])
            except IndexError:
                pass
        gad_list.append(temp)
        del temp
    if code == 0:
        return official_list
    elif code == 1:
        return sp_list
    elif code == 2:
        return gad_list
    else:
        pass


def aspect_height(new_width, img):
    new_height = int(new_width / img.width * img.height)
    return new_height


def aspect_width(new_height, img):
    new_width = int(new_height / img.height * img.width)
    return new_width


def draw_border(draw, x, y, text, ft, color='black', border=True):
    if border:
        draw.text((x - 2, y - 2), text, font=ft, fill=color)
        draw.text((x + 2, y - 2), text, font=ft, fill=color)
        draw.text((x - 2, y + 2), text, font=ft, fill=color)
        draw.text((x + 2, y + 2), text, font=ft, fill=color)
    draw.text((x, y + 10), text, font=ft, fill=color)


def draw_text(draw, x, y, text, ft):
    w = int(draw.textlength(text, font=ft))
    draw.text(((x - w) / 2, y), text, font=ft)


def sort_json(data, key, desc=False):
    sorted_json = sorted(data, key=lambda x: x[key], reverse=desc)
    return sorted_json


def search_json(data, field, key, field2):
    for i in data:
        if str(i[field]) == str(key):
            return i[field2]


def center_img(x, y, img):
    w = img.width
    h = img.height
    coord = (int(x - w / 2), int(y - h / 2))
    return coord


def two_pt_tuple(x, y, width, height):
    coord = [(x, y), (x + width, y + height)]
    return coord


def save_image1(bg_override=0, brawler_override=''):

    bs_font_0 = ImageFont.truetype(TEXT_FONT, 45)
    bs_font_1 = ImageFont.truetype(TEXT_FONT, 38)
    background_img = Image.open(
        f'assets/background/{str(bg_override)}.png').convert('RGBA')
    background_img_0 = background_img.resize(
        (2048, aspect_height(2048, background_img)))
    draw = ImageDraw.Draw(background_img_0)
    try:
        player_icon = Image.open(
            f'assets/player_icon/{GlobalStats["icon_id"]}.png').convert('RGBA')
    except FileNotFoundError:
        player_icon = Image.open('assets/player_icon/0.png').convert('RGBA')
    player_icon_0 = player_icon.resize(
        (110, aspect_height(110, player_icon)))
    background_img_0.paste(place_text(
        GlobalStats['name'], 90), (170, 35 - 90 // 2), place_text(GlobalStats['name'], 90))
    background_img_0.paste(place_text(GlobalStats['club_name'], 60), (
        170, 165 - 60 // 2), place_text(GlobalStats['club_name'], 60))
    club_badge = Image.open('assets/club_badge/' +
                            GlobalStats['club_badge']).convert('RGBA')
    club_badge_0 = club_badge.resize((90, aspect_height(90, club_badge)))
    stats_table = Image.open('assets/stats/stats_table.png').convert('RGBA')
    stats_table_0 = stats_table.resize(
        (1100, aspect_height(1100, stats_table)))
    background_img_0.paste(player_icon_0, (30, 30), player_icon_0)
    background_img_0.paste(club_badge_0, (40, 160), club_badge_0)

    # ========================================Place StatsTable (13 items)
    background_img_0.paste(stats_table_0, (30, 270), stats_table_0)
    draw_text(draw, 543, 353, str(GlobalStats['trophies']), bs_font_0)
    draw_text(draw, 1233, 353, str(
        GlobalStats['highest_trophies']), bs_font_0)
    draw_text(draw, 1923, 353, str(GlobalStats['exp_level']), bs_font_0)
    draw_text(draw, 543, 493, str(GlobalStats['x3v3_victories']), bs_font_0)
    draw_text(draw, 1233, 493, str(
        GlobalStats['solo_victories']), bs_font_0)
    draw_text(draw, 1923, 493, str(GlobalStats['duo_victories']), bs_font_0)
    solo_league = Image.open(
        f'assets/league_icon/ranked_ranks_l_{GlobalRanks[0]}.png').convert('RGBA')
    solo_league_0 = solo_league.resize(
        (170, aspect_height(170, solo_league)))
    team_league = Image.open(
        f'assets/league_icon/ranked_ranks_l_{GlobalRanks[1]}.png').convert('RGBA')
    team_league_0 = team_league.resize(
        (170, aspect_height(170, team_league)))
    club_league = Image.open(
        f'assets/league_icon/club_ranks_l_{GlobalRanks[2]}.png').convert('RGBA')
    club_league_0 = club_league.resize(
        (170, aspect_height(170, club_league)))
    background_img_0.paste(solo_league_0, (185, 616), solo_league_0)
    background_img_0.paste(team_league_0, (530, 616), team_league_0)
    background_img_0.paste(club_league_0, (875, 616), club_league_0)
    draw_text(draw, 543, 773,
              f'{GlobalStats["brawlers_owned"]}/{AvailOfficial[0]}', bs_font_0)
    draw_text(draw, 1233, 773,
              f'{GlobalStats["sp_owned"]}/{AvailOfficial[1]}', bs_font_0)
    draw_text(draw, 1923, 773,
              f'{GlobalStats["gadgets_owned"]}/{AvailOfficial[2]}', bs_font_0)
    draw_text(draw, 1233, 913, str(GlobalRanks[3]), bs_font_0)
    stats_sorted = sort_json(
        GlobalStatsLong['brawlers'], 'highestTrophies', desc=True)
    brawler_override = str(brawler_override)

    # ====================(Unspecified brawler, use brawler with highest PB) Brawler3D, trophies(current & best) , SPs, gadgets
    if brawler_override == '':
        try:
            brawler_3d = Image.open(
                f'assets/brawler_3d/{stats_sorted[0]["id"]}.png').convert('RGBA')
        except FileNotFoundError:
            brawler_3d = Image.open(
                'assets/brawler_3d/0.png').convert('RGBA')
        brawler_3d_0 = brawler_3d.resize(
            (1800, aspect_height(1800, brawler_3d)))
        brawler_rank = Image.open(
            f'assets/rank_icon/{stats_sorted[0]["rank"]}.png').convert('RGBA')
        brawler_rank_0 = brawler_rank.resize(
            (100, aspect_height(100, brawler_rank)))
        stats_tr = stats_sorted[0]['trophies']
        stats_htr = stats_sorted[0]['highestTrophies']
        stats_sp = stats_sorted[0]['starPowers']
        stats_gad = stats_sorted[0]['gadgets']
    # ====================(Specified brawler) Brawler3D, trophies(current & best), SPs, gadgets
    else:
        try:
            brawler_3d = Image.open(
                f'assets/brawler_3d/{brawler_override}.png').convert('RGBA')
        except FileNotFoundError:
            brawler_3d = Image.open(
                'assets/brawler_3d/0.png').convert('RGBA')
        brawler_3d_0 = brawler_3d.resize(
            (1800, aspect_height(1800, brawler_3d)))
        rank_search = search_json(stats_sorted, 'id', brawler_override, 'rank')
        brawler_rank = Image.open(
            f'assets/rank_icon/{rank_search}.png').convert('RGBA')
        brawler_rank_0 = brawler_rank.resize(
            (100, aspect_height(100, brawler_rank)))
        stats_tr = search_json(
            stats_sorted, 'id', brawler_override, 'trophies')
        stats_htr = search_json(
            stats_sorted, 'id', brawler_override, 'highestTrophies')
        stats_sp = search_json(
            stats_sorted, 'id', brawler_override, 'starPowers')
        stats_gad = search_json(
            stats_sorted, 'id', brawler_override, 'gadgets')

    # ========================================Place Brawler3D, HighestTrophies
    trophy_container = Image.open(
        'assets/stats/container.png').convert('RGBA')
    trophy_container_0 = trophy_container.resize(
        (300, aspect_height(210, trophy_container)))
    trophy = Image.open('assets/stats/trophies.png').convert('RGBA')
    trophy_0 = trophy.resize((50, aspect_height(50, trophy)))
    background_img_0.paste(brawler_3d_0, (250, 100), brawler_3d_0)
    background_img_0.paste(
        trophy_container_0, (1220, 80), trophy_container_0)
    background_img_0.paste(brawler_rank_0, (1160, 60), brawler_rank_0)
    background_img_0.paste(trophy_0, (1270, 95), trophy_0)
    draw.text((1320, 95), f'{stats_tr}/{stats_htr}', font=bs_font_1)
    slot = []

    # ========================================Place StarPowers, Gadgets
    for i in range(2):
        try:
            slot.append(str(stats_sp[i]['id']))
            slot.append('sp')
        except KeyError:
            break
        except IndexError:
            break
    for i in range(2):
        try:
            slot.append(str(stats_gad[i]['id']))
            slot.append('gad')
        except KeyError:
            break
        except IndexError:
            break
    for i in range(len(slot) // 2):
        if slot[i * 2 + 1] == 'sp':
            power_bg = Image.open(
                'assets/stats/star-power-blank.png').convert('RGBA')
            power_bg_0 = power_bg.resize((80, aspect_height(80, power_bg)))
            background_img_0.paste(
                power_bg_0, (1540 + 90 * i, 75), power_bg_0)
            try:
                power_fore = Image.open(
                    f'assets/star_powers/{slot[i*2]}.png').convert('RGBA')
            except FileNotFoundError:
                if brawler_override == '':
                    temp = search_sp(get_official(code=1),
                                     stats_sorted[0]['id'], int(slot[i * 2]))
                else:
                    temp = search_sp(get_official(code=1), int(
                        brawler_override), int(slot[i * 2]))
                try:
                    power_fore = Image.open(
                        f'assets/star_powers/sp{temp}.png').convert('RGBA')
                except FileNotFoundError:
                    power_fore = Image.open(
                        'assets/star_powers/sp1.png').convert('RGBA')
        else:
            power_bg = Image.open(
                'assets/stats/gadget-blank.png').convert('RGBA')
            power_bg_0 = power_bg.resize((80, aspect_height(80, power_bg)))
            background_img_0.paste(
                power_bg_0, (1540 + 90 * i, 75), power_bg_0)
            try:
                power_fore = Image.open(
                    f'assets/gadgets/{slot[i * 2]}.png').convert('RGBA')
            except FileNotFoundError:
                if brawler_override == '':
                    temp = search_sp(get_official(code=2),
                                     stats_sorted[0]['id'], int(slot[i * 2]))
                else:
                    temp = search_sp(get_official(code=2), int(
                        brawler_override), int(slot[i * 2]))
                try:
                    power_fore = Image.open(
                        f'assets/gadgets/gad{temp}.png').convert('RGBA')
                except FileNotFoundError:
                    power_fore = Image.open(
                        'assets/gadgets/gad1.png').convert('RGBA')
        if power_fore.width > power_fore.height:
            power_fore_0 = power_fore.resize(
                (38, aspect_height(38, power_fore)))
        else:
            power_fore_0 = power_fore.resize(
                (aspect_width(38, power_fore), 38))
        background_img_0.paste(power_fore_0, center_img(
            1580 + 90 * i, 115, power_fore_0), power_fore_0)
    background_img_0.save('profile1.png')


def save_image2(bg_override=0):
    background_img = Image.open(
        f'assets/background/plain-{str(bg_override)}.png').convert('RGBA')
    background_img_0 = background_img.resize(
        (2048, aspect_height(2048, background_img)))
    draw = ImageDraw.Draw(background_img_0)
    try:
        player_icon = Image.open(
            f'assets/player_icon/{GlobalStats["icon_id"]}.png').convert('RGBA')
    except FileNotFoundError:
        player_icon = Image.open('assets/player_icon/0.png').convert('RGBA')
    player_icon_0 = player_icon.resize(
        (110, aspect_height(110, player_icon)))
    club_badge = Image.open(
        f'assets/club_badge/{GlobalStats["club_badge"]}').convert('RGBA')
    club_badge_0 = club_badge.resize((90, aspect_height(90, club_badge)))
    background_img_0.paste(place_text(
        GlobalStats['name'], 90), (170, 35 - 90 // 2), place_text(GlobalStats['name'], 90))
    background_img_0.paste(place_text(GlobalStats['club_name'], 60), (
        170, 165 - 60 // 2), place_text(GlobalStats['club_name'], 60))
    background_img_0.paste(player_icon_0, (30, 30), player_icon_0)
    background_img_0.paste(club_badge_0, (40, 160), club_badge_0)
    stats_sorted = sort_json(
        GlobalStatsLong['brawlers'], 'highestTrophies', desc=True)
    pos = 0
    colors = [(198, 93, 45), (129, 133, 182), (216, 152, 83), (97, 168, 234),
              (185, 72, 238), (83, 186, 117), (195, 55, 68), (62, 50, 122)]
    for i in stats_sorted:
        img_src = f'assets/portraits/{i["id"]}.png'
        try:
            brawler_img = Image.open(img_src).convert('RGBA')
        except FileNotFoundError:
            brawler_img = Image.open(
                'assets/portraits/0.png').convert('RGBA')
        brawler_img_0 = brawler_img.resize(
            (aspect_width(99, brawler_img), 99))
        brawler_rank = Image.open(
            f'assets/rank_icon/{i["rank"]}.png').convert('RGBA')
        brawler_rank_0 = brawler_rank.resize(
            (82, aspect_height(82, brawler_rank)))
        rank_color = colors[i['rank'] // 5]
        if pos < 5:
            draw.rectangle(two_pt_tuple((pos % 5 + 5) * 222 - 193, (pos // 5 + 1) *
                           114 + 37, 212, 104), fill=rank_color, outline='black', width=3)
            background_img_0.paste(brawler_img_0, ((
                pos % 5 + 5) * 222 - 190, (pos // 5 + 1) * 114 + 40), brawler_img_0)
            background_img_0.paste(brawler_rank_0, ((
                pos % 5 + 5) * 222 - 73, (pos // 5 + 1) * 114 + 43), brawler_rank_0)
        else:
            draw.rectangle(two_pt_tuple(((pos - 5) % 9 + 1) * 222 - 193, ((pos - 5) // 9 + 2) *
                           114 + 37, 212, 104), fill=rank_color, outline='black', width=3)
            background_img_0.paste(brawler_img_0, ((
                (pos - 5) % 9 + 1) * 222 - 190, ((pos - 5) // 9 + 2) * 114 + 40), brawler_img_0)
            background_img_0.paste(brawler_rank_0, ((
                (pos - 5) % 9 + 1) * 222 - 73, ((pos - 5) // 9 + 2) * 114 + 43), brawler_rank_0)
        pos += 1
    background_img_0.save('profile2.png')


def place_text(text, size):
    background_img = Image.new(mode='RGBA', size=(2048, 274))
    draw = ImageDraw.Draw(background_img)
    apple_font = ImageFont.truetype(IOS_FONT, 137)
    text_font = ImageFont.truetype(TEXT_FONT, 137)
    new_str = ''
    for i in str(text):
        if ord(i) < 65024 or ord(i) > 65039:
            new_str += i
    text_width = 0
    for i in new_str:
        if is_emoji(i):
            draw_border(draw, 0 + text_width, 69, i,
                        ft=apple_font, border=False)
            draw.text((0 + text_width, 69), i,
                      font=apple_font, embedded_color=True)
            text_width += int(draw.textlength(i, font=apple_font))
        else:
            draw_border(draw, 0 + text_width, 69, i, ft=text_font)
            draw.text((0 + text_width, 69), i,
                      font=text_font, embedded_color=True)
            text_width += int(draw.textlength(i, font=text_font))
    background_img_0 = background_img.resize(
        (aspect_width(size * 2, background_img), size * 2))
    return background_img_0


def is_emoji(s):
    return s in UNICODE_EMOJI


def search_sp(data, brawler_id, sp_id):
    for i in data:
        if i[0] == brawler_id:
            for j in range(2):
                try:
                    if i[j + 1] == sp_id:
                        return j + 1
                except IndexError:
                    return None
    return None


def open_url(url):
    webbrowser.open_new_tab(url)


def show_canvas(canv, skip=False):
    global Window, GlobalTag, GlobalStats, GlobalStatsLong, GlobalRanks, AvailOfficial, BrawlerPinList
    tk.Misc.lift(canv)
    if str(canv) == '.!canvas4':
        with open('assets/config/config_tag.json', 'r') as f:
            config_tag = json.load(f)
        # if not skip:
        if not (config_tag['tag'] != '' and os.path.isfile('profile1.png') and os.path.isfile('profile2.png') and skip):
            f.close()
            os.remove('assets/config/config_tag.json')
            with open('assets/config/config_tag.json', 'w') as f:
                config_tag['tag'] = GlobalTag
                json.dump(config_tag, f)
            save_image1()
            save_image2()
        else:  # skips, need to load json
            with open('assets/config/config_stats.json', 'r') as f:
                GlobalStats = json.load(f)
                f.close()
            with open('assets/config/config_stats_long.json', 'r') as f:
                GlobalStatsLong = json.load(f)
                f.close()
            with open('assets/config/config_ranks.json', 'r') as f:
                temp_list = json.load(f)
                GlobalRanks = temp_list['ranks']
                f.close()
            with open('assets/config/config_avail.json', 'r') as f:
                temp_list = json.load(f)
                AvailOfficial = temp_list['avail']
                f.close()
        profile1 = Image.open('profile1.png')
        profile1_1 = profile1.resize((620, aspect_height(620, profile1)))
        profile1_0 = ImageTk.PhotoImage(profile1_1)
        Window.profile1_0 = profile1_0
        canv.create_image(15, 200, image=Window.profile1_0, anchor='nw')
        profile2 = Image.open('profile2.png')
        profile2_1 = profile2.resize((620, aspect_height(620, profile2)))
        profile2_0 = ImageTk.PhotoImage(profile2_1)
        Window.profile2_0 = profile2_0
        canv.create_image(645, 200, image=Window.profile2_0, anchor='nw')
        pin_num = 0
        pin_id_num = 0
        BrawlerPinList = []
        sort_override = [16000000, 16000001, 16000003, 16000007, 16000008, 16000009, 16000010, 16000002, 16000004,
                         16000006, 16000013, 16000011, 16000014, 16000005, 16000012]
        for i in GlobalStatsLong['brawlers']:
            if i['id'] <= 16000014:
                j = sort_override[pin_num]
            else:
                j = i['id']
            if os.path.isfile(f'assets/pins/{str(j)}.png'):
                brawler_pin = Image.open(
                    f'assets/pins/{str(j)}.png').convert('RGBA')
            else:
                brawler_pin = Image.open('assets/pins/0.png').convert('RGBA')
            width, height = brawler_pin.size
            if width > height * 1.1:
                brawler_pin_1 = brawler_pin.resize(
                    (48, aspect_height(48, brawler_pin)))
            elif width * 1.3 < height:
                brawler_pin_1 = brawler_pin.resize(
                    (aspect_width(50, brawler_pin), 50))
            else:
                brawler_pin_1 = brawler_pin.resize(
                    (aspect_width(45, brawler_pin), 45))
            brawler_pin_0 = ImageTk.PhotoImage(brawler_pin_1)
            BrawlerPinList.append(brawler_pin_0)
            canv.create_image(pin_num % 24 * 51 + 55, pin_num // 24 * 48 + 560,
                              image=BrawlerPinList[pin_num], anchor="center", tag=f'pin_{pin_id_num}')
            canv.tag_bind(f'pin_{pin_id_num}', '<1>', lambda e: change_color(
                canv) if element_tag2(e) else change_color(canv))
            pin_num += 1
            pin_id_num += 1
            if pin_id_num == 33 or pin_id_num == 55:
                pin_id_num += 1


def validation(tag):
    global GlobalStats, GlobalStatsLong, GlobalRanks, GlobalOfficial, AvailOfficial, GlobalTag, ErrCode
    GlobalTag = tag
    ErrCode = 0
    if tag == '':
        ErrCode = 1
        return 1
    if not all(i.upper() in 'PYLQGRJCUV0289' for i in tag):
        ErrCode = 2
        return 1

    # =======================================cr.is-a.dev init
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    user_json_dict = asyncio.run(url_fetch(player_tag=tag))
    GlobalStatsLong = user_json_dict['user_long']
    GlobalOfficial = user_json_dict['official']
    if 'pl_error' in user_json_dict.keys():
        ErrCode = 5000
        return 1
    GlobalRanks = user_json_dict['pl']
    # =======================================cr.is-a.dev GlobalStatsLong, GlobalStats, AvailOfficial
    if 'message' in GlobalStatsLong:
        ErrCode = int(GlobalStatsLong['message'][0:3])
        return 1
    name = GlobalStatsLong['name']
    icon_id = GlobalStatsLong['icon']['id']
    trophies = GlobalStatsLong['trophies']
    highest_trophies = GlobalStatsLong['highestTrophies']
    exp_level = GlobalStatsLong['expLevel']
    x3v3_victories = GlobalStatsLong['3vs3Victories']
    solo_victories = GlobalStatsLong['soloVictories']
    duo_victories = GlobalStatsLong['duoVictories']
    in_club = True
    try:
        club_name = GlobalStatsLong['club']['name']
        club_tag = GlobalStatsLong['club']['tag']
        url = f'https://cr.is-a.dev/clubs/{club_tag[1:len(club_tag)]}'
        response = requests.get(url)
        if response.status_code in [400, 403, 404, 429, 500, 503]:
            return response.status_code
        club_json = response.json()
        club_badge_id = str(club_json['badgeId'])
        club_badge = f'{club_badge_id}.png'
    except KeyError:
        club_name = 'Not in a Club'
        club_tag = ''
        club_badge = '0.png'
        in_club = False
    brawlers_owned = len(GlobalStatsLong['brawlers'])
    sp_owned = 0
    for i in GlobalStatsLong['brawlers']:
        sp_owned += len(i['starPowers'])
    gadget_owned = 0
    for i in GlobalStatsLong['brawlers']:
        gadget_owned += len(i['gadgets'])
    GlobalStats = {
        'name': name,
        'icon_id': icon_id,
        'trophies': trophies,
        'highest_trophies': highest_trophies,
        'exp_level': exp_level,
        'x3v3_victories': x3v3_victories,
        'solo_victories': solo_victories,
        'duo_victories': duo_victories,
        'in_club': in_club,
        'club_name': club_name,
        'club_tag': club_tag,
        'club_badge': club_badge,
        'brawlers_owned': brawlers_owned,
        'sp_owned': sp_owned,
        'gadgets_owned': gadget_owned
    }
    AvailOfficial = get_official()

    # =======================================BrawlStats GlobalRanks
    with open('assets/config/config_stats.json', 'w') as f:
        json.dump(GlobalStats, f)
        f.close()
    with open('assets/config/config_stats_long.json', 'w') as f:
        json.dump(GlobalStatsLong, f)
        f.close()
    with open('assets/config/config_ranks.json', 'w') as f:
        json.dump({'ranks': GlobalRanks}, f)
        f.close()
    with open('assets/config/config_avail.json', 'w') as f:
        json.dump({'avail': AvailOfficial}, f)
        f.close()
    return 0  # not 0 returns True


def bad_input_err(err_type=1):
    global Window, ErrCode
    window_new = tk.Toplevel()
    window_new.geometry('400x255+360+360')
    window_new.config(bg='#fff')
    err_icon = tk.PhotoImage(file='assets/ui/error.png')
    window_new.iconphoto(False, err_icon)
    canvas = tk.Canvas(window_new, width=400, height=255,
                       bd=0, highlightthickness=0)
    pyglet.font.add_file(TEXT_FONT)
    background_img = Image.open('assets/ui/background.png')
    background_img_1 = background_img.resize((400, 255))
    background_img_0 = ImageTk.PhotoImage(background_img_1)
    canvas.create_image(0, 0, image=background_img_0, anchor='nw')
    if err_type == 1:
        window_new.title('Missing player tag')
        canvas.create_text(200, 120, text='Please fill in your player tag.',
                           fill='#fff', font=('Lilita One Fresh', 18), anchor='center')
    elif err_type == 2:
        window_new.title('Invalid player tag')
        canvas.create_text(200, 120, text='Player tag must only consist of\nP,Y,L,Q,G,R,J,C,U,V,0,2,8,9.',
                           fill='#fff', font=('Lilita One Fresh', 18), anchor='center', justify='center')
    elif err_type == 404 or err_type == 1404:
        window_new.title('Player tag not found')
        canvas.create_text(200, 120, text='Cannot find the player with\nthe provided tag',
                           fill='#fff', font=('Lilita One Fresh', 18), anchor='center', justify='center')
    elif err_type == 5000:
        window_new.title('Brawl stats error')
        canvas.create_text(200, 120, text='An error occurred when fetching\nBrawl Stats data.',
                           fill='#fff', font=('Lilita One Fresh', 18), anchor='center', justify='center')

    elif err_type == 503 or err_type == 1503:
        window_new.title('Maintenance break')
        canvas.create_text(200, 120, text='Brawl stars is having a maintenance\nbreak. Please try again later.',
                           fill='#fff', font=('Lilita One Fresh', 18), anchor='center', justify='center')
    else:
        window_new.title('Error')
        if err_type < 1000:
            canvas.create_text(200, 120, text=f'An error occurred. Please try again.\n[Errno {str(err_type)}]',
                               fill='#fff', font=('Lilita One Fresh', 18), anchor='center', justify='center')
        else:
            canvas.create_text(200, 120, text=f'An error occurred. Please try again.\n[Errno {str(err_type-1000)}] at brawlstats.com',
                               fill='#fff', font=('Lilita One Fresh', 18), anchor='center', justify='center')
    canvas.place(x=0, y=0)
    window_new.mainloop()


def element_tag(event, window_old):
    global Window, BgColorOverride
    current = event.widget.find_withtag("current")[0]
    window_old.destroy()
    BgColorOverride = current - 1
    return current


def element_tag1(event):
    global BgColorOverride
    current = event.widget.find_withtag("current")[0]
    current_str = event.widget.itemconfig(current)['tags'][-1][5]
    BgColorOverride = str(current_str)


def element_tag2(event):
    global BrawlerOverride
    current = event.widget.find_withtag("current")[0]
    current_str = event.widget.itemconfig(current)['tags'][-1]
    current_str_0 = re.findall('[0-9]+', current_str)
    BrawlerOverride = int(current_str_0[0])
    sort_override = [0, 1, 3, 7, 8, 9, 10, 2, 4, 6, 13, 11, 14, 5, 12]
    if BrawlerOverride <= 14:
        BrawlerOverride = sort_override[BrawlerOverride]
    if (BrawlerOverride >= 48) and (BrawlerOverride <= 53):
        if BrawlerOverride == 53:
            BrawlerOverride = 48
        else:
            BrawlerOverride += 1
    BrawlerOverride += 16000000
    return current


def change_color(canv):
    global Window, BgColorOverride, BrawlerOverride
    save_image1(bg_override=BgColorOverride, brawler_override=BrawlerOverride)
    save_image2(bg_override=BgColorOverride)
    profile1 = Image.open('profile1.png')
    profile1_1 = profile1.resize((620, aspect_height(620, profile1)))
    profile1_0 = ImageTk.PhotoImage(profile1_1)
    Window.profile1_0 = profile1_0
    canv.create_image(15, 200, image=Window.profile1_0, anchor='nw')
    profile2 = Image.open('profile2.png')
    profile2_1 = profile2.resize((620, aspect_height(620, profile2)))
    profile2_0 = ImageTk.PhotoImage(profile2_1)
    Window.profile2_0 = profile2_0
    canv.create_image(645, 200, image=Window.profile2_0, anchor='nw')


def gui():
    global Window, VERSION

    # ========================================Window config
    Window.title('BrawlCV')
    Window.geometry('1280x720+100+100')
    Window.config(bg='#fff')
    smol_icon = tk.PhotoImage(file='assets/ui/brawl_cv_smol.png')
    Window.iconphoto(False, smol_icon)
    canvas_1 = tk.Canvas(Window, width=1280, height=720,
                         bd=0, highlightthickness=0)  # Sample
    canvas_2 = tk.Canvas(Window, width=1280, height=720,
                         bd=0, highlightthickness=0)  # FAQ
    canvas_3 = tk.Canvas(Window, width=1280, height=720,
                         bd=0, highlightthickness=0)  # Contributors
    canvas_4 = tk.Canvas(Window, width=1280, height=720,
                         bd=0, highlightthickness=0)  # Image1
    canvas_5 = tk.Canvas(Window, width=1280, height=720,
                         bd=0, highlightthickness=0)  # Image2
    canvas_0 = tk.Canvas(Window, width=1280, height=720,
                         bd=0, highlightthickness=0)  # Home
    canvas_list = (canvas_0, canvas_1, canvas_2,
                   canvas_3, canvas_4, canvas_5)
    pyglet.font.add_file(TEXT_FONT)

    # ========================================For all canvases
    background_img = Image.open('assets/ui/background.png')
    background_img_1 = background_img.resize((1280, 720))
    background_img_0 = ImageTk.PhotoImage(background_img_1)
    logo = Image.open('assets/ui/brawl_cv_logo.png')
    logo_1 = logo.resize((360, aspect_height(360, logo)))
    logo_0 = ImageTk.PhotoImage(logo_1)
    for c in canvas_list:
        c.create_image(0, 0, image=background_img_0, anchor='nw')
        c.create_image(50, 50, image=logo_0, anchor='nw', tag='home')
        if c != canvas_0:
            c.tag_bind('home', '<1>', lambda e: show_canvas(canvas_0))
        c.create_text(40, 700,
                      text="This content is not affiliated with, endorsed, sponsored, or specifically approved by Supercell and Supercell is not responsible for it. For more information see",
                      fill='#fff', font=('Lilita One Fresh', 11), anchor='nw')
        c.create_text(1050, 700, text="Supercell's Fan Content Policy", fill='#fff',
                      font=('Lilita One Fresh', 11, 'underline'), anchor='nw', tag='policy')
        c.tag_bind('policy', '<1>', lambda e: open_url(
            'https://supercell.com/en/fan-content-policy/'))
        if c != canvas_1:
            c.create_text(950, 50, text='Sample', fill='#fff', font=(
                'Lilita One Fresh', 20, 'underline'), anchor='nw', tag='sample')
            c.tag_bind('sample', '<1>', lambda e: show_canvas(canvas_1))
        else:
            c.create_text(950, 50, text='Sample', fill='#fff',
                          font=('Lilita One Fresh', 20), anchor='nw')
        if c != canvas_2:
            c.create_text(1050, 50, text='FAQ', fill='#fff', font=(
                'Lilita One Fresh', 20, 'underline'), anchor='nw', tag='faq')
            c.tag_bind('faq', '<1>', lambda e: show_canvas(canvas_2))
        else:
            c.create_text(1050, 50, text='FAQ', fill='#fff',
                          font=('Lilita One Fresh', 20), anchor='nw')
        if c != canvas_3:
            c.create_text(1120, 50, text='Contributors', fill='#fff', font=(
                'Lilita One Fresh', 20, 'underline'), anchor='nw', tag='contributors')
            c.tag_bind('contributors', '<1>',
                       lambda e: show_canvas(canvas_3))
        else:
            c.create_text(1120, 50, text='Contributors', fill='#fff', font=(
                'Lilita One Fresh', 20), anchor='nw')

    # ========================================Home
    with open('assets/config/config_version.json', 'w') as f:
        json.dump({"version": VERSION}, f)
        f.close()
    response = requests.get(
        "https://api.github.com/repos/Waterdragen/BrawlCV/releases/latest")
    version_latest = response.json()['tag_name']
    version_desc = response.json()['body']
    if VERSION != version_latest:
        show_canvas(canvas_5)

    canvas_0.create_text(50, 160, text='Enter your tag to generate your profile card',
                         fill='#fff', font=('Lilita One Fresh', 20), anchor='nw')
    tag_field_bg = Image.open('assets/ui/tag_field_bg.png')
    tag_field_bg_1 = tag_field_bg.resize(
        (aspect_width(65, tag_field_bg), 65))
    tag_field_bg_0 = ImageTk.PhotoImage(tag_field_bg_1)
    tag_field = tk.Text(canvas_0, width=10, height=1, font=(
        'Lilita One Fresh', 27), bd=0, bg='#fff')
    tag_field.place(x=90, y=220)
    canvas_0.create_image(40, 210, image=tag_field_bg_0, anchor='nw')
    canvas_0.create_text(55, 222, text='#', fill='#000',
                         font=('Lilita One Fresh', 27), anchor='nw')
    search_button = Image.open('assets/ui/search_button.png')
    search_button_1 = search_button.resize(
        (78, aspect_height(78, search_button)))
    search_button_0 = ImageTk.PhotoImage(search_button_1)
    canvas_0.create_image(322, 210, image=search_button_0,
                          anchor='nw', tag='search_button')
    canvas_0.tag_bind('search_button', '<1>', lambda e: show_canvas(canvas_4)
                      if not validation(tag_field.get('1.0', 'end-1c')) else bad_input_err(err_type=ErrCode))

    with open('assets/config/config_tag.json', 'r') as f:
        config_tag = json.load(f)
    has_config = True
    for i in ('stats', 'stats_long', 'ranks', 'avail'):
        if not os.path.isfile(f'assets/config/config_{i}.json'):
            has_config = False
            break
    if config_tag['tag'] != '' and os.path.isfile('profile1.png') and os.path.isfile('profile2.png') and has_config:
        canvas_0.create_text(420, 230, text='Skip...', fill='#fff', font=(
            'Lilita One Fresh', 20, 'underline'), anchor='nw', tag='skip')
        canvas_0.tag_bind(
            'skip', '<1>', lambda e: show_canvas(canvas_4, skip=True))
    canvas_0.create_text(50, 300, text='Where is my tag?', fill='#fff', font=(
        'Lilita One Fresh', 20), anchor='nw')
    tutorial1 = Image.open('assets/ui/tutorial1.png')
    tutorial1_1 = tutorial1.resize((450, aspect_height(450, tutorial1)))
    tutorial1_0 = ImageTk.PhotoImage(tutorial1_1)
    canvas_0.create_image(50, 350, image=tutorial1_0, anchor='nw')
    tutorial2 = Image.open('assets/ui/tutorial2.png')
    tutorial2_1 = tutorial2.resize((450, aspect_height(450, tutorial2)))
    tutorial2_0 = ImageTk.PhotoImage(tutorial2_1)
    canvas_0.create_image(600, 350, image=tutorial2_0, anchor='nw')
    tut_arrow = Image.open('assets/ui/tutorial_arrow.png')
    tut_arrow_1 = tut_arrow.resize((50, aspect_height(50, tut_arrow)))
    tut_arrow_0 = ImageTk.PhotoImage(tut_arrow_1)
    canvas_0.create_image(530, 450, image=tut_arrow_0, anchor='nw')

    # ========================================Sample
    sample1 = Image.open('assets/ui/sample1.png')
    sample1_1 = sample1.resize((620, aspect_height(620, sample1)))
    sample1_0 = ImageTk.PhotoImage(sample1_1)
    canvas_1.create_image(15, 200, image=sample1_0, anchor='nw')
    sample2 = Image.open('assets/ui/sample2.png')
    sample2_1 = sample2.resize((620, aspect_height(620, sample2)))
    sample2_0 = ImageTk.PhotoImage(sample2_1)
    canvas_1.create_image(645, 200, image=sample2_0, anchor='nw')

    # ========================================FAQ
    canvas_2.create_text(50, 140, text='What is Brawl CV?', fill='#fff', font=(
        'Lilita One Fresh', 25), anchor='nw')
    canvas_2.create_text(50, 190, text='Brawl CV is a script that generates your profile card in the mobile game Brawl Stars.',
                         fill='#fff', font=('Lilita One Fresh', 16), anchor='nw')
    canvas_2.create_text(50, 240, text='How does Brawl CV work?',
                         fill='#fff', font=('Lilita One Fresh', 25), anchor='nw')
    canvas_2.create_text(50, 290, text='Just simply enter your player tag and Brawl CV will fetch the Brawl Stars API using the provided tag.',
                         fill='#fff', font=('Lilita One Fresh', 16), anchor='nw')
    canvas_2.create_text(50, 340, text='Why am I getting a Brawl Stats error?',
                         fill='#fff', font=('Lilita One Fresh', 25), anchor='nw')
    canvas_2.create_text(50, 390, text="An error occurred on the Brawl Stats page. Don't worry, you can click the search button to try again.",
                         fill='#fff', font=('Lilita One Fresh', 16), anchor='nw')
    canvas_2.create_text(50, 440, text='My account is lost / hacked / blocked – can you help me?', fill='#fff',
                         font=('Lilita One Fresh', 25), anchor='nw')
    canvas_2.create_text(50, 490, text="I'm sorry to hear that, but I am not related to the game's company. Please refer to the ",
                         fill='#fff', font=('Lilita One Fresh', 16), anchor='nw')
    canvas_2.create_text(817, 490, text="official Brawl Stars support page",
                         fill='#fff', font=('Lilita One Fresh', 16, 'underline'), anchor='nw', tag='official_bs_support')
    canvas_2.tag_bind('official_bs_support', '<1>', lambda e: open_url(
        'https://help.supercellsupport.com/brawl-stars/en/index.html'))
    canvas_2.create_text(1120, 490, text="by Supercell", fill='#fff', font=(
        'Lilita One Fresh', 16), anchor='nw', tag='official_bs_support')

    # ========================================Contributors
    waterdr_pfp = Image.open('assets/ui/waterdragen_pfp.png')
    waterdr_pfp_1 = waterdr_pfp.resize((100, 100))
    waterdr_pfp_0 = ImageTk.PhotoImage(waterdr_pfp_1)
    canvas_3.create_image(50, 140, image=waterdr_pfp_0, anchor='nw', tag='waterdr_pfp')
    canvas_3.tag_bind('waterdr_pfp', '<1>', lambda e: open_url(
        'https://github.com/Waterdragen'))
    canvas_3.create_text(160, 175, text="Waterdragen", fill='#fff', font=(
        'Lilita One Fresh', 22), anchor='nw')
    canvas_3.create_text(50, 260, text="a brawl cv dev. does random brawl stars stuff",
                         fill='#fff', font=('Lilita One Fresh', 16), anchor='nw')
    waterdr_yt = Image.open('assets/ui/youtube_logo.png')
    waterdr_yt_1 = waterdr_yt.resize((50, aspect_height(50, waterdr_yt)))
    waterdr_yt_0 = ImageTk.PhotoImage(waterdr_yt_1)
    canvas_3.create_image(340, 175, image=waterdr_yt_0,
                          anchor='nw', tag='waterdr_yt')
    canvas_3.tag_bind('waterdr_yt', '<1>', lambda e: open_url(
        'https://www.youtube.com/channel/UC9XGyk7-f8S4s8WnLYr2pdQ'))
    waterdr_ig = Image.open('assets/ui/instagram_logo.png')
    waterdr_ig_1 = waterdr_ig.resize((50, 50))
    waterdr_ig_0 = ImageTk.PhotoImage(waterdr_ig_1)
    canvas_3.create_image(400, 167, image=waterdr_ig_0,
                          anchor='nw', tag='waterdr_ig')
    canvas_3.tag_bind('waterdr_ig', '<1>', lambda e: open_url(
        'https://www.instagram.com/waterdragen/'))
    waterdr_bmac = Image.open('assets/ui/buymeacoffee_logo.png')
    waterdr_bmac_1 = waterdr_bmac.resize((45, 45))
    waterdr_bmac_0 = ImageTk.PhotoImage(waterdr_bmac_1)
    canvas_3.create_image(460, 170, image=waterdr_bmac_0,
                          anchor='nw', tag='waterdr_bmac')
    canvas_3.tag_bind('waterdr_bmac', '<1>', lambda e: open_url(
        'https://www.buymeacoffee.com/waterdragen'))
    canvas_3.create_text(50, 320, text="Credits", fill='#fff', font=(
        'Lilita One Fresh', 27), anchor='nw')
    canvas_3.create_text(50, 380, text="cr.is-a.dev", fill='#fff',
                         font=('Lilita One Fresh', 18), anchor='nw')
    canvas_3.create_text(50, 420, text="brawlstats.com", fill='#fff', font=(
        'Lilita One Fresh', 18), anchor='nw')
    rodriguez_moon_pfp = Image.open('assets/ui/rodriguez-moon_pfp.png')
    rodriguez_moon_pfp_1 = rodriguez_moon_pfp.resize((100, 100))
    rodriguez_moon_pfp_0 = ImageTk.PhotoImage(rodriguez_moon_pfp_1)
    canvas_3.create_image(550, 140, image=rodriguez_moon_pfp_0, anchor='nw', tag='rodriguez_moon_pfp')
    canvas_3.create_text(660, 175, text="Rodriguez Moon", fill='#fff', font=(
        'Lilita One Fresh', 22), anchor='nw')
    canvas_3.tag_bind('rodriguez_moon_pfp', '<1>', lambda e: open_url(
        'https://github.com/rodriguez-moon'))

    # ========================================Image Preview
    canvas_4.create_text(50, 140, text='Preview', fill='#fff', font=(
        'Lilita One Fresh', 27), anchor='nw')
    canvas_4.create_text(1260, 150, text='Images saved to computer as profile1.png and profile2.png',
                         fill='#fff', font=('Lilita One Fresh', 16), anchor='ne')
    color_list = []
    for i in range(6):
        color_img = Image.open(f'assets/ui/color_{str(i)}.png')
        color_img1 = color_img.resize((50, aspect_height(50, color_img)))
        color_list.append(ImageTk.PhotoImage(color_img1))
        canvas_4.create_image(
            i * 50 + 230, 138, image=color_list[i], anchor='nw', tag=f'color{i}')
        canvas_4.tag_bind(f'color{i}', '<1>', lambda e: change_color(
            canvas_4) if element_tag1(e) else change_color(canvas_4))

    # ========================================Outdated version
    canvas_5.create_text(50, 140, text='You are using an outdated version of BrawlCV!',
                         fill='#fff', font=('Lilita One Fresh', 27), anchor='nw')
    canvas_5.create_text(50, 200, text='Please go to the', fill='#fff', font=(
        'Lilita One Fresh', 16), anchor='nw')
    canvas_5.create_text(195, 200, text='BrawlCV Github page', fill='#fff', font=(
        'Lilita One Fresh', 16, 'underline'), anchor='nw', tag='update_version')
    canvas_5.create_text(390, 200, text=f'and download the latest release ({version_latest}).', fill='#fff', font=(
        'Lilita One Fresh', 16), anchor='nw')
    canvas_5.tag_bind('update_version', '<1>', lambda e: open_url(
        'https://github.com/Waterdragen/BrawlCV'))
    canvas_5.create_text(50, 240, text='Proceeding may result in program failure.',
                         fill='#fff', font=('Lilita One Fresh', 16), anchor='nw')
    canvas_5.create_text(50, 300, text='Update changes', fill='#fff', font=(
        'Lilita One Fresh', 27), anchor='nw')
    canvas_5.create_text(50, 360, text=version_desc, fill='#fff', font=(
        'Lilita One Fresh', 16), anchor='nw')

    # ========================================Place all Canvas
    for c in canvas_list:
        c.place(x=0, y=0, anchor='nw')  # placing canvas
    Window.mainloop()


if __name__ == '__main__':
    gui()
