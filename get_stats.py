import requests
import re
from PIL import Image, ImageDraw, ImageFont
from emot.emo_unicode import UNICODE_EMOJI
from bs4 import BeautifulSoup

waterdr_key = {
    'Accept': 'application/json',
    'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjhmNGIyOTgwLWIzZGUtNDNlYi05MDNlLTU2MjlhOGViZjQ4ZSIsImlhdCI6MTY1NzQ0NzgyMCwic3ViIjoiZGV2ZWxvcGVyLzFkYmEwNTg2LTZjMDMtNzRlMS00MmMxLWY3NWVjZmMyMjk2ZiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTEyLjExOC4yNDUuMTUwIl0sInR5cGUiOiJjbGllbnQifV19.TeWXqlNlV4AL5WFyz_WECJgZbCQXCmerPbTfAjDr9YjMnUf_dF5qnAPo4Kgs_biJOnZYfZPhBeQgYnerBu_qgQ'
}
global_tag = 'GJL0GPG0'
TEXT_FONT = 'fonts/LilitaOne-Fresh4.ttf'
IOS_FONT = 'fonts/AppleColorEmoji.ttf'

def validation(player_tag):
    if player_tag == '':
        raise Exception(ValueError,'Player tag is empty')
    for i in player_tag:
        if str(i).upper() not in ['P','Y','L','Q','G','R','J','C','U','V','0','2','8','9']:
            raise Exception(ValueError, 'Player tag must only consist of P,Y,L,Q,G,R,J,C,U,V,0,2,8,9')

def get_user(player_tag):
    url = 'https://api.brawlstars.com/v1/players/%23'+player_tag.upper()
    response = requests.get(url, headers = waterdr_key)
    if response.status_code in [400,403,404,429,500,503]:
        raise Exception(response.status_code)
    user_json = response.json()
    name = user_json['name']
    icon_id = user_json['icon']['id']
    trophies = user_json['trophies']
    highest_trophies = user_json['highestTrophies']
    exp_level = user_json['expLevel']
    x3v3_victories = user_json['3vs3Victories']
    solo_victories = user_json['soloVictories']
    duo_victories = user_json['duoVictories']
    in_club = True
    try:
        club_name = user_json['club']['name']
        club_tag = user_json['club']['tag']
        url = 'https://api.brawlstars.com/v1/clubs/%23' + club_tag[1:len(club_tag)]
        response = requests.get(url, headers=waterdr_key)
        if response.status_code in [400, 403, 404, 429, 500, 503]:
            raise Exception(response.status_code)
        club_json = response.json()
        club_badge_id = str(club_json['badgeId'])
        club_badge = club_badge_id + '.png'
    except KeyError:
        club_name = 'Not in a Club'
        club_tag = ''
        club_badge = '0.png'
        in_club = False
    brawlers_owned = len(user_json['brawlers'])
    sp_owned = 0
    for i in user_json['brawlers']:
        sp_owned += len(i['starPowers'])
    gadget_owned = 0
    for i in user_json['brawlers']:
        gadget_owned += len(i['gadgets'])
    basic_profile_list = {
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
    return basic_profile_list

def get_user_long(player_tag):
    url = 'https://api.brawlstars.com/v1/players/%23'+player_tag.upper()
    response = requests.get(url, headers = waterdr_key)
    if response.status_code in [400,403,404,429,500,503]:
        raise Exception(response.status_code)
    user_json = response.json()
    return user_json

def get_pl(player_tag):
    url = 'https://brawlstats.com/profile/' + player_tag.upper()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }
    req = requests.get(url, headers = headers)
    if req.status_code in [400, 403, 404, 429, 500, 503]:
        raise Exception(req.status_code)
    soup = BeautifulSoup(req.text, 'html.parser')
    temp_ranks = []
    if soup.find('div', {'class': '_230Gh9q1rJmb0YFOn6qXf5'}) is not None:
        raise Exception('Brawl Stats unknown error')
    for item in soup.find_all('img', {'class': 'DPUFH-EhiGBBrkki4Gsaf'}): temp_ranks.append(item['src'])
    challenge_attrs = soup.find_all('div', {'class': 'mo25VS9slOfRz6jng3WTf'})
    challenge_wins = int(challenge_attrs[10].text)
    ranks = []
    for item in temp_ranks:
        for s in re.findall(r'\d+', item):
            if s.isdigit():
                ranks.append(int(s))
    ranks.append(challenge_wins)
    return ranks

