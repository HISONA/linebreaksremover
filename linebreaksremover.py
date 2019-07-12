import os
import sys
import hunspell


find_cnt1 = 0
find_cnt2 = 0
find_cnt3 = 0

posts = []
posts_len = 0

def korstems_init():

    global posts, posts_len

    words = []

    infile = open("./dic/JOSA.TXT", "rt", encoding="utf-8-sig")
    words += infile.readlines()
    infile.close()

    infile = open("./dic/EOMI.TXT", "rt", encoding="utf-8-sig")
    words += infile.readlines()
    infile.close()

    words = [x.strip('\n') for x in words]

    words = list(set(words))

    words.sort()
    words.sort(key=len, reverse=False)

    posts_len = 1

    st = 0
    ed = 0

    for word in words:
        if len(word) > posts_len:
            ed = words.index(word)
            posts_len += 1
            posts.append(words[st:ed-1])
            st = ed

    posts.append(words[st:])

def korstems_check(word):

    global posts, posts_len

    word_len = len(word)

    if word_len < 2:
        return 0

    if word_len > posts_len:
        word_len = posts_len
    else:
        word_len -= 1

    #print(word + " searching .... ")

    while word_len > 0:

        if word[-word_len:] in posts[word_len-1]:
            #print(str(word_len) + ", " + word[-word_len:] + " found.")
            return 1

        #print(str(word_len) + ", " + word[-word_len:] + " not found.")
        word_len -= 1

    return 0

def check_spacing_word(hobj, word1, word2):

    global find_cnt1, find_cnt2, find_cnt3
    global posts, posts_len

    word1_strip = word1.rstrip(".?!,ᆞ:/\"\'(){}[]<>-~_@$%&*+=")
    word2_strip = word2.rstrip(".?!,ᆞ:/\"\'(){}[]<>-~_@$%&*+=")

    word1_len = len(word1)
    word2_len = len(word2_strip)

    if word1_len > len(word1_strip):
        return 1

    if hobj.spell(word1 + word2_strip):
        #find_cnt1 += 1
        return 0
    elif hobj.spell(word1) and hobj.spell(word2_strip):
        #find_cnt1 += 1
        return 1
    elif word2_len > 1 and hobj.spell(word2_strip):
        ret = hobj.analyze(word2_strip)
        for value in ret:
            if value.decode('utf-8').find('fl:') > 0:
                find_cnt1 += 1
                return 1

    if not korstems_check(word2_strip) and korstems_check(word1 + word2_strip):
        find_cnt2 += 1
        return 0

    if korstems_check(word1):
        find_cnt3 += 1
        return 1

    return -1


if __name__ == '__main__':

    out_enable = False

    if len(sys.argv) < 2:
        print("\r\nInvalid parameter.")
        print("Usage: " + sys.argv[0] + " <inputfile> <ouputfile>\r\n")
        sys.exit(-1)
    else:

        filename = sys.argv[1]
        infile = open(filename, "rt", encoding='utf-8-sig')

        if len(sys.argv) > 2:
            filename = sys.argv[2]
            outfile = open(filename, "wt")
            out_enable = True

    line_end = True
    last_word = ""

    total_cnt = 0
    break_cnt = 0

    hobj = hunspell.HunSpell('./dic/ko.dic', './dic/ko.aff')

    korstems_init()

    while True:

        line = infile.readline()
        if not line:
            break

        s1 = line.strip('\n')
        s2 = s1.rstrip()

        if len(s1) > 0 and len(s2) > 0:

            if line_end and s1[0] != ' ':
                s1 = ' ' + s1
            elif len(last_word) > 0 and s1[0] != ' ':

                word = s1.split(' ')
                first_word = word[0]

                ret = check_spacing_word(hobj, last_word, first_word)

                if ret == 1:
                    s1 = ' ' + s1
                elif ret == -1:
                    break_cnt += 1
                    print("|" + last_word + "|" + first_word + "|")

            outfile.write(s1)

            c = s2[len(s2) - 1]

            if c == '.' or c == '\'' or c == '\"':
                line_end = True
                last_word = ""
                outfile.write("\n")
            else:
                line_end = False
                last_word = ""
                total_cnt += 1
                if s1[len(s1)-1] != ' ':
                    word = s1.split(' ')
                    last_word = word[len(word)-1]

        else:
            if line_end:
                outfile.write("\n")
            else:
                line_end = True
                last_word = ""
                outfile.write("\n\n")

    # while True:

    infile.close()

    if out_enable:
        outfile.close()

    print("total: " + str(total_cnt) + ", break: " + str(break_cnt))
    print("find1: " + str(find_cnt1))
    print("find2: " + str(find_cnt2))
    print("find3: " + str(find_cnt3))

