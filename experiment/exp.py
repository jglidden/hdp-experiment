import os
import random
import json

STIM_DIR = 'static/stimuli'
CORRECT_FREQUENCY = .25
with open('key.json') as f:
    EXPERIMENT_KEY = json.load(f)
ALL_CATS = set([i for cat in EXPERIMENT_KEY.values() for i in cat])
ALL_IMGS = [os.path.join(STIM_DIR, fname) for fname in os.listdir(STIM_DIR) if 'prototype' not in fname]
IMGS_BY_CAT = {}
for cat in ALL_CATS:
    IMGS_BY_CAT[cat] = []
    for fname in ALL_IMGS:
        if  img_to_cat(fname) == cat:
            IMGS_BY_CAT[cat].append(fname)
IMGS_BY_LABEL = {}
for label, cats in EXPERIMENT_KEY.iteritems():
    IMGS_BY_LABEL[label] = list(set([img for cat in cats for img in IMGS_BY_CAT[cat]]))

def img_to_cat(img):
    return os.path.split(fname)[1].split('-')[1]


def _gen_pair(show_correct):
    label = random.choice(EXPERIMENT_KEY.keys())
    if show_correct:
        category = random.choice(EXPERIMENT_KEY[label])
        img = random.choice(IMGS_BY_CAT[category])
    else:
        img = random.choice(ALL_IMGS)
    return label, img

def gen_pair():
    show_correct = random.random() < CORRECT_FREQUENCY
    return _gen_pair(show_correct)

def check_pair(label, img):
    actual = (img in IMGS_BY_LABEL[label])
    return actual

