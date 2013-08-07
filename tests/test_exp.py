import os
from nose.tools import *
from experiment import exp

def test_img_to_cat():
    cat = "1"
    img = os.path.join(exp.STIM_DIR, 'fruit-{}-1.png'.format(cat))
    assert_equal(cat, exp.img_to_cat(img))

def test_check():
    for label, cats in exp.EXPERIMENT_KEYS.iteritems():
        for img in exp.ALL_IMAGES:
            actual = (exp.img_to_cat(img) in cats)
            check = exp.check_pair(label, img)
            assert_equal(actual, check)

def test_get_pair():
    img, label = exp._get_pair(True)
    assert_true(exp.check_pair(img, label))
