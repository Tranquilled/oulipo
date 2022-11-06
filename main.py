import bisect
import os
import re
import sys

accents = {224: 'a', 226: 'a', 230: 'ae', 231: 'c', 232: 'e', 233: 'e', \
           234: 'e', 238: 'i', 239: 'i', 244: 'o', 339: 'oe', 249: 'u', \
           251: 'u', 252: 'u', 255: 'y', 95: ''}
forbidden = re.compile(r"[0-9%'+-]")


def clean(filename):
    words = set()
    with open(os.path.join(os.getcwd(), filename), "r", encoding="utf-8") as f:
        for line in f:
            word = line.split("\t")[0].rstrip()
            # if any(x in word for x in ["%", "'", "-", "+", "."]) or word.isupper():
            if len(word) < 2 or word.isupper() or word.istitle() or forbidden.search(word):
                continue # need to add back "a" and "y"
            word = word.lower().translate(accents)
            words.add(word)
    new_filename = "".join(filename.split(".")[:-1]) + "_clean." + filename.split(".")[-1]
    print(len(words))
    with open(os.path.join(os.getcwd(), new_filename), "w+") as f:
        f.write("\n".join(words))


def compare(file1, file2):
    corpus1 = set(line.strip() for line in open(os.path.join(os.getcwd(), file1), "r"))
    corpus2 = set(line.strip() for line in open(os.path.join(os.getcwd(), file2), "r"))
    overlap = corpus1.intersection(corpus2)
    print(len(overlap))

    new_filename = file1.split("_")[0] + "_n_" + file2.split("_")[0] + ".txt"
    with open(os.path.join(os.getcwd(), new_filename), "w+") as f:
        f.write("\n".join(corpus1.intersection(corpus2)))


# def alphabetize(corpus):
    # Returns dict of lists:

def test_corpus(target, corpus, output):
    # returns [new target], [output]
    while len(output) < 40 and len(corpus) > 0:
        try:
            test = corpus.pop()
        except:
            print(f"corpus size is {len(corpus)}")
            return False, False
        test_shorter = target.removeprefix(test)
        if test_shorter != target:
            print(f"{test} was shorter than {target}.", f"remainder: {test_shorter}")
            return test_corpus(test_shorter, corpus, output)
        test_longer = test.removeprefix(target)
        if test_longer != test:
            print(f"{test} was longer than {target}.", f"remainder: {test_longer}")
            return test_longer, output + "|" + test_longer
    return target, output


def try_random(file1, file2):
    corpus1 = set(line.strip() for line in open(os.path.join(os.getcwd(), file1), "r"))
    corpus2 = set(line.strip() for line in open(os.path.join(os.getcwd(), file2), "r"))
    while True:
        output = corpus1.pop()
        unmatched = output[:]
        print(f"started with {output}")
        while len(unmatched) > 0:
            unmatched, output = test_corpus(unmatched, corpus2.copy(), output)
            if not output or len(output) > 40:
                print(f"nothing found for {output}")
                break
            # print(unmatched, output)
            unmatched, output = test_corpus(unmatched, corpus1.copy(), output)
            if not output or len(output) > 40:
                print(f"nothing found for {output}")
                break

        print("TERMINATED", output, unmatched)


def search_corpus(target, corpus, output):
    # returns [new target], [output]
    # print(output)
    if target == False:
        return False, output
    elif len(target) == 0:
        return target, output

    test = corpus[bisect.bisect(corpus, target) - 1]

    test_shorter = target.removeprefix(test)
    if test_shorter != target:
        print(f"{test} was shorter than {target}.", f"remainder: {test_shorter}", f"output: {output}")
        return search_corpus(test_shorter, corpus, output)

    test_longer = test.removeprefix(target)
    if test_longer != test:
        print(f"{test} was longer than {target}.", f"remainder: {test_longer}", f"output: {output}")
        return test_longer, output + "|" + test_longer
    # no matching words in corpus
    return False, output


def try_methodically(file1, file2):
    corpus1 = sorted(line.strip() for line in open(os.path.join(os.getcwd(), file1), "r"))
    corpus2 = sorted(line.strip() for line in open(os.path.join(os.getcwd(), file2), "r"))
    for x in corpus1:
        output = x[:]
        unmatched = x[:]
        print(f"started with {output}")
        while len(unmatched) > 0:
            unmatched, output = search_corpus(unmatched, corpus2, output)
            unmatched, output = search_corpus(unmatched, corpus1, output)
            if unmatched == False:
                print(f"Nothing found for {x}: {output}")
                break
        else:
            print(f"Success: {x} gave {output}")


if __name__ == "__main__":
    ## Cleaning
    # filename = sys.argv[1]
    # clean(filename)

    ## Direct comparison
    # file1, file2 = sys.argv[1:]
    # compare(file1, file2)

    ## Bogo-style guessing
    # file1, file2 = sys.argv[1:]
    # try_random(file1, file2)

    ## Binary search
    file1, file2 = sys.argv[1:]
    try_methodically(file1, file2)
