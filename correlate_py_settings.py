import pygame

"""

Settings file

Any value may be set to None and will be asked for upon
running the program.

"""

# Term to look for associations with
term = "Trump"

# Number of bars
bar_count = 15

# Main font
font_size = 15
font = pygame.font.SysFont("calibri", font_size)
font_color = (200, 0, 150)

# Small font
small_font_size = 12
small_font = pygame.font.SysFont("monospace", small_font_size)

# Space around the edges
body_padding = 30

bar_width = 400
# Note: displayed on top of EVERY bar
bar_margin = 10
bar_height = font_size + small_font_size + 1 * 2

main_color = (150, 0, 100)
aux_color = (255, 255, 255)

# Number of datapoints in StatList needed for r^2 to be graphically displayed
sureness_threshold = 15

# How difficult it is for a bar to become bright
# Used in equation rgb_scalar = 2/(1 + e**(-num_datapoints / strictness)) - 1
# when calculating bar color
strictness = 15

"""

Ignore below

"""

# Display every n frames
display_every = 10

bar_padding = int((bar_height - font_size - small_font_size) / 2)
if bar_padding < 0: raise ValueError("Bars too small to contain labels")

scn_width = 2 * body_padding + 2 * bar_width
scn_height = 2 * body_padding + bar_count * (bar_height + bar_margin) + font_size
