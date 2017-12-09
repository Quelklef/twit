import twitter as tw
import opinion as op
from misc import SortedDict
import pygame
import sys
import log
import math
import itertools as it

pygame.init()
#pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
pygame.event.set_allowed([pygame.QUIT])

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

    def __str__(self):
        return "stat" + super().__str__()


count = -1
BLACK = (0, 0, 0)


def render_once(surface, settings):
    title = settings['font'].render(f"Correlations with '{settings['term']}'", 1, settings['main_color'])
    surface.blit(title, (settings['body_padding'],) * 2 + settings['font'].size(settings['term']))
    pygame.display.flip()


@log.watch_time(0.5)
def render_rs(statlists, surface, settings):
    global count
    count += 1
    if count % settings['display_every'] != 0:
        return

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

    #datapoint_counts = [statlist.length for word, statlist in statlists]
    #max_datapoint_count = max(datapoint_counts) if datapoint_counts else None
    #min_datapoint_count = min(datapoint_counts) if datapoint_counts else None

    for i, (word, statlist) in enumerate(statlists):
        val = statlist.correlation()
        #datapoint_count = datapoint_counts[i]
        datapoint_count = statlist.length

        rgb_scalar = 2 / (1 + math.e ** (-datapoint_count / settings['strictness'])) - 1
        #rgb_scalar = (datapoint_count - min_datapoint_count) / (max_datapoint_count - min_datapoint_count)
        actual_color = (main_color[0] * rgb_scalar, main_color[1] * rgb_scalar, main_color[2] * rgb_scalar)

        y += bar_margin

        pygame.draw.rect(surface, BLACK, (0, y, scn_width, bar_height))  # TODO
        rects.append((0, y, scn_width, bar_height))
        bar_end = y + bar_height

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

        strval = f"{str(val)[:4]} [{datapoint_count}]"
        #strval = str(val)[:4]
        val_label = small_font.render(strval, 1, aux_color)
        val_label_size = small_font.size(strval)

        surface.blit(val_label, (int(midx - val_label_size[0] / 2), y))
        #y += small_font_size

        y = bar_end

    pygame.display.update(rects)


def pygame_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)


def realtime_correlate(query, surface, settings):
    # Yash is the query

    bar_count = settings['bar_count']
    sureness_threshold = settings['sureness_threshold']
    stream = tw.realtime(query)

    # {noun: [(opinion of Yash, opinion of noun)]
    noun_statlist_map = SortedDict(key=lambda k: -abs(noun_statlist_map[k].correlation()))

    for tweet in stream:
        opin = op.opinion(op.get_words(tweet['text']))  # User opinion of Yash
        prof = op.profile(tweet['user']['id'])  # User opinion of everything else; {noun: opinion}

        for noun in prof:
            if noun not in noun_statlist_map:
                noun_statlist_map[noun] = StatList()
            noun_statlist_map.mutate_val(noun, lambda: noun_statlist_map[noun].append((opin, prof[noun])))

        rendered_rs = it.islice(
            (item for item in noun_statlist_map.items() if item[1].length >= sureness_threshold),
            bar_count
        )
        pygame_events()
        render_rs(rendered_rs, surface, settings)
        pygame_events()


def main():
    settings = get_settings()

    scn_width = settings['scn_width']
    scn_height = settings['scn_height']
    term = settings['term']

    surface = pygame.display.set_mode((scn_width, scn_height))

    pygame.display.set_caption(f"Correlations with <{term}>")
    render_once(surface, settings)
    realtime_correlate(term, surface, settings)


if __name__ == "__main__":
    log.logger.info(f"{__file__} main section run.")
    main()
