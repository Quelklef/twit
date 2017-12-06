import twitter as tw
import opinion as op
from collections import defaultdict
from sortedcontainers import SortedDict
import pygame

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
    small_font = settings['small_font']
    small_font_size = settings['small_font_size']
    bar_color = settings['bar_color']
    font_color = settings['font_color']
    small_font_color = settings['small_font_color']

    pygame.draw.rect(surface, (0, 0, 0), (0, 0, scn_width, scn_height))

    counter = font.render(str(count), 1, bar_color)
    surface.blit(counter, (body_padding, body_padding - font_size))

    title = font.render(term, 1, bar_color)
    surface.blit(title, (body_padding, scn_height - body_padding + 5))

    pygame.draw.rect(surface, bar_color, (body_padding, body_padding - 1, scn_width - 2 * body_padding, 1))
    pygame.draw.rect(surface, bar_color, (body_padding, scn_height - body_padding, scn_width - 2 * body_padding, 1))

    x = body_padding
    for word, val in vals:
        bar_color = (int(abs(val) ** 0.2 * 255), 0, 180)

        if val < 0:
            rect = (x, scn_height / 2, bar_width, abs(val) * bar_height)
        else:
            rect = (x, scn_height / 2 - val * bar_height, bar_width, abs(val) * bar_height)
        pygame.draw.rect(surface, bar_color, rect)

        label = font.render(word, 1, font_color)
        surface.blit(pygame.transform.rotate(label, 90), (x, body_padding + 5))

        rlabel = small_font.render(str(val)[:4], 1, small_font_color)
        if val > 0:
            surface.blit(rlabel, (1 + x, scn_height / 2 - sgn(val) * small_font_size - 5))
        else:
            surface.blit(rlabel, (1 + x, scn_height / 2 + 5))

        x += bar_width + bar_margin

    pygame.display.flip()  # TODO
    count += 1


def realtime_correlate(query, surface, settings):
    # Yash is the query

    bar_count = settings['bar_count']
    sureness_threshold = settings['sureness_threshold']
    stream = tw.realtime(query)

    # {noun: [(opinion of Yash, opinion of noun)]
    vals = defaultdict(StatList)

    _rs = dict()
    # {noun: sgn(r) * (r^2)}
    rs = SortedDict(lambda k: -abs(_rs[k]))

    def add_r(k, v):
        """ Use instead of rs[k] = v, but don't ask why. """
        _rs[k] = v
        rs[k] = v

    run = True
    for tweet in stream:
        if not run: break
        opin = op.opinion(op.get_words(tweet['text']))  # User opinion of Yash
        prof = op.profile(tweet['user']['id'])  # User opinion of everything else; {noun: opinion}
        prof.pop(query, None)  # Don't track user opinion of Yash in profile

        for noun in prof:
            vals[noun].append((opin, prof[noun]))

            if noun in rs:
                del rs[noun]
            add_r(noun, vals[noun].correlation())

        rendered_rs = []
        count_desire = bar_count
        for item in sorted_items(rs):
            noun, r = item
            if vals[noun].length >= sureness_threshold:
                rendered_rs.append(item)
                count_desire -= 1
                if count_desire == 0:
                    break

        render_rs(rendered_rs, surface, settings)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


if __name__ == "__main__":
    settings = get_settings()

    scn_width = settings['scn_width']
    scn_height = settings['scn_height']
    term = settings['term']

    surface = pygame.display.set_mode((scn_width, scn_height))

    pygame.display.set_caption("Correlations with '{}'".format(term))
    realtime_correlate(term, surface, settings)
