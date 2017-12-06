import pygame

"""

Settings file

Any value may be set to None and will be asked for upon
running the program.

"""

# Term to look for associations with
term = "Trump"

# Number of bars
bar_count = 40

# Main font
font_size = 20
font = pygame.font.SysFont("calibri", font_size)
font_color = (255, 255, 255)

# Small font
small_font_size = 9
small_font = pygame.font.SysFont("monospace", small_font_size)
small_font_color = (255, 255, 255)

# Space around the edges
body_padding = 30

bar_width = int(font_size * 1.2)
bar_margin = 5
bar_height = 150
bar_color = (255, 0, 200)

# Number of datapoints in StatList needed for r^2 to be graphically displayed
sureness_threshold = 15

"""

Ignore below

"""

scn_width = 2 * body_padding + bar_count * bar_width + (bar_count - 1) * bar_margin
scn_height = 2 * body_padding + 2 * bar_height