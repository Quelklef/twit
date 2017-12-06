import twitter as tw
import opinion as op
from collections import defaultdict
from sortedcontainers import SortedDict
import pygame
import sys
import log
import math

pygame.init()

import correlate_py_settings


def get_settings():
    """ Return settings in correlate_py_settings as dict """
    settings = {}

    for setting in correlate_py_settings.__dict__:
        # Ignore magic and hidden attributes
        if setting.startswith('_'):
            continue

        val = correlate_py_settings.__dict__[setting]
        if val is None:
            # Get blank inputs from user
            raw = input(f"{setting}: ")
            try:
                # Eval is fine here.
                # It's being used by end-user with no risks.
                val = eval(raw)
            except Exception:
                val = raw  # type str

        settings[setting] = val

    return settings


def sgn(x):
    if x < 0:
        return -1
    return 1


def unzip(li):
    l1 = []
    l2 = []
    for items in li:
        item1, item2 = items
        l1.append(item1)
        l2.append(item2)
    return l1, l2


class StatList(list):
    """ Subclass of list allowing for calculation of r^2 in O(1) time.
    Should be a list only of 2-tuples of numbers. """

    def __init__(self, *args, **kwargs):
        self.sumx = 0
        self.sumy = 0
        self.sumxy = 0
        self.sumxsq = 0
        self.sumysq = 0
        self.length = 0
        super().__init__(*args, **kwargs)

    def append(self, pair):
        x, y = pair
        self.sumx += x
        self.sumy += y
        self.sumxy += x * y
        self.sumxsq += x ** 2
        self.sumysq += y ** 2
        self.length += 1
        super().append(pair)

    def remove(self, pair):
        x, y = pair
        self.sumx -= x
        self.sumy -= y
        self.sumxy -= x * y
        self.sumxsq -= x ** 2
        self.sumysq -= y ** 2
        self.length -= 1
        super().remove(pair)

    def correlation(self):
        """ Return sgn(r) * (r^2) for this set of data. O(1). """
        if self.length in [0, 1]: return 0  # Special case: no correlation for <2 elements      
        denom = (self.length * self.sumxsq - self.sumx ** 2) * (self.length * self.sumysq - self.sumy ** 2)
        if denom == 0: return 0  # When things don't work, no correlation
        sqrt_num = (self.length * self.sumxy - self.sumx * self.sumy)
        num = sqrt_num ** 2
        val = sgn(sqrt_num) * abs(num / denom)
        return val


def sorted_items(sorteddict):
    for key in sorteddict:
        yield (key, sorteddict[key])


count = 0
BLACK = (0, 0, 0)


def render_once(surface, settings):
    title = settings['font'].render(f"Correlations with '{settings['term']}'", 1, settings['main_color'])
    surface.blit(title, (settings['body_padding'],) * 2 + settings['font'].size(settings['term']))
    pygame.display.flip()


@log.watch_time(0.5)
def render_rs(vals, surface, settings):
    global count
    """ takes list of values (floats) in [-1, 1]
    len(vals) must be equal to the arugment passed to init_gfx """

    font = settings['font']
    font_size = settings['font_size']
    body_padding = settings['body_padding']
    bar_width = settings['bar_width']
    bar_height = settings['bar_height']
    bar_margin = settings['bar_margin']
    bar_padding = settings['bar_padding']
    small_font = settings['small_font']
    #small_font_size = settings['small_font_size']
    #scn_height = settings['scn_height']
    scn_width = settings['scn_width']
    main_color = settings['main_color']
    aux_color = settings['aux_color']

    x = y = 0
    y += body_padding
    midx = scn_width / 2
    rects = []

    counter = font.render(str(count), 1, main_color)
    counter_size = counter.get_size()
    counter_pos = (scn_width - body_padding - counter_size[0], y)
    counter_rect = counter_pos + counter_size
    pygame.draw.rect(surface, BLACK, counter_rect)
    surface.blit(counter, counter_pos)
    rects.append(counter_rect)
    y += counter_size[1]

    x += body_padding
    for word, statlist in vals:
        val = statlist.correlation()
        count = statlist.length

        s = 2 / (1 + math.e ** (-count / settings['strictness'])) - 1
        actual_color = (main_color[0] * s, main_color[1] * s, main_color[2] * s)

        pygame.draw.rect(surface, BLACK, (0, y, scn_width, bar_height))  # TODO
        rects.append((0, y, scn_width, bar_height))
        bar_end = y + bar_height + bar_margin

        scaled = abs(val * bar_width)
        if val < 0:
            bar = (midx - scaled, y, scaled, bar_height)
        else:
            bar = (midx, y, scaled, bar_height)
        pygame.draw.rect(surface, actual_color, bar)
        y += bar_padding

        word_label = font.render(word, 1, aux_color)
        word_label_size = font.size(word)

        surface.blit(word_label, (int(midx - word_label_size[0] / 2), y))
        y += font_size

        strval = f"{str(val)[:4]} [{count}]"
        #strval = str(val)[:4]
        val_label = small_font.render(strval, 1, aux_color)
        val_label_size = small_font.size(strval)

        surface.blit(val_label, (int(midx - val_label_size[0] / 2), y))
        #y += small_font_size

        y = bar_end

    pygame.display.update(rects)
    count += 1


def pygame_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)


@log.watch_time(0.5)
def realtime_correlate(query, surface, settings):
    # Yash is the query

    bar_count = settings['bar_count']
    sureness_threshold = settings['sureness_threshold']
    stream = tw.realtime(query)

    # {noun: [(opinion of Yash, opinion of noun)]
    vals = defaultdict(StatList)

    # {noun: correlation}
    _rs = dict()
    # {noun: StatList}
    rs = SortedDict(lambda k: -abs(_rs[k]))

    def add_r(k, v):
        """ Use instead of rs[k] = v, but don't ask why. """
        _rs[k] = v.correlation()
        rs[k] = v

    for tweet in stream:
        opin = op.opinion(op.get_words(tweet['text']))  # User opinion of Yash
        prof = op.profile(tweet['user']['id'])  # User opinion of everything else; {noun: opinion}

        for noun in prof:
            vals[noun].append((opin, prof[noun]))
            if noun in rs: del rs[noun]  # Needed, but I don't know why
            add_r(noun, vals[noun])

        rendered_rs = []
        count_desire = bar_count
        for item in sorted_items(rs):
            if count_desire == 0:
                break

            noun, r = item
            if vals[noun].length >= sureness_threshold:
                rendered_rs.append(item)
                count_desire -= 1

        pygame_events()
        render_rs(rendered_rs, surface, settings)
        pygame_events()


def main():
    settings = get_settings()

    scn_width = settings['scn_width']
    scn_height = settings['scn_height']
    term = settings['term']

    surface = pygame.display.set_mode((scn_width, scn_height))

    pygame.display.set_caption("Correlations with '{}'".format(term))
    render_once(surface, settings)
    realtime_correlate(term, surface, settings)


if __name__ == "__main__":
    main()