"""
Reads in a groudtruth for the events collection and produces precison / recall values
for a run of an event detection system
"""

"""
There is literally some horrible, horrible code here. Do yourself a favour and stop reading now...
This was written as a run once and throw away script. Funny how things never seem to work out as 
expected, isn't it?
"""

import sys

MIN_PCT_COVERAGE_THRESHOLD = 5
MIN_TWEET_COVERAGE_THRESHOLD = 15


def main():
    """Attempts to load relevance information and parse evaluation file"""

    if len(sys.argv) < 2:
        print "You need to specify the path to the clusters file you want to evaluate."
        print "The file should have the same format as clusters.sortedby.clusterid.csv, however row order does not matter."
        print "example: python eval.py ../1day/clusters.sortedby.clusterid.csv"
        return

    eval_file = sys.argv[1]

    events = {}
    descriptions = {}
    category = {}
    cat_count = {}
    tweets_per_event = {}
    category_counts = {}
    total_items_count = 0

    rels_file = open('events.rel', 'r')
    for line in rels_file:
        event, tweet = line.strip().split(" ")
        events[tweet] = event

        if event not in tweets_per_event:
            tweets_per_event[event] = []
        tweets_per_event[event].append(tweet)

    desc_file = open('events.desc', 'r')
    for line in desc_file:
        event, desc = line.strip().split(" ", 1)
        descriptions[event] = desc[1:-1].strip()

    cat_file = open('events.category', 'r')
    for line in cat_file:
        event, cat = line.strip().split(" ", 1)
        category[event] = cat
        if cat not in cat_count:
            cat_count[cat] = 0
        cat_count[cat] = cat_count[cat] + 1

    table = []

    candidates = {}
    eval_file = open(eval_file, 'r')
    line = 0 
    for row in eval_file:
        line += 1
        parts = row.strip().split(",")
        if len(parts) < 2:
            print "Line", line, "malformed."
            print "Expected:\t[cluster_id],[named_entity],[tweet_id]" 
            print "Or:\t\t[cluster_id],[tweet_id]" 
            print "\nGot:\t\t", row
            return

        candidate = str(parts[0].strip())
        tweet = str(parts[1].strip())
        if len(parts) > 2:
            tweet = str(parts[2].strip())

        if candidate not in candidates:
            candidates[candidate] = set()
        candidates[candidate].add(tweet)

    valid_count = 0
    above_threshold = []
    found_above_threshold = []
    ret_cat_count = {}
    cat_ent_count = {}
    cat_event_count = {}
    relevant_tweets = []
    possible_tweets = []
    total_tweets = 0

    rel_found_event = {}

    print "CLUSTER_ID\tTWEET COVERAGE\tEVENT DESCRIPTION FROM CROWDSOURCED EVALUATION"
    for candidate in sorted(candidates):
        valid_count += 1
        # print candidate, ",",

        relevant = {}
        for tweet in candidates[candidate]:
            if tweet in events:
                if events[tweet] not in relevant:
                    relevant[events[tweet]] = 0
                    rel_found_event[events[tweet]] = []
                rel_found_event[events[tweet]].append(tweet)
                relevant[events[tweet]] += 1
                relevant_tweets.append(tweet)
        total_tweets += len(candidates[candidate])

    for candidate in sorted(candidates):
        relevant = {}
        rt = []
        for tweet in candidates[candidate]:
            if tweet in events:
                if events[tweet] not in relevant:
                    relevant[events[tweet]] = 0
                relevant[events[tweet]] += 1
                rt.append(tweet)

        if len(relevant) >= 0:
            # print "Event ID:", candidate, "\tContains", str(len(candidates[candidate]))

            passed = []
            tr = 0
            for e in relevant:
                e = str(e)

                if relevant[e] > 5 and (int(100.0 / len(candidates[candidate]) * relevant[e]) >= MIN_PCT_COVERAGE_THRESHOLD or relevant[e] >= MIN_TWEET_COVERAGE_THRESHOLD):
                    if category[e] not in ret_cat_count:
                        ret_cat_count[category[e]] = 0
                        cat_ent_count[category[e]] = []
                        cat_event_count[category[e]] = 0

                    possible_tweets += tweets_per_event[e]

                    if e not in found_above_threshold:
                        ret_cat_count[category[e]] = ret_cat_count[category[e]] + 1
                    cat_event_count[category[e]] += 1

                    above_threshold.append(candidate)
                    found_above_threshold.append(e)

                    if category[e] not in category_counts:
                        category_counts[category[e]] = 0
                    category_counts[category[e]] += 1
                    total_items_count += 1

                    print candidate, "\t\t", str(relevant[e]) + "/" + str(len(set(tweets_per_event[e]))) + " (" + str(int(100.0 / len(candidates[candidate]) * relevant[e])) + "%)\t", descriptions[e][:120]
                # else:
                    # print "\t\t", str(relevant[e]) + "/" + str(len(set(tweets_per_event[e]))) + "(" + str(int(100.0 / len(candidates[candidate]) * relevant[e])) + "%)\t", descriptions[e][:120]

                passed.append(e)
                tr += relevant[e]

            # print ""

    if valid_count > 0 and len(set(above_threshold)) > 0 and len(set(found_above_threshold)) > 0:
        event_recall = float(
            len(set(found_above_threshold))) / len(descriptions)
        event_precision = float(len(set(above_threshold))) / valid_count
        f_measure = 2 * ((event_precision * event_recall) / (event_precision + event_recall))

        print
        print "-------   EVENTS   -------\t"
        print
        print "EVENTS / CLUSTER STATISTICS:"
        print " - Of", len(descriptions), "events,", len(set(found_above_threshold)), "were detected."
        print " - Of", valid_count, "clusters,", len(set(above_threshold)), "could be matched back to an event."
        print ""
        print "Event Recall:\t\t%1.3f" % (event_recall)
        print "Cluster Precision:\t%1.3f" % (event_precision)
        print "Overall F-Measure:\t%1.3f" % (f_measure)

        print
        print
        print "----- CATEGORIES  -----"
        print
        print "%-30s    RECALL" % ("CATEGORY NAME")
        for cat in ret_cat_count:
            print "%-30s  %3d/%d\t(%1.3f)" % (cat, ret_cat_count[cat], cat_count[cat], ret_cat_count[cat] / float(cat_count[cat]))
        print ""

        print
    else:
        print "Didn't find any event clusters that could be matched to an event."


if __name__ == "__main__":
    main()
