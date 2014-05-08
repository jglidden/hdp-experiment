import os
from nose.tools import *
from experiment import exp

def test_img_to_cat():
    cat = "1"
    img = os.path.join(exp.STIM_DIR, 'fruit-{}-2.png'.format(cat))
    img_cat = exp.img_to_cat(img)
    assert_equal(cat, img_cat)


def test_check():
    for label, cats in exp.EXPERIMENT_KEY.iteritems():
        for img in exp.ALL_IMGS:
            actual = (exp.img_to_cat(img) in cats)
            check = exp.check_pair(label, img)
            assert_equal(actual, check)


def test_gen_pair():
    img, label = exp._gen_pair(True)
    assert_true(exp.check_pair(img, label))

    img, label = exp._gen_pair(False)
    assert_false(exp.check_pair(img, label))
