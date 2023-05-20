import bisect
import os
import re
import sys

accents = {224: 'a', 226: 'a', 230: 'ae', 231: 'c', 232: 'e', 233: 'e', \
           234: 'e', 238: 'i', 239: 'i', 244: 'o', 339: 'oe', 249: 'u', \
           251: 'u', 252: 'u', 255: 'y', 95: ''}
forbidden = re.compile(r"[0-9%'+-_]")


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
        f.write("\n".join(sorted(words)))


def compare(file1, file2):
    corpus1 = set(line.strip() for line in open(os.path.join(os.getcwd(), file1), "r"))
    corpus2 = set(line.strip() for line in open(os.path.join(os.getcwd(), file2), "r"))
    overlap = corpus1.intersection(corpus2)
    print(len(overlap))

    new_filename = file1.split("_")[0] + "_n_" + file2.split("_")[0] + ".txt"
    with open(os.path.join(os.getcwd(), new_filename), "w+") as f:
        f.write("\n".join(corpus1.intersection(corpus2)))


def line_to_dict(filename):
    words = dict()
    with open(os.path.join(os.getcwd(), filename), "r", encoding="utf-8") as f:
        for line in f:
            word, _, tags = line.split("\t")
            word = word.translate(accents)
            if word in words:
                words[word].append(tags.rstrip())
            else:
                words[word] = [tags.rstrip()]
    return words


def compare_dicts(file1, file2):
    # Takes full words-with-metadata files
    corpus1 = line_to_dict(file1)
    corpus2 = line_to_dict(file2)
    overlap = corpus1.keys() & corpus2.keys()
    
    ## Returns all homonyms
    # output = ["\t".join([word, corpus1[word], corpus2[word]]) for word in overlap]
    ## Returns homonyms only if tags sufficiently different
    output = []
    for word in overlap:
        tags1 = [x[0] for x in corpus1[word]]
        tags2 = [x[0] for x in corpus2[word]]
        try:
            if not any (x == y for x in tags1 for y in tags2):
                output.append("\t".join([word, str(corpus1[word]), str(corpus2[word])]))
        except Exception as e:
            print(e)
    return "\n".join(["\t".join(["word", f"{file1} tags", f"{file2} tags"])] + sorted(output))


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


def search_corpus(target, corpus, output1, output2):
    # returns [new target], [output from other corpus], [output from this corpus]
    if target == False:
        return False, output1, output2
    elif len(target) == 0:
        return target, output1, output2
    length = len(target)
    # looking for a corpus word that is a substring of the target

    for i in range(length):
        # insert = bisect.bisect(corpus, target[:i+1]) # favors shorter words
        insert = bisect.bisect(corpus, target[:length - i]) # favors longer words
        test = corpus[insert - 1]
        # print(f"input {target[:i+1]}", f"test {test}")

        test_shorter = target.removeprefix(test)
        if test_shorter != target:
            # print(f"{test} was shorter than {target}.", f"remainder: {test_shorter}", f"output: {output}")
            return search_corpus(test_shorter, corpus, output1, output2 + "|" + test)
        
        # if no preceding word is found... the succeeding word is necessarily "longer"?
        try:
            test = corpus[insert]
            test_longer = test.removeprefix(target)
            if test_longer != test:
                # print(f"{test} was longer than {target}.", f"remainder: {test_longer}", f"output: {output + '|' + test_longer}")
                return test_longer, output1, output2 + "|" + test
        except Exception as e:
            return False, output1, output2
    # no matching words in corpus
    return False, output1, output2


def try_methodically(file1, file2):
    corpus1 = sorted(line.strip() for line in open(os.path.join(os.getcwd(), file1), "r"))
    corpus2 = sorted(line.strip() for line in open(os.path.join(os.getcwd(), file2), "r"))
    for x in corpus1:
        output1 = x[:]
        output2 = ""
        unmatched = x[:]
        # print(f"started with {output}")
        while len(unmatched) > 0:
            unmatched, output1, output2 = search_corpus(unmatched, corpus2, output1, output2)
            unmatched, output2, output1 = search_corpus(unmatched, corpus1, output2, output1)
            if unmatched == False:
                # print(f"Best try for {x}: {output1} / {output2}")
                break
        else:
            # remove leading | from second output
            # column 2: total chars, column 3: corpus 1 words, column 4: corpus 2 words
            print(f"Success: {x} gave {output1} / {output2[1:]}\t{len(output1.replace('|',''))}\t{output1.count('|')}\t{output2.count('|')-1}") 


if __name__ == "__main__":
    ## Cleaning
    # filename = sys.argv[1]
    # clean(filename)

    ## Matching orthography with metadata
    # file1, file2 = sys.argv[1:]
    # print(compare_dicts(file1, file2))

    ## Direct comparison
    # file1, file2 = sys.argv[1:]
    # compare(file1, file2)

    ## Bogo-style guessing
    # file1, file2 = sys.argv[1:]
    # try_random(file1, file2)

    ## Binary search
    file1, file2 = sys.argv[1:]
    try_methodically(file1, file2)
    # corpus1 = sorted(line.strip() for line in open(os.path.join(os.getcwd(), "wfl-en_clean.txt"), "r"))
    # search_corpus("tocarde", corpus1, "tocarde")
