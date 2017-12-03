
import twitter as tw
import opinion as op
from collections import defaultdict
from sortedcontainers import SortedDict
from misc import Avg
import itertools as it

def sgn(x):
    if x < 0: return -1
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
        if abs(val) > 1: print(val, self)
        return val

def sorted_items(sorteddict):
    for key in sorteddict:
        yield (key, sorteddict[key])

import pygame

count = 0

def render_rs(vals):
    global count
    """ takes list of values (floats) in [-1, 1]
    len(vals) must be equal to the arugment passed to init_gfx """
    bar_color = (255, 0, 100)
    font_color = (255, 255, 255)
   
    pygame.draw.rect(screen, (0,0,0), (0, 0, scn_width, scn_height))

    counter = font.render(str(count), 1, bar_color)
    screen.blit(counter, (body_padding, body_padding - font_size))

    title = font.render(term, 1, bar_color)
    screen.blit(title, (body_padding, scn_height - body_padding + 5))

    pygame.draw.rect(screen, bar_color, (body_padding, body_padding - 1, scn_width - 2 * body_padding, 1))
    pygame.draw.rect(screen, bar_color, (body_padding, scn_height - body_padding, scn_width - 2 * body_padding, 1))

    x = body_padding
    rects = []
    for word, val in vals:
        if val < 0: rect = (x, scn_height / 2, bar_width, abs(val) * bar_height)
        else: rect = (x, scn_height / 2 - val * bar_height, bar_width, abs(val) * bar_height)
        pygame.draw.rect(screen, bar_color, rect)

        label = font.render(word, 1, font_color)
        screen.blit(label, (x, scn_height / 2 + ((sgn(val) * font_size) if val < 0 else 0) ))
        
        x += bar_width + bar_margin

    pygame.display.flip()
    count += 1

def init_gfx(nvals):
    pygame.init()

    global font, font_size
    font_size = 20
    font = pygame.font.SysFont("calibri", font_size)

    """ Janky quick fix: global vars b.c no vim copy-paste knowledge """

    global body_padding, bar_width, bar_margin, bar_height
    body_padding = 30
    bar_width = 80
    bar_margin = 10
    bar_height = 50

    global scn_width, scn_height
    scn_width = 2 * body_padding + nvals * bar_width + (nvals - 1) * bar_margin
    scn_height = 2 * body_padding + 2 * bar_height

    global screen
    screen = pygame.display.set_mode((scn_width, scn_height))

def realtime_correlate(query):
    # Yash is the query

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
        opin = op.opinion(op.get_words(tweet.text))  # User opinion of Yash
        user = tweet.user
        prof = op.profile(user)  # User opinion of everything else; {noun: opinion}
        prof.pop(query, None)  # Don't track user opinion of Yash in profile
       
        for noun in prof:
            vals[noun].append((opin, prof[noun]))

            if noun in rs:
                del rs[noun]
            add_r(noun, vals[noun].correlation())
        
        rendered_rs = []
        count_desire = nvals
        for item in sorted_items(rs):
            noun, r = item
            if vals[noun].length > 10:
                rendered_rs.append(item)
                count_desire -= 1
                if count_desire == 0:
                    break

        render_rs(rendered_rs)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

sureness_threshold = 15  # Number of datapoints in StatList needed for r^2 to be graphically displayed
nvals = 10

if __name__ == "__main__":
    global term
    term = input('Term? ')
    init_gfx(nvals)
    pygame.display.set_caption("Correlations with '{}'".format(term))
    realtime_correlate(term)



