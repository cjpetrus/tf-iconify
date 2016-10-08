import os
from nltk import metrics, stem, tokenize
from test import test_text
from fuzzywuzzy import process, fuzz

stemmer = stem.PorterStemmer()
import re
import sys
import operator
from operator import itemgetter
from pprint import pprint


def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def get_icons():
    fname = os.path.dirname(os.path.realpath(__file__)) + "/aws_icons.zip"
    if not os.path.isfile(fname):
        os.system(
            "wget -O aws_icons.zip https://media.amazonwebservices.com/AWS-Design/Arch-Center/16.2.22_Update/AWS_Simple_Icons_EPS-SVG_v16.2.22.zip")
    os.system("unzip -u aws_icons.zip -d ./aws_icons")
    temp = os.walk("./aws_icons", topdown=False)
    for root, dirs, files in temp:
        for i in dirs:
            dir = os.path.join(root, i)
            os.rename(dir, os.path.join(root, i.replace("&", "").replace(" ", "")))


def abs_icon_list(path="./aws_icons/.", rename=False):
    file_list = []
    for root, dirs, files in os.walk(os.path.abspath(path), topdown=False):
        for file in files:
            abs = os.path.join(root, file)
            if "__MAC" in abs:
                continue
            elif '.png' not in abs:
                continue
            else:
                file_list.append(abs)
    return file_list


def process_noise(data):
    processed_dict = {}
    for d in data:
        tmp = d.rsplit("/")[-1].split(".png")[0].lower().replace("amazon", "_").replace("-", "_").replace("__",
                                                                                                          "_").replace(
            "aws", "")
        processed_dict[d] = tmp
    return processed_dict


def get_tf_labels():
    scrubbed_tf_dict = dict()
    for s in TF_GRAPH_OUTPUT.split("\n"):
        if '[label' in s:
            alt_label = ''
            raw_label = s.split('"')[3]
            label = raw_label.split(".")[0].replace("aws_", '')
            og_repl = 'label = "{}"'.format(raw_label)
            if 'iam' in label:
                alt_label = label.replace("iam_", "security_identity_iam_")
            if 'route' in label:
                alt_label = label.replace('route_', 'networking_route_')
            if 'vpc' in label:
                alt_label = label.replace('vpc_', 'networking_vpc_')
            scrubbed_tf_dict[label] = {'repl': og_repl, 'alt_label': alt_label}

    return scrubbed_tf_dict


TF_GRAPH_OUTPUT = test_text
if __name__ == '__main__':

    scrubbed_icon_dict = process_noise(abs_icon_list('./aws_icons/.'))
    rev_scrubbed_icon_dict = dict((y, x) for x, y in scrubbed_icon_dict.iteritems())
    scrubbed_tf_dict = get_tf_labels()
    final_out = TF_GRAPH_OUTPUT
    #    pprint(scrubbed_tf_dict)
    scorers = [fuzz.partial_ratio, fuzz.token_set_ratio, fuzz.ratio, fuzz.partial_token_set_ratio]
    for label, v in scrubbed_tf_dict.iteritems():
        tmp_repl = None
        alt_label = v['alt_label']
        scores = list()
        for scorer in scorers:
            tmp = process.extract(label, scrubbed_icon_dict.values(), limit=1, scorer=scorer)[0]
            scores.append(tmp)
            if alt_label:
                tmp = process.extract(label, scrubbed_icon_dict.values(), limit=1, scorer=scorer)[0]
                scores.append(tmp)
        best_match = sorted(scores, key=lambda x: x[1], reverse=True)[0]
        if best_match < 70:
            continue
        icon_file = rev_scrubbed_icon_dict[best_match[0]]
        print final_out
        if icon_file:
            tmp_repl = """label = <<TABLE BORDER="0"><TR><TD><IMG SRC="{}"/></TD><TD>{}</TD></TR></TABLE>>""".format(
                icon_file, label)

            final_out = final_out.replace(v['repl'], tmp_repl)

    os.system("printf {} | dot -Tpng > graph2.png && open graph2.png".format(shellquote(final_out)))

# final[orig] = og_repl

# print test_text
#    for k,v in data.iteritems():
#       print k,v