def get_official(code=0):
    url = 'https://api.brawlstars.com/v1/brawlers'
    response = requests.get(url, headers=waterdr_key)
    if response.status_code in [400, 403, 404, 429, 500, 503]:
        raise Exception(response.status_code)
    official_json = response.json()
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
    gadget_disabled = 2
    gadget_available -= gadget_disabled
    official_list = [brawler_available, sp_available, gadget_available]
    sp_list = []
    for i in official_json['items']:
        temp = []
        temp.append(i['id'])
        for j in range(2):
            try:
                temp.append(i['starPowers'][j]['id'])
            except IndexError:
                pass
        sp_list.append(temp)
        del temp
    gad_list = []
    for i in official_json['items']:
        temp = []
        temp.append(i['id'])
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
        draw.text((x-2, y-2), text, font=ft, fill=color)
        draw.text((x+2, y-2), text, font=ft, fill=color)
        draw.text((x-2, y+2), text, font=ft, fill=color)
        draw.text((x+2, y+2), text, font=ft, fill=color)
    draw.text((x, y+10), text, font=ft, fill=color)

def draw_text(draw, x, y, text, ft):
    w = int(draw.textlength(text, font=ft))
    draw.text(((x-w)/2, y), text, font=ft)

def sort_json(data, key, desc = False):
    sorted_json = sorted(data, key=lambda x:x[key], reverse=desc)
    return sorted_json
def search_json(data, field, key, field2):
    for i in data:
        if str(i[field]) == str(key):
            return i[field2]
def center_img(x, y, img):
    w = img.width
    h = img.height
    coord = (int(x-w/2), int(y-h/2))
    return coord

def two_pt_tuple(x, y, width, height):
    coord = [(x, y),(x+width,y+height)]
    return coord

