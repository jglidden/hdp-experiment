import os
import random
import json
import sys
from glob import glob

SCRIPTDIR = os.path.dirname(__file__)

STIM_PREFIX = 'static/stimuli'
STIM_DIR = os.path.join(SCRIPTDIR, STIM_PREFIX)
KEY_FILE = os.path.join(SCRIPTDIR, os.path.join(STIM_PREFIX, 'key.json'))
CORRECT_FREQUENCY = .25
with open(KEY_FILE) as f:
    EXPERIMENT_KEY = json.load(f)
ALL_CATS = set([i for cat in EXPERIMENT_KEY.values() for i in cat])
ALL_IMGS = [os.path.join(STIM_PREFIX, os.path.split(fname)[1])
            for fname in glob(os.path.join(STIM_DIR, '*.png')) if 'prototype' not in fname]
random.shuffle(ALL_IMGS)
ALL_IMGS = ALL_IMGS[:6]
TRUE_LINKS = []

def img_to_cat(img):
    return os.path.split(img)[1].split('-')[1]

IMGS_BY_CAT = {}
for cat in ALL_CATS:
    IMGS_BY_CAT[cat] = []
    for fname in ALL_IMGS:
        if  img_to_cat(fname) == cat:
            IMGS_BY_CAT[cat].append(fname)
IMGS_BY_LABEL = {}
for label, cats in EXPERIMENT_KEY.iteritems():
    IMGS_BY_LABEL[label] = list(set([img for cat in cats for img in IMGS_BY_CAT[cat]]))

LABELS_BY_CAT = {}
for label, cats in EXPERIMENT_KEY.iteritems():
    for cat in cats:
        if cat not in LABELS_BY_CAT:
            LABELS_BY_CAT[cat] = []
        LABELS_BY_CAT[cat].append(label)


def gen_pairs():
    labels = EXPERIMENT_KEY.keys()
    random.shuffle(labels)
    pairs = []
    for label in labels:
        if random.random() < CORRECT_FREQUENCY:
            category = random.choice(EXPERIMENT_KEY[label])
            img = random.choice(IMGS_BY_CAT[category])
        else:
            img = random.choice(ALL_IMGS)
        pairs.append((label, img))
    return pairs

def gen_label(img):
    show_correct = random.random() < CORRECT_FREQUENCY
    cat = img_to_cat(img)
    if show_correct:
        label = random.choice(LABELS_BY_CAT[cat])
    else:
        label = random.choice(EXPERIMENT_KEY.keys())
    return label
    

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

def check_links(links):
    return set(links) == set(TRUE_LINKS)

def process_links(links):
    processed_links = []
    for link in links:
        if link['right']:
            parent = link['source']
            child = link['target']
        elif link['left']:
            parent = link['target']
            child = link['source']
        processed_links.append((parent, child))
    return processed_links
            
