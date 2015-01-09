import numpy
import csv
import json

trees = json.load(open('results/trees.json'))
true = json.load(open('results/true_tree.json'))

true_positives = []
true_negatives = []

for session, user_trees in trees.iteritems():
    session = int(session)
    for user, trees in user_trees.iteritems():
        for block, tree in enumerate(trees):
            if tree is None:
                continue
            if user == 'ASTVV4I4O4S5X':
                continue
            flat_tree = numpy.array(tree).reshape((144,))
            flat_true = numpy.array(true).reshape((144,))

            zipped = zip(flat_tree, flat_true)

            true_edges = [user_adj for (user_adj, actual_adj) in zipped if actual_adj]
            false_edges = [not user_adj for (user_adj, actual_adj) in zipped if not actual_adj]

            true_positive_count = float(sum(true_edges))
            true_negative_count = float(sum(false_edges))

            true_positives.append([user, session, block, true_positive_count])
            true_negatives.append([user, session, block, true_negative_count])

tp = csv.writer(open('results/true_positives.csv', 'w'), delimiter='\t')
tp_cols = ['user', 'session', 'block', 'tp_count']
tp.writerows(true_positives)

tn = csv.writer(open('results/true_negatives.csv', 'w'), delimiter='\t')
tn_cols = ['user', 'session', 'block', 'tn_count']
tn.writerows(true_negatives)

scores = json.load(open('results/scores.json'))
scores_csv = csv.writer(open('results/scores.csv', 'w'), delimiter='\t')
scores_cols = ['user', 'session', 'block', 'pct_correct']
scores_csv.writerows(scores)

import pandas
tp_df = pandas.DataFrame(true_positives, columns=tp_cols)
score_df = pandas.DataFrame(scores, columns=scores_cols)

joined = tp_df.merge(score_df, right_on=tp_cols[:-1], left_on=scores_cols[:-1], how='inner')
joined = joined.reset_index()
joined['tp_rate'] = joined['tp_count'] / float(sum(flat_true))
joined[['pct_correct', 'tp_rate']].to_csv('results/joined.csv', sep='\t', index=False, header=False)