def place_image1():
    bs_font_0 = ImageFont.truetype(TEXT_FONT, 90)
    bs_font_1 = ImageFont.truetype(TEXT_FONT, 60)
    bs_font_2 = ImageFont.truetype(TEXT_FONT, 45)
    bs_font_3 = ImageFont.truetype(TEXT_FONT, 38)
    background_img = Image.open('assets/background/0.png').convert('RGBA')
    background_img_0 = background_img.resize((2048,aspect_height(2048,background_img)))
    draw = ImageDraw.Draw(background_img_0)
    try:
        player_icon = Image.open('assets/player_icon/{}.png'.format(str(global_stats['icon_id']))).convert('RGBA')
    except FileNotFoundError:
        player_icon = Image.open('assets/player_icon/0.png').convert('RGBA')
    player_icon_0 = player_icon.resize((110,aspect_height(110,player_icon)))
    #draw_border(draw, 170, 35, '{}'.format(str(global_stats['name'])), bs_font_0)
    #draw.text((170, 35), '{}'.format(str(global_stats['name'])), font=bs_font_0)
    background_img_0.paste(place_text(global_stats['name'], 90), (170, 35-90//2), place_text(global_stats['name'], 90))
    #draw_border(draw, 170, 165, '{}'.format(str(global_stats['club_name'])), bs_font_1)
    #draw.text((170, 165), '{}'.format(str(global_stats['club_name'])), font=bs_font_1)
    background_img_0.paste(place_text(global_stats['club_name'], 60), (170, 165-60//2), place_text(global_stats['club_name'], 60))
    club_badge = Image.open('assets/club_badge/'+global_stats['club_badge']).convert('RGBA')
    club_badge_0 = club_badge.resize((90,aspect_height(90,club_badge)))
    stats_table = Image.open('assets/stats/stats_table.png').convert('RGBA')
    stats_table_0 = stats_table.resize((1100,aspect_height(1100,stats_table)))
    background_img_0.paste(player_icon_0,(30,30), player_icon_0)
    background_img_0.paste(club_badge_0,(40,160), club_badge_0)
    background_img_0.paste(stats_table_0,(30,270), stats_table_0)
    draw_text(draw, 543, 353, '{}'.format(str(global_stats['trophies'])), bs_font_2)
    draw_text(draw, 1233, 353, '{}'.format(str(global_stats['highest_trophies'])), bs_font_2)
    draw_text(draw, 1923, 353, '{}'.format(str(global_stats['exp_level'])), bs_font_2)
    draw_text(draw, 543, 493, '{}'.format(str(global_stats['x3v3_victories'])), bs_font_2)
    draw_text(draw, 1233, 493, '{}'.format(str(global_stats['solo_victories'])), bs_font_2)
    draw_text(draw, 1923, 493, '{}'.format(str(global_stats['duo_victories'])), bs_font_2)
    solo_league = Image.open('assets/league_icon/ranked_ranks_l_{}.png'.format(str(global_ranks[0]))).convert('RGBA')
    solo_league_0 = solo_league.resize((170,aspect_height(170,solo_league)))
    team_league = Image.open('assets/league_icon/ranked_ranks_l_{}.png'.format(str(global_ranks[1]))).convert('RGBA')
    team_league_0 = team_league.resize((170, aspect_height(170, team_league)))
    club_league = Image.open('assets/league_icon/club_ranks_l_{}.png'.format(str(global_ranks[2]))).convert('RGBA')
    club_league_0 = club_league.resize((170, aspect_height(170, club_league)))
    background_img_0.paste(solo_league_0,(185, 616), solo_league_0)
    background_img_0.paste(team_league_0, (530, 616), team_league_0)
    background_img_0.paste(club_league_0, (875, 616), club_league_0)
    draw_text(draw, 543, 773, '{}/{}'.format(str(global_stats['brawlers_owned']),str(avail_official[0])), bs_font_2)
    draw_text(draw, 1233, 773, '{}/{}'.format(str(global_stats['sp_owned']),str(avail_official[1])), bs_font_2)
    draw_text(draw, 1923, 773, '{}/{}'.format(str(global_stats['gadgets_owned']),str(avail_official[2])), bs_font_2)
    draw_text(draw, 1233, 913, '{}'.format(str(global_ranks[3])), bs_font_2)
    stats_sorted = sort_json(global_stats_long['brawlers'], 'highestTrophies', desc=True)
    brawler_override = '16000058' #ID
    if brawler_override == '':
        try:
            brawler_3d = Image.open('assets/brawler_3d/{}.png'.format(str(stats_sorted[0]['id']))).convert('RGBA')
        except FileNotFoundError:
            brawler_3d = Image.open('assets/brawler_3d/0.png').convert('RGBA')
        brawler_3d_0 = brawler_3d.resize((1800, aspect_height(1800, brawler_3d)))
        brawler_rank = Image.open('assets/rank_icon/{}.png'.format(stats_sorted[0]['rank'])).convert('RGBA')
        brawler_rank_0 = brawler_rank.resize((100, aspect_height(100, brawler_rank)))
        stats_tr = stats_sorted[0]['trophies']
        stats_htr = stats_sorted[0]['highestTrophies']
        stats_sp = stats_sorted[0]['starPowers']
        stats_gad = stats_sorted[0]['gadgets']
    else:
        try:
            brawler_3d = Image.open('assets/brawler_3d/{}.png'.format(str(brawler_override))).convert('RGBA')
        except FileNotFoundError:
            brawler_3d = Image.open('assets/brawler_3d/0.png').convert('RGBA')
        brawler_3d_0 = brawler_3d.resize((1800, aspect_height(1800, brawler_3d)))
        brawler_rank = Image.open('assets/rank_icon/{}.png'.format(search_json(stats_sorted, 'id', brawler_override, 'rank'))).convert('RGBA')
        brawler_rank_0 = brawler_rank.resize((100, aspect_height(100, brawler_rank)))
        stats_tr = search_json(stats_sorted, 'id', brawler_override, 'trophies')
        stats_htr = search_json(stats_sorted, 'id', brawler_override, 'highestTrophies')
        stats_sp = search_json(stats_sorted, 'id', brawler_override, 'starPowers')
        stats_gad = search_json(stats_sorted, 'id', brawler_override, 'gadgets')

    trophy_container = Image.open('assets/stats/container.png').convert('RGBA')
    trophy_container_0 = trophy_container.resize((300, aspect_height(210 , trophy_container)))
    trophy = Image.open('assets/stats/trophies.png').convert('RGBA')
    trophy_0 = trophy.resize((50, aspect_height(50, trophy)))
    background_img_0.paste(brawler_3d_0, (250, 100), brawler_3d_0)
    background_img_0.paste(trophy_container_0, (1220, 80), trophy_container_0)
    background_img_0.paste(brawler_rank_0, (1160, 60), brawler_rank_0)
    background_img_0.paste(trophy_0, (1270, 95), trophy_0)
    draw.text((1320, 95), '{}/{}'.format(str(stats_tr),str(stats_htr)), font=bs_font_3)
    slot = []
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
    for i in range(len(slot)//2):
        if slot[i*2+1] == 'sp':
            power_bg = Image.open('assets/stats/star-power-blank.png').convert('RGBA')
            power_bg_0 = power_bg.resize((80, aspect_height(80, power_bg)))
            background_img_0.paste(power_bg_0, (1540+90*i, 75), power_bg_0)
            try:
                power_fore = Image.open('assets/star_powers/{}.png'.format(slot[i*2])).convert('RGBA')
            except FileNotFoundError:
                if brawler_override == '':
                    temp = search_sp(get_official(code=1), stats_sorted[0]['id'], int(slot[i*2]))
                else:
                    temp = search_sp(get_official(code=1), int(brawler_override), int(slot[i*2]))
                try:
                    power_fore = Image.open('assets/star_powers/sp{}.png'.format(str(temp))).convert('RGBA')
                except FileNotFoundError:
                    power_fore = Image.open('assets/star_powers/sp1.png').convert('RGBA')
        else:
            power_bg = Image.open('assets/stats/gadget-blank.png').convert('RGBA')
            power_bg_0 = power_bg.resize((80, aspect_height(80, power_bg)))
            background_img_0.paste(power_bg_0, (1540+90*i, 75), power_bg_0)
            try:
                power_fore = Image.open('assets/gadgets/{}.png'.format(slot[i * 2])).convert('RGBA')
            except FileNotFoundError:
                if brawler_override == '':
                    temp = search_sp(get_official(code=2), stats_sorted[0]['id'], int(slot[i*2]))
                else:
                    temp = search_sp(get_official(code=2), int(brawler_override), int(slot[i*2]))
                try:
                    power_fore = Image.open('assets/gadgets/gad{}.png'.format(str(temp))).convert('RGBA')
                except FileNotFoundError:
                    power_fore = Image.open('assets/gadgets/gad1.png').convert('RGBA')
        if power_fore.width > power_fore.height:
            power_fore_0 = power_fore.resize((38, aspect_height(38, power_fore)))
        else:
            power_fore_0 = power_fore.resize((aspect_width(38, power_fore), 38))
        background_img_0.paste(power_fore_0, center_img(1580+90*i, 115, power_fore_0), power_fore_0)
    background_img_0.save('profile1.png')
def place_image2():
    bs_font_0 = ImageFont.truetype(TEXT_FONT, 90)
    bs_font_1 = ImageFont.truetype(TEXT_FONT, 60)
    #bs_font_2 = ImageFont.truetype('fonts/LilitaOne-Regular.ttf', 45)
    background_img = Image.open('assets/background/plain-0.png').convert('RGBA')
    background_img_0 = background_img.resize((2048, aspect_height(2048, background_img)))
    draw = ImageDraw.Draw(background_img_0)
    try:
        player_icon = Image.open('assets/player_icon/{}.png'.format(str(global_stats['icon_id']))).convert('RGBA')
    except FileNotFoundError:
        player_icon = Image.open('assets/player_icon/0.png').convert('RGBA')
    player_icon_0 = player_icon.resize((110, aspect_height(110, player_icon)))
    club_badge = Image.open('assets/club_badge/' + global_stats['club_badge']).convert('RGBA')
    club_badge_0 = club_badge.resize((90, aspect_height(90, club_badge)))
    #draw_border(draw, 170, 35, '{}'.format(str(global_stats['name'])), bs_font_0)
    #draw.text((170, 35), '{}'.format(str(global_stats['name'])), font=bs_font_0)
    background_img_0.paste(place_text(global_stats['name'], 90), (170, 35 - 90 // 2),place_text(global_stats['name'], 90))
    #draw_border(draw, 170, 165, '{}'.format(str(global_stats['club_name'])), bs_font_1)
    #draw.text((170, 165), '{}'.format(str(global_stats['club_name'])), font=bs_font_1)
    background_img_0.paste(place_text(global_stats['club_name'], 60), (170, 165 - 60 // 2),place_text(global_stats['club_name'], 60))
    background_img_0.paste(player_icon_0, (30, 30), player_icon_0)
    background_img_0.paste(club_badge_0, (40, 160), club_badge_0)
    stats_sorted = sort_json(global_stats_long['brawlers'], 'highestTrophies', desc=True)
    pos = 0
    colors = [(62,50,122),(195,55,68),(83,186,117),(185,72,238),(97,168,234),(216,152,83),(129,133,182),(198,93,45)]
    for i in stats_sorted:
        img_src = 'assets/portraits/'+str(i['id'])+'.png'
        try:
            brawler_img = Image.open(img_src).convert('RGBA')
        except FileNotFoundError:
            brawler_img = Image.open('assets/portraits/0.png').convert('RGBA')
        brawler_img_0 = brawler_img.resize((aspect_width(99, brawler_img),99))
        brawler_rank = Image.open('assets/rank_icon/'+str(i['rank'])+'.png').convert('RGBA')
        brawler_rank_0 = brawler_rank.resize((82, aspect_height(82, brawler_rank)))
        if i['rank'] == 35:
            rank_color = colors[0]
        elif i['rank'] >= 30:
            rank_color = colors[1]
        elif i['rank'] >= 25:
            rank_color = colors[2]
        elif i['rank'] >= 20:
            rank_color = colors[3]
        elif i['rank'] >= 15:
            rank_color = colors[4]
        elif i['rank'] >= 10:
            rank_color = colors[5]
        elif i['rank'] >= 5:
            rank_color = colors[6]
        else:
            rank_color = colors[7]
        if pos < 5:
            draw.rectangle(two_pt_tuple((pos % 5 + 5)*222-193, (pos // 5 + 1)*114+37, 212, 104), fill=rank_color, outline='black', width=3)
            #draw.rectangle(two_pt_tuple((pos % 5 + 4)*250-220, (pos // 5 + 1)*102+57, 242, 95), fill=rank_color, outline='black', width=3)
            background_img_0.paste(brawler_img_0, ((pos % 5 + 5)*222-190 , (pos // 5 + 1)*114+40), brawler_img_0)
            background_img_0.paste(brawler_rank_0, ((pos % 5 + 5)*222-73, (pos // 5 + 1)*114+43), brawler_rank_0)
        else:
            draw.rectangle(two_pt_tuple(((pos - 5) % 9 + 1)*222-193, ((pos - 5) // 9 + 2)*114+37, 212, 104), fill=rank_color, outline='black', width=3)
            #draw.rectangle(two_pt_tuple(((pos - 5) % 8 + 1)*250-220, ((pos - 5) // 8 + 2)*102+57, 242, 95), fill=rank_color, outline='black', width=3)
            background_img_0.paste(brawler_img_0, (((pos-5) % 9 + 1)*222-190, ((pos-5) // 9 + 2)*114+40), brawler_img_0)
            background_img_0.paste(brawler_rank_0, (((pos-5) % 9 + 1)*222-73, ((pos-5) // 9 + 2)*114+43), brawler_rank_0)
        #print(i['name'], str(i['highestTrophies']), str(i['rank']), sep='  ')
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
            draw_border(draw, 0+text_width, 69, i, ft=apple_font, border=False)
            draw.text((0+text_width, 69), i, font=apple_font, embedded_color=True)
            text_width += int(draw.textlength(i, font=apple_font))
        else:
            draw_border(draw, 0+text_width, 69, i, ft=text_font)
            draw.text((0+text_width, 69), i, font=text_font, embedded_color=True)
            text_width += int(draw.textlength(i, font=text_font))
    background_img_0 = background_img.resize((aspect_width(size*2, background_img), size*2))
    return background_img_0

def is_emoji(s):
    return s in UNICODE_EMOJI

def uni_decode(s):
    for i in str(s):
        print('U+{:X}'.format(ord(i)), is_emoji(i))
def search_sp(data, brawler_id, sp_id):
    for i in data:
        if i[0] == brawler_id:
            for j in range(2):
                try:
                    if i[j+1] == sp_id:
                        return j+1
                except IndexError:
                    return None
    return None

validation(global_tag)
global_stats = get_user(global_tag)
global_stats_long = get_user_long(global_tag)
global_ranks = get_pl(global_tag)
avail_official = get_official()
'''print(global_stats)
print(global_ranks)
print(global_official)'''
place_image1()
place_image2()